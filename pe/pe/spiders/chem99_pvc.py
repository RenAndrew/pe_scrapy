# -*- coding: utf-8 -*-

from splash_base import SplashSpiderBase

from pe.items import PeNongmoPrice


class Chem99PvcWeek(SplashSpiderBase):
	name = 'chem99_pvc'

	SEARCH_API_META = {
		"keyword" : "甲醇港口库存量",
		"sccid" : 0
	}

	def parse_page(self, response):
		print '====================> parse chem99_pvc'

		print response.css('.news_info').extract_first()