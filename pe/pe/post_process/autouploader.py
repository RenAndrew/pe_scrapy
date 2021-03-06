# -*- coding: utf-8 -*-
import os
import time
import requests
import json
import urllib

from upload_config import UploaderConfig
from xls_builder import ExcelBuilder
from files_collector import FilesCollector
from db_checkset import DbChecksetMaker
from mylogin import MyLogin

from boxing import BoxingConfig,DatabaseConfig

class AutoUploader(object):

	def __init__(self, crawler_name):
		self.crawler_name = crawler_name
		upload_config = UploaderConfig().get_upload_config("upload_basic")
		print os.getcwd()
		if os.path.exists(os.path.join(os.getcwd(), 'DEV_FLAG')):   #runs in dev mode.
			self.csv_download_path = './result'
			self.csv_aggregate_path = './pe/work/csv'
			self.xls_output_path = './pe/work/upload_work_dir'
		else:
			self.csv_download_path = upload_config.get('csv_download_path')
			self.csv_aggregate_path = upload_config.get('csv_aggregate_path')
			self.xls_output_path = upload_config.get('xls_output')

		self.ensure_path_exists(self.csv_download_path)\
			.ensure_path_exists(self.csv_aggregate_path)\
			.ensure_path_exists(self.xls_output_path)

	def wait_until_dumping_finished(self, compelte_flag):
		while True:
			time.sleep(5)
			if self.detect(compelte_flag):
				break
			print '...'
			opt = raw_input('Still wait?')
			if opt != 'y':
				break

		return self

	def detect(self, compelete_flag):
		flag_file = os.path.join(self.csv_download_path, self.crawler_name, compelete_flag)
		if os.path.exists(flag_file):
			#delete compelete_flag
			os.remove(flag_file)
			return True
		return False
	
	def process_results(self, crawler_name):
		csv_path = FilesCollector().from_path(self.csv_download_path)\
						.to_path(self.csv_aggregate_path)\
						.collect_files_of(crawler_name)
		# csv_path = "/home/ren/work/git_repos/pe_scrapy/pe/pe/work/csv/oilchem_ma/2019-05-22/"

		print "Processing csv files in:"
		print csv_path

		target_table_name = UploaderConfig().get_upload_config(crawler_name)\
											.get('target_table')

		checkset = DbChecksetMaker().make_checkset(target_table_name)

		excel_builder = ExcelBuilder(config_name=crawler_name, csv_path=csv_path, \
									 xls_outdir=self.xls_output_path)

		self.excel_file = excel_builder.check_before(checkset)\
					 				   .build()

		return self

	def upload_excel(self):
		print 
		print 'Start uploading excel data...'
		print 
		retcode = self.read_configs()\
					  .login()\
					  .upload_in_append_mode(self.excel_file)
		self.logout()

		return retcode


	def read_configs(self):
		upload_basic = UploaderConfig().get_upload_config("upload_basic")
		main_url = upload_basic.get('main_url')
		main_url = main_url.encode('ascii')

		user = upload_basic.get('username').encode('ascii')
		password = upload_basic.get('password').encode('ascii')

		upload_config = UploaderConfig().get_upload_config(self.crawler_name)

		# self.login_url = 'http://' + main_url + '/api/v1/sso/login'
		self.login_url = 'http://' + main_url + '/login'
		self.login_info = {
			'username' : user,
			'password': password
		}
		self.login_headers = {
			"Content-Type" : "application/json;charset=UTF-8",
			"host" : main_url,
			"User-Agent" : "Mozilla/5.0"
		}

		self.upload_url = 'http://' + main_url + upload_config.get('upload_api_uri')

		self.upload_headers = {
			'host' : main_url.replace('http://',''),
			'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
		}

		self.session = requests.session()
		return self

	def login(self):
		print 'Login to ' + self.login_url
		print self.login_info
		cookie_str = MyLogin.login(self.login_url, self.login_info['username'], self.login_info['password'])
		self.upload_headers['Cookie'] = cookie_str
		return self

	def logout(self):
		self.session.close()

	def upload_in_append_mode(self, file_name):
		file = open(file_name)
		params = {
			'file' : file
		}

		print 'Upload to url: ' + self.upload_url
		print 
		# print self.upload_headers
		print 'File name is: ' + file_name

		ret = requests.post(self.upload_url, data= {'upload_type' : 'APPEND'}, files=params, headers=self.upload_headers)
	
		flag = False
		if (ret.status_code == 400):
			print json.loads(ret.text).get('message')
		elif (ret.status_code == 401):
			print 'Unauthorized, please check login!'
			print ret.text
		elif (ret.status_code == 200):
			print "Uploading successfully!"
			flag = True
		else:
			print "Unknown Error!"
			print ret.text

		file.close()
		return flag

	def ensure_path_exists(self, path):
		if os.path.exists(path):
			return self
		else:
			os.makedirs(path)
			return self

if __name__ == '__main__':

	# AutoUploader("oilchem_ma").process_results("oilchem_ma")
	uploader = AutoUploader("oilchem_ma")
	uploader.excel_file = "/shared/boxing/user_spiders/work/xls/oilchem_ma_2019-05-24.xlsx"
	uploader.upload_excel()
