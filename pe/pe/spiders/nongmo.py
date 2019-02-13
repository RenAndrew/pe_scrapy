# -*- coding: utf-8 -*-

from splash_base import SplashSpiderBase


class NongmoSpider(SplashSpiderBase):
	name = 'nongmo'

	
	SEARCH_API_META = {
		"keyword" : "塑膜收盘价",
		"sccid" : 4602
	}

	def parse_page(self, response):
		print '====================> parse nongmo'

		