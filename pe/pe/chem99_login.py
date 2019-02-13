# -*- coding: utf-8 -*-
import scrapy
import time
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys

class SeleniumLogin:

	configFileName = 'login_config.dat'

	def set_account(self, accountName, password):
		self.userName = accountName
		self.userPassword = password

	def __init__(self, configPath):
		self.isCookieValid = False

		self.configPath = configPath

		if not self.isConfigExists():
			self.Cookie_Max_Duration = 172800 	# in seconds, equals to 48 hours
		else:
			self.readCookies()
		

	def selelogin(self, url):
		if self.isCookieValid:
			return self.cookieStr

		#if the cookie in config file is no more valid, then relogin
		browser = webdriver.Chrome()
		# browser = webdriver.PhantomJS()
		browser.implicitly_wait(5)  # wait until the page is fully loaded.

		browser.get(url)

		loginFrame = browser.find_element_by_xpath('//*[@id="Panel_Login"]/iframe')
		browser.switch_to.frame(loginFrame)

		userNameInput = browser.find_element_by_xpath('//*[@id="chemname"]')
		userNameInput.click()
		userNameInput.send_keys(self.userName)

		userPasswdInput = browser.find_element_by_xpath('//*[@id="chempwd"]')
		userPasswdInput.click()
		userPasswdInput.send_keys(self.userPassword)

		submitBtn = browser.find_element_by_xpath('//*[@id="frm_login"]//*[@class="login_l_block"]//ul/li[3]//input')

		# print submitBtn.get_attribute('innerHTML')
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
			configFile.write( str(self.Cookie_Max_Duration) + '\n' )
			configFile.write( str(int(time.time())) + '\n' )
			configFile.write(cookieStr)

	def readCookies(self):
		with open(self.configPath + self.configFileName, 'r') as configFile:
			self.Cookie_Max_Duration = int(configFile.readline())
			createdTime = int(configFile.readline())

			self.cookieStr = configFile.readline()

			print '---------- Reading config...  ----------'
			print 'Max cookie duration(s): ' + str(self.Cookie_Max_Duration)
			print createdTime
			print self.cookieStr
			print '----------------------------------------'
			
			currentTime = int(time.time())
		
			if (currentTime - createdTime < self.Cookie_Max_Duration):
				self.isCookieValid = True
			else:
				self.isCookieValid = False

	def isConfigExists(self):
		if os.path.exists(self.configPath + self.configFileName):
			return True
		return False




if __name__ == '__main__':
	loginMachine = SeleniumLogin(os.getcwd() + '/')
	loginMachine.setAccount('founder123', '123Qweasd')
	loginMachine.selelogin('http://plas.chem99.com/news/30375838.html')
