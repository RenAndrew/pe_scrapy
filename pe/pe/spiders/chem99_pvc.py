# -*- coding: utf-8 -*-
from splash_base import SplashSpiderBase

from ..util import html_table_parsing

from user_items import Chem99PvcOpRateWeek

def filter_pvc_sccid(field):
	if field == "698":
		return False
	else:
		return True

def filter_pvc_title(field):
	if field.find(u'糊树脂') == -1:
		return False
	else:
		return True

class Chem99PvcOperationWeek(SplashSpiderBase):
	name = 'chem99_pvc'

	SEARCH_API_META = {
		"keyword" : "本周PVC企业开工",
		"sccid" : 0,
		"filter" : [{
			"field" : "SCCID",
			"method" : filter_pvc_sccid
		},{
			"field" : "Title",
			"method" : filter_pvc_title
		},]
	}

	# DEBUG_URL = 'http://plas.chem99.com/news/30420259.html'

	def parse_page(self, response):
		print '====================> parse chem99_pvc'
		try:
			# print response.css('#PanelContent').extract_first()
			table_html = response.css('#PanelContent table').extract_first()
			print table_html
			table = html_table_parsing(table_html)

			for i in range(1,len(table)):

				item = Chem99PvcOpRateWeek()
				row = table[i]

				print row[0], row[1], row[2], row[3], row[4], row[5]

				item['area'] = self.clean_tags(row[0])
				item['province'] = self.clean_tags(row[1])
				item['producer'] = self.clean_tags(row[2])
				item['tech_process'] = self.clean_tags(row[3])
				item['brand'] = self.clean_tags(row[4])
				item['operation_rate'] = self.clean_tags(row[5])

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
		
	# def _strip_html_tags(self, content_with_html):
	# 	# print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
	# 	content_with_html = '>' + content_with_html.replace('\n', '') + '<' #delete \n to make regexp work
	# 	content_pattern = re.compile('>(.*?)<')
	# 	# print content_pattern.findall(content_with_html)
	# 	text_without_tag = ''.join(content_pattern.findall(content_with_html))
	# 	return text_without_tag.strip()
	# 	