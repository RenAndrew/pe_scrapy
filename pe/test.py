# -*- coding: utf-8 -*-
import time
import os


class TEST:
	DOWNLOAD_PATH = '/home/ren/work/git_repos/pe_scrapy/pe/result'
	DOWNLOAD_FILE_TMP_NAME = 'historydata.xls'

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


TEST().move_and_rename_file('./tmp', 'historydata.xls')