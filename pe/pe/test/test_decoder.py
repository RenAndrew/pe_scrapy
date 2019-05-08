# -*- coding: utf-8 -*-
import os
import tesserocr
from PIL import Image

class Decoder(object):

    def __init__(self):
        pass

    def threshold_filter_img(self, img, threshold=140):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(1)
            else:
                table.append(0)
        img = img.point(table, '1')  # 所有低于门限值的全部为0
        return img

    def transform_img(self, img):
        size = img.size
        img = img.resize((size[0]*5, size[1]*5), Image.ANTIALIAS)  # 放大5倍

        size = img.size
        cutSizeX = int(size[0] * 0.87)  # magic number here
        cutSizeY = int(size[1] * 0.8)
        img = img.crop((0, 0, cutSizeX, cutSizeY))

        img = img.convert('L')  # 转为灰度图片（黑白）

        # 还可以进行二值化门限处理降低背景噪音增加精度 self.thresholdFilterImg
        return img

    def decode_img(self, img_file):
        im = Image.open(img_file)
        reenforced_im = self.transform_img(im)

        expression = tesserocr.image_to_text(reenforced_im)

        code_value = None
        try:
            code_value = self.calculate(expression)
        except:
            pass

        return code_value

    def read_img(self, img_file):
        im = Image.open(img_file)
        reenforced_im = self.transform_img(im)

        expression = tesserocr.image_to_text(reenforced_im)

        return expression

if __name__ == '__main__':
	codeImgFilePath = '/home/ren/work/git_repos/pe_scrapy/pe/pe/work/oilchem/'

	img_list = os.listdir(codeImgFilePath)

	for i in range(0, len(img_list)):
		file_path = os.path.join(codeImgFilePath, img_list[i])
		print file_path

		if not os.path.isfile(file_path):
			continue

		im = Image.open(file_path)
		size = im.size
		size = (size[0]*6, size[1]*6)
		im = im.resize(size, Image.ANTIALIAS)

		im = im.crop( (size[0]*0.18, size[1]*0.15, size[0]*0.9, size[1]*0.85) )
		im = im.convert('L')
		im = Decoder().threshold_filter_img(im, 180)
		im.save(os.path.join(codeImgFilePath + 'tmp/', img_list[i]))
		
		# im.show()
		expression = tesserocr.image_to_text(im)
		print expression.strip()
		print ''
		# break