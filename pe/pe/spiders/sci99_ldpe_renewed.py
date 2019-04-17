# -*- coding: utf-8 -*-
import time
import os
from datetime import date

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from boxing.spider import SpiderBase,SpiderConfig

from user_items import Sci99Ldpe

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

	DOWNLOAD_TMP_PATH = '/home/ren/work/git_repos/pe_scrapy/pe/result/'
	DOWNLOAD_FILE_TMP_NAME = 'historydata.xls'
	DOWNLOAD_PATH = '/home/ren/work/git_repos/pe_scrapy/pe/result/sci99_ldpe'

	WORK_PATH = './pe/work/sci99/'
	
	HEADLESS_MODE = False		#headless mode does not work, dont know why

	def parse(self, response):
		print '====================> parse sci99_ldpe'
		print response.url

		self.download_data()

	def __init__(self):
		super(Sci99LdpeRenewed, self).__init__()
		if os.path.exists(os.path.join(os.getcwd(), 'DEV_FLAG')):
			print 'Current spider runs in dev mode.'
			print os.getcwd()
		else:
			#read the configs
			self.crawl_config = SpiderConfig().get_config('sci99')
			self.config['username'] = self.crawl_config['username']
			self.config['password'] = self.crawl_config['password']
			self.WORK_PATH = self.crawl_config['work_path']
			self.DOWNLOAD_TMP_PATH = os.path.join(self.WORK_PATH, 'tmp')
			self.DOWNLOAD_PATH = os.path.join(self.crawl_config['result_path'], self.name)

		if not os.path.exists(self.WORK_PATH):
			os.makedirs(self.WORK_PATH)
		if not os.path.exists(self.DOWNLOAD_TMP_PATH):
			os.makedirs(self.DOWNLOAD_TMP_PATH)
		

		print 'Work path is: ' + self.WORK_PATH



	def download_data(self):
		browser = self.open_browser()
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

		lookup_button = browser.find_element_by_xpath('//*[@id="btnSearch"]')
		lookup_button.click()	#click the lookup button to show the price list of ldpe

		#########################################################################################
		#In the price list, click "查看" of each product to see the history price data page.
		rows = browser.find_elements_by_css_selector('#divContents table:nth-child(2) tr')

		tr_css_sel_templ = '#divContents table:nth-child(2) tr:nth-child(%s)'
		area = ''
		for row_idx in range(1, len(rows)):
			print '-' * 100
			# print tr_css_sel_templ % row_idx
			rid = browser.find_element_by_css_selector(tr_css_sel_templ % row_idx).get_attribute("id")  #row id
			print str(row_idx) + ' : ' + str(rid)
			
			if rid is not None and rid != '':
				td_css_sel = (tr_css_sel_templ % row_idx) + ' td:nth-child(%d)'
				regoin = browser.find_element_by_css_selector(td_css_sel % 1).text
				spec = browser.find_element_by_css_selector(td_css_sel % 2).text	#规格
				print area + ', ' + regoin + ', ' + spec
				file_name = area + '_' + regoin + '_' + spec + '_' + str(date.today()) + '.xls'
				
				retry_count = 0
				while (retry_count < 5):
					retry_count += 1
					show_detail_lookup = browser.find_element_by_css_selector(td_css_sel % 11)
					show_detail_lookup.click()		#click to open new page

					time.sleep(3)	#wait the new tab
					handles = browser.window_handles
					handle_history = None
					for handle in handles:
						if handle != handle_main:
							handle_history = handle

					if handle_history is None:
						print 'The page has been closed, skip this page!'
						break;
					print "Switching to download page..."
					browser.switch_to_window(handle_history)
					data_exists_flag = False
					try:
						noDataPrompt = browser.find_element_by_css_selector('#noData')
						if noDataPrompt is None:
							print 'Can not find the no data prompt.'
						else:
							print 'No data here, attempt to retry'
							browser.close()
							browser.switch_to_window(handle_main)
							time.sleep(3)
					except:
						print 'It is able to get the data.'
						data_exists_flag = True

					if data_exists_flag:
						print 'Downloading...'
						self.enable_download_in_headless_chrome(browser, self.DOWNLOAD_TMP_PATH)
						download_button = browser.find_element_by_css_selector('.trend #Button2')
						download_button.click()
						time.sleep(4) #sleep to wait the download finish.
						self.move_and_rename_file(self.DOWNLOAD_PATH, file_name)
						print 'Successfully download to ' + self.DOWNLOAD_PATH + ' with file name as: ' + file_name
						browser.close()
						browser.switch_to_window(handle_main)
						break	#break the retry loop
			else:
				area = browser.find_element_by_css_selector(tr_css_sel_templ % row_idx + ' td').text
				area = area.strip()
				if area != u'华北地区':
					break

		time.sleep(5)
		browser.close()
		return 'return'

	def open_browser(self):
		options = Options()
		# options = webdriver.ChromeOptions()
		if self.HEADLESS_MODE:
			options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		options.add_argument("--start-maximized")
		prefs = {'download.default_directory' : self.DOWNLOAD_TMP_PATH}
		options.add_experimental_option('prefs', prefs)
		# options.add_argument("download.default_directory=/home/ren/work/git_repos/pe_scrapy/pe")
		browser = webdriver.Chrome(chrome_options=options)
		# browser = webdriver.PhantomJS()
		# browser = webdriver.Firefox()
		
		browser.implicitly_wait(5)  # wait until the page is fully loaded.

		return browser

	#download function is closed when open headless mode, this cammand will enable the download in the current tab
	def enable_download_in_headless_chrome(self, driver, download_dir):
		if not self.HEADLESS_MODE:
			return
		# add missing support for chrome "send_command"  to selenium webdriver
		driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

		params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
		command_result = driver.execute("send_command", params)
		# print("response from browser:")
		# for key in command_result:
		#	 print("result:" + key + ":" + str(command_result[key]))

	def move_and_rename_file(self, dest_path, newname):
		files = os.listdir(self.DOWNLOAD_TMP_PATH)
		find_flag = False
		for f in files:
			if f == self.DOWNLOAD_FILE_TMP_NAME:
				find_flag = True
				oldname = os.path.join(self.DOWNLOAD_TMP_PATH, f)
				newname = os.path.join(dest_path, newname)
				print 'Moving %s to %s' % (oldname, newname)
				os.rename(oldname, newname)
				print 'OK.'

		if not find_flag:
			print 'Can not find the file %s, no operation applied.' % self.DOWNLOAD_FILE_TMP_NAME
