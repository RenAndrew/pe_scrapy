# -*- coding: utf-8 -*-
#PP粉料
from splash_base import SplashSpiderBase

from ..util import html_table_parsing

from user_items import Chem99PPPowderPrice


class Chem99PPPowderPriceWeek(SplashSpiderBase):
	name = 'chem99_pp_powder'

	SEARCH_API_META = {
		"keyword" : "聚丙烯粉料及上游丙烯价格一览",
		"sccid" : 0,
	}

	# DEBUG_URL = 'http://plas.chem99.com/news/30404467.html'

	def parse_page(self, response):
		print '====================> parse chem99_pp_powder'
		try:
			table_html = response.css('#PanelContent table').extract_first()
			table = html_table_parsing(table_html)

			for i in range(1,len(table)):
				item = Chem99PPPowderPrice()
				row = table[i]

				item['region'] = self.clean_tags(row[0])
				price_range = self.clean_tags(row[1])
				prices = price_range.split('-')
				item['pp_powder_price_low'] = prices[0].strip()
				item['pp_powder_price_high'] = prices[1].strip()
				
				price_range = self.clean_tags(row[2])
				prices = price_range.split('-')
				item['propene_price_low'] = prices[0].strip()
				item['propene_price_high'] = prices[1].strip()
				
				item['name'] = self.name
				item['filename'] = self.name
				item['date'] = self.get_date_from_meta_info(response.url)

				yield item
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print e
			print '-' * 50
		print '=' * 40
		