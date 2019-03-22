# -*- coding: utf-8 -*-
import re
from splash_base import SplashSpiderBase

from ..util import html_table_parsing

from user_items import Chem99PvcOpRateWeek

def filter_pvc_sccid(field):
	if field == "698":
		return False
	else:
		return True

class Chem99PvcOperationWeek(SplashSpiderBase):
	name = 'chem99_pvc'

	SEARCH_API_META = {
		"keyword" : "本周PVC企业开工",
		"sccid" : 0,
		"filter" : {
			"field" : "SCCID",
			"method" : filter_pvc_sccid
		},
	}

	# DEBUG_URL = 'http://plas.chem99.com/news/30420259.html'

	def parse_page(self, response):
		print '====================> parse chem99_pvc'
		try:
			# print response.css('#PanelContent').extract_first()
			table_html = response.css('#PanelContent table').extract_first()
			# print table_html
			table = html_table_parsing(table_html)

			for i in range(1,len(table)):

				item = Chem99PvcOpRateWeek()
				row = table[i]

				item['area'] = self._strip_html_tags(row[0])
				item['province'] = self._strip_html_tags(row[1])
				item['producer'] = self._strip_html_tags(row[2])
				item['tech_process'] = self._strip_html_tags(row[3])
				item['brand'] = self._strip_html_tags(row[4])
				item['op_rate'] = self._strip_html_tags(row[5])

				item['name'] = self.name
				item['filename'] = self.name
				news_info = self.visited_news.get( self._get_id_from_url(response.url) )
				if news_info:
					item['date'] = news_info['pubDate']

				yield item
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print e
			print '-' * 50
		print '=' * 40
		
	def _strip_html_tags(self, content_with_html):
		# print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
		content_with_html = '>' + content_with_html.replace('\n', '') + '<' #delete \n to make regexp work
		content_pattern = re.compile('>(.*?)<')
		# print content_pattern.findall(content_with_html)
		text_without_tag = ''.join(content_pattern.findall(content_with_html))
		return text_without_tag.strip()
		