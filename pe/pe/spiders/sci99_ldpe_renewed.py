# -*- coding: utf-8 -*-
import time
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from boxing.spider import SpiderBase

# from user_items import Chem99PvcOpRateWeek

class Sci99LdpeRenewed(SpiderBase):
	name = 'sci99_ldpe'

	#Account info
	config = {
		'username' : 'founder123',
		'password' : '123Qweasd'
	}

	DATA_URL = r'http://price.sci99.com/view/PriceView.aspx?pagename=plasticView&classid=571&pricetypeid=24&linkname=LDPE%u518d%u751f%u6599'
	start_urls = [DATA_URL]

	SCI_LOGIN = {
			'user_name' : '//*[@id="LogInPart1_SciName"]',
			'password' : '//*[@id="LogInPart1_SciPwd"]',
			'submit_button' : '//*[@id="LogInPart1_IB_Login"]'
		}

	DOWNLOAD_PATH = '/home/ren/work/git_repos/pe_scrapy/pe/result'
	DOWNLOAD_FILE_TMP_NAME = 'historydata.xls'
	HEADLESS_MODE = False

	def parse(self, response):
		print '====================> parse sci99_ldpe'
		print response.url

		options = Options()
		options = webdriver.ChromeOptions()
		# options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		options.add_argument("--start-maximized")
		prefs = {'download.default_directory' : '/home/ren/work/git_repos/pe_scrapy/pe/result'}
		options.add_experimental_option('prefs', prefs)
		# options.add_argument("download.default_directory=/home/ren/work/git_repos/pe_scrapy/pe")
		browser = webdriver.Chrome(chrome_options=options)
		# browser = webdriver.PhantomJS()
		# browser = webdriver.Firefox()
		
		browser.implicitly_wait(5)  # wait until the page is fully loaded.

		browser.get(self.DATA_URL)
		# browser.maximize_window()
		handle_main = browser.current_window_handle

		user_name_input = browser.find_element_by_xpath(self.SCI_LOGIN['user_name'])
		user_name_input.click()
		user_name_input.send_keys(self.config['username'])

		user_password_input = browser.find_element_by_xpath(self.SCI_LOGIN['password'])
		user_password_input.click()
		user_password_input.send_keys(self.config['password'])

		submit_button = browser.find_element_by_xpath(self.SCI_LOGIN['submit_button'])

		submit_button.click()
		# time.sleep(3)

		# browser.refresh()
		# time.sleep(3)
		lookup_button = browser.find_element_by_xpath('//*[@id="btnSearch"]')
		lookup_button.click()

		# time.sleep(3)

		show_detail_lookup = browser.find_element_by_xpath('//*[@id="20534"]/td[11]')
		show_detail_lookup.click()

		time.sleep(3)

		handles = browser.window_handles

		for handle in handles:
			if handle != handle_main:
				handle_history = handle

		if handle_history:
			print "Switching..."
			browser.switch_to_window(handle_history)

		self.enable_download_in_headless_chrome(browser, '/home/ren/work/git_repos/pe_scrapy/pe/result')
		print 'Downloading...'
		time.sleep(3)
		download_button = browser.find_element_by_xpath('//*[@id="Button2"]')
		download_button.click()
		# ret = browser.execute_script('alert(window.option)')

		browser.close()	#just close a tab
		
		browser.switch_to_window(handle_main)
		# print ret
		# print (loginedCookie)

		time.sleep(5)
		browser.close()

	def download_data(self):
		pass

	def open_browser(self):
		pass


	#download function is closed when open headless mode, this cammand will enable the download in the current tab
	def enable_download_in_headless_chrome(self, driver, download_dir):
	    # add missing support for chrome "send_command"  to selenium webdriver
	    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

	    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
	    command_result = driver.execute("send_command", params)
	    # print("response from browser:")
	    # for key in command_result:
	    #     print("result:" + key + ":" + str(command_result[key]))

	def move_and_rename_file(self, dest_path, newname):
		files = os.listdir(self.DOWNLOAD_PATH)
		find_flag = False
		for f in files:
			if f == self.DOWNLOAD_FILE_TMP_NAME:
				find_flag = True
				oldname = os.path.join(self.DOWNLOAD_PATH, f)
				newname = os.path.join(dest_path, newname)
				print 'Moving %s to %s' % (oldname, newname)
				os.rename(oldname, newname)
				print 'OK.'

		if not find_flag:
			print 'Can not find the file %s, no operation applied.' % self.DOWNLOAD_FILE_TMP_NAME
