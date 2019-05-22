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

		print csv_path

		target_table_name = UploaderConfig().get_upload_config(crawler_name)\
											.get('ma_cn_cargo_price_daily')

		checkset = DbChecksetMaker().make_checkset(target_table_name)

		excel_builder = ExcelBuilder(config_name=crawler_name, csv_path=self.csv_aggregate_path, \
									 xls_outdir=self.xls_output_path)

		self.excel_file = excel_builder.check_before(checkset)\
					 				   .build()

		return self

	def upload_excel(self):
		retcode = self.read_configs()\
					  .login()\
					  .upload_in_append_mode(self.excel_file)

		return retcode


	def read_configs(self):
		main_url = BoxingConfig().get_main_url()
		db_config = DatabaseConfig()
		upload_config = UploaderConfig().get_upload_config(self.crawler_name)

		user = db_config.db_username()
		password = db_config.db_password()

		self.login_url = 'http://' + main_url + '/api/v1/sso/login'
		self.login_info = {
			'username' : user,
			'password': password
		}
		self.login_headers = {
			"Content-Type" : "application/json;charset=UTF-8",
			"host" : main_url,
			"User-Agent" : "Mozilla/5.0"
		}

		self.upload_url = main_url + upload_config.get('upload_api_uri')

		self.upload_headers = {
			'host' : main_url.replace('http://',''),
			# 'Host': 'localhost:9875',
			# 'Origin': 'http://localhost:9875',
			# 'Referer': 'http://localhost:9875/data/',
			#   'Cookie': 'phaseInterval=120000; previewCols=url%20status%20size%20timeline; stats=true; session=.eJwdjkFrwyAYhv_K8NyD2lrSwA4dWUMG3ycZuqCXsjm7ROMlXWlq6X9f2OGFBx54eO_keJr8uSfl73TxK3Icvkl5J09fpCSo9hTye5J1Kxbe2KBnyOMg1f4G9ce4LNqkKXQYoWu44fpquB2xigLySwKlKeZ4Q97MGGAGBUuvoUb9UKz6AKmhtjr0qDCYpLnscJQdMLt4W7cZwtJIbxE5MFlhlLXZYGivyF-ZVH20KnLIh0HW-pk8VuRy9tP_fyKEc8Va-NPWUcZ8UTi2K1whdvRzTf3Wkccf6DpOVQ.XN97jA.EMPsud7mffr1xPQTogHpEvDe1VU',
			'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
		}

		self.session = requests.session()
		return self

	def login(self):
		ret = self.session.post(self.login_url, data=json.dumps(self.login_info), headers=self.login_headers)
		return self

	def logout(self):
		self.session.close()

	def upload_in_append_mode(self, file):
		params = {
			'file' : file
		}

		print self.upload_url
		print self.upload_headers

		ret = self.session.post(self.upload_url, data= {'upload_type' : 'APPEND'}, files=params, headers=self.upload_headers)
	
		if (ret.status_code == 400):
			print json.loads(ret.text).get('message')
		elif (ret.status_code == 200):
			print "Uploading successfully!"
		else:
			print "Unknown Error!"
		print ret.text
		return ret.status_code

	def ensure_path_exists(self, path):
		if os.path.exists(path):
			return self
		else:
			os.makedirs(path)
			return self

if __name__ == '__main__':

	AutoUploader().process_results("oilchem_ma")
