# -*- coding: utf-8 -*-
import scrapy
import time
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class SeleniumLogin:

	LOGIN_XPATH_SELECTOR = {
		'PLAS_LOGIN' : {
			'login_frame' : '//*[@id="Panel_Login"]/iframe',
			'user_name' : '//*[@id="chemname"]',
			'password' : '//*[@id="chempwd"]',
			'submit_button' : '//*[@id="frm_login"]//*[@class="login_l_block"]//ul/li[3]//input'
		},
		'CHEM_LOGIN' : {
			'login_frame' : '//*[@id="Panel_Login"]/iframe',
			'user_name' : '//*[@id="chemname"]',
			'password' : '//*[@id="chempwd"]',
			'submit_button' : '//*[@id="frm_login"]//*[@id="ImageButton1"]'
		} 
	}

	LOGIN_URL = {
		'PLAS_LOGIN' : 'http://plas.chem99.com/news/30420259.html',
		'CHEM_LOGIN' : 'http://chem.chem99.com/news/30417130.html'
	}

	def set_account(self, accountName, password):
		self.userName = accountName
		self.userPassword = password

	def __init__(self, configPath, login_type='PLAS_LOGIN'):
		self.isCookieValid = False

		self.login_page_url = self.LOGIN_URL.get(login_type)
		self.configPath = configPath
		self.configFileName = login_type.lower() + '_cookies.dat'
		self.selector = self.LOGIN_XPATH_SELECTOR.get(login_type)

		if self.selector is None:
			raise Exception('Can not recognize the login type, please confirm!')
		else:
			print '############# LOGIN TYPE: %s #############' % login_type

		if not self.isConfigExists():
			self.COOKIE_MAX_DURATION = 3600 	# in second
		else:
			self.readCookies()
		
	def selelogin(self):
		if self.isCookieValid:
			return self.cookieStr

		#if the cookie in config file is no more valid, then relogin
		options = Options()
		#options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		browser = webdriver.Chrome(chrome_options=options)
		# browser = webdriver.PhantomJS()
		# browser = webdriver.Firefox()
		
		browser.implicitly_wait(5)  # wait until the page is fully loaded.

		browser.get(self.login_page_url)

		loginFrame = browser.find_element_by_xpath(self.selector['login_frame'])
		browser.switch_to.frame(loginFrame)

		userNameInput = browser.find_element_by_xpath(self.selector['user_name'])
		userNameInput.click()
		userNameInput.send_keys(self.userName)

		userPasswdInput = browser.find_element_by_xpath(self.selector['password'])
		userPasswdInput.click()
		userPasswdInput.send_keys(self.userPassword)

		submitBtn = browser.find_element_by_xpath(self.selector['submit_button'])

		submitBtn.click()
		time.sleep(3)

		cookie_items = browser.get_cookies()
		loginedCookie = self.cookieToStr(cookie_items)
		# print (loginedCookie)
		browser.close()

		self.storeCookies(loginedCookie)
		return loginedCookie

	def cookieToStr(self, cookie_items):
		cookie_str = ''
		for cookie_item in cookie_items:
			cookie_str += ( cookie_item['name'] + '=' + cookie_item['value'] + ';' )

		return cookie_str;

	def storeCookies(self, cookieStr):
		with open(self.configPath + self.configFileName, 'w+') as configFile:
			configFile.write( str(self.COOKIE_MAX_DURATION) + '\n' )
			configFile.write( str(int(time.time())) + '\n' )
			configFile.write(cookieStr)

	def readCookies(self):
		with open(self.configPath + self.configFileName, 'r') as configFile:
			self.COOKIE_MAX_DURATION = int(configFile.readline())
			createdTime = int(configFile.readline())

			self.cookieStr = configFile.readline()
			
			currentTime = int(time.time())
		
			if (currentTime - createdTime < self.COOKIE_MAX_DURATION):
				self.isCookieValid = True
				print '---------- Reading config...  ----------'
				print 'Max cookie duration(s): ' + str(self.COOKIE_MAX_DURATION)
				print createdTime
				print self.cookieStr
				print '----------------------------------------'
			else:
				self.isCookieValid = False

	def isConfigExists(self):
		if os.path.exists(os.path.join(self.configPath,self.configFileName)):
			return True
		return False






if __name__ == '__main__':
	loginMachine = SeleniumLogin(os.getcwd() + '/')
	loginMachine.setAccount('founder123', '123Qweasd')
	loginMachine.selelogin('http://plas.chem99.com/news/30375838.html')