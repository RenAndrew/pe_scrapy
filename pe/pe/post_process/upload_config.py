# -*- coding: utf-8 -*-

import os,json

from boxing import BoxingConfig, Singleton

class UploaderConfig:
	"""config for AutoUploader"""
	__metaclass__ = Singleton

	def __init__(self):
		super(UploaderConfig, self).__init__()
		
		self.UPLOAD_CONFIG_FILE = '/shared/boxing/config/upload_config.json'
		self.upload_config = json.load(open(self.UPLOAD_CONFIG_FILE))

	def get_upload_config(self, config_name):
		return self.upload_config[config_name]
