# -*- coding: utf-8 -*-

import os,sys
import shutil
from ..util import TimeKit

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
		src_dir = os.path.join(self._from_src_path, crawler_name)
		# print os.listdir(src_dir)

		dates_refered = set()

		for file in os.listdir(src_dir):
			if not os.path.isfile(os.path.join(src_dir,file)):
				continue
			pos = file.rfind('_')
			if pos == -1:
				print 'Error processing %s, skiped.' % file
			dt = file[pos+1:].split('.')[0]
			print dt
			dates_refered.add(TimeKit.str_to_date(dt))

			target_dir = os.path.join(self._to_dest_path, crawler_name, dt)
			target_file = os.path.join(target_dir, file)
			src_file = os.path.join(src_dir, file)
			print src_file, target_file

			self.ensure_path_exists(target_dir)
			shutil.move(src_file, target_file)

		closest_day = str(max(dates_refered))
		print closest_day
		return os.path.join(self._to_dest_path, crawler_name, closest_day)

	def ensure_path_exists(self, path):
		if os.path.exists(path):
			return self
		else:
			os.makedirs(path)
			return self