# -*- coding: utf-8 -*-

from splash_base import SplashSpiderBase

from pe.items import PeNongmoPrice


def filter_pvc_sccid(field):
	if field == "3265":
		return False
	else:
		return True

class Chem99PvcWeek(SplashSpiderBase):
	name = 'chem99_pvc'

	SEARCH_API_META = {
		"keyword" : "本周PVC企业开工",
		"sccid" : 0,
		"filter" : {
			"field" : "SCCID",
			"method" : filter_pvc_sccid
		},
	}

	DEBUG_URL = 'http://plas.chem99.com/news/30420259.html'

	def parse_page(self, response):
		print '====================> parse chem99_pvc'

		print response.css('#Panel_News').extract_first()