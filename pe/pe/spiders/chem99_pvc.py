# -*- coding: utf-8 -*-

from splash_base import SplashSpiderBase

from pe.items import PeNongmoPrice


class Chem99PvcWeek(SplashSpiderBase):
	name = 'chem99_pvc'

	SEARCH_API_META = {
		"keyword" : "本周PVC企业开工",
		"sccid" : 0
	}

	DEBUG_URL = 'http://plas.chem99.com/news/30420259.html'

	def parse_page(self, response):
		print '====================> parse chem99_pvc'

		print response.css('#Panel_News').extract_first()