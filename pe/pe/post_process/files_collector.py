# -*- coding: utf-8 -*-

import os,sys

class FilesCollector(object):

	def __init__(self):
		pass

	def from_path(self, from_src):
		self._from_src_path = from_src
		return self

	def to_path(self, to_dest):
		self._to_dest_path = to_dest
		return self

	def collect_files_of(self, crawler_name):
		pass