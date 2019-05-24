# -*- coding: utf-8 -*-
import time
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class MyLogin:

	@staticmethod
	def login(login_url, username, password):
		if os.path.exists(os.path.join(os.getcwd(), 'DEV_FLAG')):	#runs in dev mode.
			options = Options()
			# options.add_argument('--headless')
			options.add_argument('--no-sandbox')
			browser = webdriver.Chrome(chrome_options=options)
			# browser = webdriver.Firefox()
		else:
			# browser = webdriver.PhantomJS()		#phantomjs mode failed login, and headless mode
			options = Options()
			# options.add_argument('--headless')
			options.add_argument('--no-sandbox')
			browser = webdriver.Chrome(chrome_options=options)

		browser.implicitly_wait(5)  # wait until the page is fully loaded.

		browser.get(login_url)

		username_input = browser.find_element_by_css_selector('#app > div > div > div.login-content > div.login-content-form > form > div:nth-child(1) > div > div.el-input > input')
		username_input.click()
		username_input.send_keys(username)

		password_input = browser.find_element_by_css_selector('#app > div > div > div.login-content > div.login-content-form > form > div:nth-child(2) > div > div.el-input > input')
		password_input.click()
		password_input.send_keys(password)

		submit = browser.find_element_by_css_selector('#app > div > div > div.login-content > div.login-content-form > form > div:nth-child(3) > div > button')
		submit.click()

		time.sleep(3)
		cookie_items = browser.get_cookies()
		loginedCookie = MyLogin.cookieToStr(cookie_items)
		# print (loginedCookie)
		browser.close()

		return loginedCookie

	@staticmethod
	def cookieToStr( cookie_items):
		cookie_str = ''
		for cookie_item in cookie_items:
			cookie_str += ( cookie_item['name'] + '=' + cookie_item['value'] + ';' )

		return cookie_str;


if __name__ == '__main__':

	cookie_str = MyLogin.login('http://localhost:9875/login', 'root', '11111111')
	print cookie_str
