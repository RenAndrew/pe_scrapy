# -*- coding: utf-8 -*-
import os
import json
import tesserocr
from PIL import Image

class Decoder(object):
    #Only this method is called outside
    def read_img(self, img_file):
        im = Image.open(img_file)
        code_value = self.parse_the_code(im)
        im.close()
        return code_value

    def parse_the_code(self, img):
        img = self.filter_color(img)
        img = self.de_dots(img)

        size = img.size
        multi_size = 8
        size = (size[0]*multi_size, size[1]*multi_size)
        img = img.resize(size, Image.ANTIALIAS)

        img = img.crop( (size[0]*0.18, size[1]*0.14, size[0]*0.9, size[1]*0.85) )
        img = self.threshold_filter_img(img,190)

        raw_code = tesserocr.image_to_text(img)
        code_value = self.refine(raw_code)
        return code_value


    def filter_color(self, img):
        img_rgba = img.convert('RGBA')
        pixdata = img_rgba.load()
        max_color_product = 0

        for y in range(img_rgba.size[1]):
            for x in range(img_rgba.size[0]):
                color_product = pixdata[x,y][0] * pixdata[x,y][1] * pixdata[x,y][2]
                # if color_product < 2000:
                #     color_product = color_product*color_product*color_product
                #     if color_product < 17000000:
                #         pixdata[x,y] = (255, 255, 255, 0)
                if color_product < 260:
                    pixdata[x,y] = (255, 255, 255, 0)

        return img_rgba.convert('L')

    def refine(self, exp):
        refined_exp = ''

        for ch in exp:
            if ch == 'l':
                refined_exp = refined_exp + '1' #No L in lowercase, it must be 1
            elif ch.isalnum():
                refined_exp = refined_exp + ch

        return refined_exp.upper()

    def threshold_filter_img(self, img, threshold=140):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        img = img.point(table, '1')  # 所有低于门限值的全部为0
        return img

    #8领域算法去噪
    def de_dots(self, img):
        pixdata = img.load()
        w,h = img.size
        for y in range(1,h-1):
            for x in range(1,w-1):
                count = 0    #Count white
                if pixdata[x,y-1] > 245:#上
                    count = count + 1
                if pixdata[x,y+1] > 245:#下
                    count = count + 1
                if pixdata[x-1,y] > 245:#左
                    count = count + 1
                if pixdata[x+1,y] > 245:#右
                    count = count + 1
                if pixdata[x-1,y-1] > 245:#左上
                    count = count + 1
                if pixdata[x-1,y+1] > 245:#左下
                    count = count + 1
                if pixdata[x+1,y-1] > 245:#右上
                    count = count + 1
                if pixdata[x+1,y+1] > 245:#右下
                    count = count + 1
                    if count > 6:
                       pixdata[x,y] = 255
        return img