# encoding=utf-8

import random
import sys,os
import tempfile
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from decode import Decoder      #Not used now


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
        timestamp_millisecond = str(int(time.time()*1000))
        verf_code_url = 'https://passport.oilchem.net/member/login/getImgCode?timestamp=' + timestamp_millisecond

        req = urllib2.Request(verf_code_url)
        req.add_header('cookie', cookie)
        response = urllib2.urlopen(req)
        imgData = response.read()

        # img_file = '/home/ren/work/git_repos/pe_scrapy/pe/pe/work/oilchem/' + timestamp_millisecond + '.jpg'
        img_file = tempfile.NamedTemporaryFile(suffix='_oc_verf', dir=SpiderConfig().get_temp_dir(), delete=True)
        img_file.write(imgData)
        # codeImgFile = open(img_file, 'wb')
        # codeImgFile.write(imgData)  
        # codeImgFile.close()

        code_value = self.decoder.read_img(img_file)
        return code_value

    def try_get_verf_code_value(self, cookie, retry_times=5):
        while (retry_times > 0):
            retry_times = retry_times - 1
            code_value = self._get_ver_code_value(cookie)
            if len(code_value) == 4:
                return code_value
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

#login by selenium operations, extends AutoLogin
class SeleniumLogin(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def selelogin(self):
        target_url = 'https://dc.oilchem.net/priceInternational/detail.htm?id=3963&timeType=0&flag=1'
        if os.path.exists(os.path.join(os.getcwd(), 'DEV_FLAG')):   #runs in dev mode.
            options = Options()
            #options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            browser = webdriver.Chrome(chrome_options=options)
            # browser = webdriver.Firefox()

            if os.path.exists(os.path.join(os.getcwd(), 'dev_cookie_tmp.dat')):
                with open(os.path.join(os.getcwd(), 'dev_cookie_tmp.dat'), 'r') as cookie_file:
                    logined_cookie = cookie_file.read()
                    return logined_cookie
        else:
            browser = webdriver.PhantomJS()
        # browser = webdriver.PhantomJS()
        browser.implicitly_wait(5)  # wait until the page is fully loaded.

        count_tried = 0
        while (count_tried < 3):
            count_tried += 1

            browser.get(target_url)

            login_window_button = browser.find_element_by_css_selector('#header_menu_top_login a:nth-child(1)')
            login_window_button.click()

            username_box = browser.find_element_by_id('dialogUsername')  
            username_box.click()
            username_box.send_keys(self.username)

            passwrd_box = browser.find_element_by_id('dialogPassword')
            passwrd_box.click()
            passwrd_box.send_keys(self.password)

            cookie_items = browser.get_cookies()
            cookie = self._cookie_to_str(cookie_items)
            
            # code_value = self.try_get_verf_code_value(cookie)
            code_value = self._read_code_from_cookie(cookie)
            if code_value is None:
                raise Exception('Code value not found exception.') # this will quit the program

            verification_code_box = browser.find_element_by_id('dialogImgCodeStr')
            verification_code_box.click()
            verification_code_box.send_keys(code_value)

            submit_button = browser.find_element_by_css_selector('#dialogForm .form-sub button')
            submit_button.click()

            #get the data page for updating cookie
            try:
                browser.get('https://dc.oilchem.net/priceDomestic/detail.htm?id=6229&timeType=0&flag=1')
                time.sleep(3)
                cookie_items = browser.get_cookies()
                if not self._test_login_OK(cookie_items):
                    continue
                logined_cookie = self._cookie_to_str(cookie_items)
                print '$' * 80
                print (logined_cookie)
                print '$' * 80
                browser.close()

                with open(os.path.join(os.getcwd(), 'dev_cookie_tmp.dat'), 'w+') as cookie_file:
                    cookie_file.write(logined_cookie)
                return logined_cookie
            except:
                print traceback.format_exc()
                dig_alert = browser.switch_to.alert
                dig_alert.accept()

        browser.close()
        print('Login failed more than 3 times, sorry we have to quit program.')
        raise Exception('Program quit exception.')

    def _test_login_OK(self, cookie_items):
        for cookie_item in cookie_items:
            if cookie_item['name'] == '_member_user_tonken_':
                # print '=========>' + cookie_item['value']
                if len(cookie_item['value']) > 2:
                    return True
        return False

    def _cookie_to_str(self, cookie_items):
        cookie_str = ''
        for cookie_item in cookie_items:
            cookie_str += ( cookie_item['name'] + '=' + cookie_item['value'] + ';' )

        return cookie_str;

    def _read_code_from_cookie(self, cookie):
        p1 = cookie.find('_imgCode')
        pCodeBeg = p1 + len('_imgCode=')
        pCodeEnd = pCodeBeg + 4
        return cookie[pCodeBeg : pCodeEnd]
