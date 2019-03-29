# encoding=utf-8
import json
import locale
import random
import sys
import tempfile
import time
import traceback
import urllib
import urllib2
import zlib  # for gzip decompression

import demjson
import tesserocr
from PIL import Image

from boxing.spider import SpiderConfig


class Decoder(object):

    def __init__(self):
        pass

    def threshold_filter_img(self, img, threshold=140):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
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

    def calculate(self, expression):
        tokens = expression.split('+')
        op = '+'
        if (len(tokens) == 1):   # not plus operator
            tokens = expression.split('-')
            if (len(tokens) == 1):  # neither plus nor minus, bad recoginization
                return -1
            op = '-'

        if len(tokens) != 2:
            return -1  # unknown condition

        left = tokens[0].encode('ascii').strip()
        right = tokens[1].encode('ascii').strip()

        left = int(left)
        right = int(right)

        if op == '+':
            return left + right
        else:
            return left - right

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


class AutoLoginTool(object):
    """隆众网自动登录"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.decoder = Decoder()

    def gen_logined_cookie(self, data, set_cookie):
        cookie_items = set_cookie.split(';')
        cookie_dict = {}
        for item in cookie_items:
            idx = item.find(',')
            if (idx > 0):
                item = item.split(',')[1]
            pair = item.split('=')
            valueset = (pair[0].strip(), pair[1].strip())
            cookie_dict[valueset[0]] = valueset[1]

        cookie = 'parentid=0; userid=' + str(data['userNo']) + '; '
        cookie += ('password=' + cookie_dict['password'] + '; ')
        cookie += ('AccessToken=' + cookie_dict['AccessToken'] + ';')
        cookie += ('username=' + cookie_dict['username'] + ';')
        cookie += ('sidid=' + cookie_dict['sidid'] + ';')
        cookie += ('userNo=' + str(data['userNo']) + ';')
        cookie += ('LZ_' + str(data['userNo']) + '_UN=' + urllib.quote('安信证券股份有限公司') + '(axzq1010);')
        cookie += ('lz_usermember=' + urllib.quote(data['userMember']) + ';')
        cookie += 'lz_usermember=0%2C2; auto=0; refcheck=ok; refpay=0; refsite=http%3A%2F%2Fnews.oilchem.net%2Flogin.shtml; '
        cookie += 'Hm_lvt_47f485baba18aaaa71d17def87b5f7ec=1546486194; Hm_lpvt_47f485baba18aaaa71d17def87b5f7ec=1546486194'

        return cookie

    def try_login(self, login_url, code_value, set_cookie):
        form = dict()

        form['username'] = self.username
        form['password'] = self.password
        form['code'] = str(code_value)
        form['rp'] = ''

        encoded_form_data = urllib.urlencode(form)

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36',
            'Origin': 'http://news.oilchem.net',
            'Referer': 'http://news.oilchem.net/login.shtml',
            'Content-Length': len(encoded_form_data),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'cookie': set_cookie,
            'X-Requested-With': 'XMLHttpRequest'
        }

        req = urllib2.Request(login_url, headers=headers, data=encoded_form_data)

        response = urllib2.urlopen(req)
        data = response.read()
        message = demjson.decode(data)

        print '$' * 100
        print message.get('message') or message
        print '$' * 100
        if (message['data'] == None or message['data'] == '' or message['data']['login'] != '1'):
            raise Exception('failed to login.')

        set_cookie = response.headers['Set-Cookie']
        logined_cookie = self.gen_logined_cookie(message['data'], set_cookie)

        return logined_cookie

    def _get_ver_code_value(self, cookie):
        verf_code_url = 'http://news.oilchem.net/getcode/api/?' + str(random.random()) + str(random.random())[2:6]  # 18 digits random number

        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())

        req = urllib2.Request(verf_code_url)
        req.add_header('cookie', cookie)
        response = urllib2.urlopen(req)
        imgData = response.read()

        img_file = tempfile.NamedTemporaryFile(suffix='_oc_verf', dir=SpiderConfig().get_temp_dir(), delete=True)
        img_file.write(imgData)

        code_value = self.decoder.decode_img(img_file)
        return code_value

    def try_get_verf_code_value(self, cookie, retry_times=5):
        while (retry_times > 0):
            retry_times = retry_times - 1
            codeValue = self._get_ver_code_value(cookie)
            if (codeValue is not None and codeValue > 1000 and codeValue < 10000):
                return codeValue

        return None

    def submit_login_form(self, cookie):
        login_url = "http://news.oilchem.net/user/userLogin.do?ajax=1&chkbdwx=0&closewindow=&rnd=" + str(random.random()) + str(random.random())[2:6] + '&b=c6cd86f957430ab076158365dac8a2d4'

        max_retries = 1
        while (max_retries > 0):
            max_retries = max_retries - 1
            code_value = self.try_get_verf_code_value(cookie)
            if code_value is None:
                raise Exception('failed to parse verf code')

            try:
                logined_cookie = self.try_login(login_url, code_value, cookie)
                return logined_cookie
            except:
                print traceback.format_exc()
                pass

        raise Exception('failed to login')

class UrlCrawlerConfig:
    def __init__(self, price_id, product_id, start_time, end_time, specification):
        self.price_id = price_id
        self.product_id = product_id
        self.start_time = start_time
        if end_time == 'today':
            today = time.strftime("%Y-%m-%d", time.localtime())
            self.end_time = today
        else:
            self.end_time = end_time
        self.specification = specification

class UrlCrawler(object):

    def __init__(self, config):
        self.config = config

    def _get_headers(self, cookie):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36',
            'cookie': cookie
        }

        return headers

    def _get_post_body(self, page, page_size):
        body = {
            'id' : self.config.price_id,
            'startTime' : self.config.start_time,
            'endTime' : self.config.end_time,
            'timeType' : 0,
            'pageNum' : page,
            'pageSize' : page_size,
        }
        return urllib.urlencode(body)

    def _req_data(self, req_url, headers, page_size, page_idx):
        if (page_idx < 1 or page_idx > page_size):
            raise "Incorrect page number " + str(page_idx)

        body = self._get_post_body(page_idx, page_size)
        req = urllib2.Request(req_url, headers=headers, data=body)
        response = urllib2.urlopen(req)

        return demjson.decode(response.read())  # the data is in raw javascript format, not json, convert it to json (python object).

    def download_data(self, req_url, cookie):
        page_idx = 1
        page_size = 300
        headers = self._get_headers(cookie)
        data = self._req_data(req_url, headers, page_size, page_idx)  # get the first page of data
        
        num_pages = data['pages']
        
        records = self._extract_items_in_page(data)     #first page
        for i in range(1, num_pages):
            data = self._req_data(req_url, headers, page_size, i)
            records = records + self._extract_items_in_page(data)
    
        print 'finished downloading data for: ' + req_url
        
        return records

    def _extract_items_in_page(self, jsonData):
        rows = jsonData['pageInfo']['list']

        records = []
        for item in rows:
            pubDate = item['indexDate']
            productName = item['varietiesName']
            spec = item['specificationsName']
            standard = item['standard']
            region = item['regionName']
            market = item['internalMarketName']
            company = item['memberAbbreviation']
            priceLow = item['lprice']
            priceHigh = item['gprice']
            priceMarket = item['indexValue']
            unit = item['unitValuationName']
            increaseAmount = item['riseOrFallSum']
            increaseRate = item['riseOrFallRate']
            remarks = item['remark']

            record = {
                'product_name' : productName,
                'date' : pubDate,
                'model' : spec,
                'region' : region,
                'market' : market,
                'company' : company,
                'price_low' : priceLow,
                'price_high' : priceHigh,
                'price_market' : priceMarket,
                'unit' : unit,
                'change' : increaseAmount,
                'delta_rate' : increaseRate,
                'remarks' : remarks 
            }

            records.append(record)

        return records
