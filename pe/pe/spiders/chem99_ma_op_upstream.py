# -*- coding: utf-8 -*-

#化工-MA上游开工-周度
from splash_base import SplashSpiderBase

from user_items import Chem99MaOperationRateUpstreamWeek,Chem99MaOperationRateUpstreamDetailWeek

from ..util import html_table_parsing

def filter_title(field):
	if not u'年' in field:
		return False
	else:
		return True

class Chem99MaOpUpstreamWeek(SplashSpiderBase):
	name = 'chem99_ma_op'

	SEARCH_API_META = {
		"keyword" : "国内甲醇装置有效开工率",
		"sccid" : 0,
		"filter" : {
			"field" : "Title",
			"method" : filter_title
		}
	}

	LOGIN_TYPE = 'CHEM_LOGIN'

	DEBUG_URL = 'http://chem.chem99.com/news/30417035.html'

	def parse_page(self, response):
		print '====================> parse chem99_ma_operation_rate_upstream'

		try:
			html_tabs = response.css('#PanelContent table').extract()

			table_op_rate = html_table_parsing(html_tabs[0])   #开工率
			table_detail_productivity = html_table_parsing(html_tabs[1])	#国内部分甲醇装置变动情况

			for i in range(1,3):
				item = Chem99MaOperationRateUpstreamWeek()
				item['operation_rate'] = self.clean_tags(table_op_rate[1][i])
				item['operation_rate_last_week'] = self.clean_tags(table_op_rate[2][i])
				item['compare_to_last_week'] = self.clean_tags(table_op_rate[3][i])
				item['operation_rate_last_year'] = self.clean_tags(table_op_rate[4][i])
				item['compare_year_on_year'] = self.clean_tags(table_op_rate[5][i])
				
				item['name'] = self.name
				item['unit'] = '%'

				news_info = self.visited_news.get( self._get_id_from_url(response.url) )
				if news_info:
					item['date'] = news_info['pubDate']

				if i == 1: 		#全国开工率
					item['filename'] = 'China_MA_operation_rate_weekly'
				else:
					item['filename'] = 'Nortwest_China_MA_operation_rate_weekly'

				yield item

			for i in range(1, len(table_detail_productivity)):
				item = Chem99MaOperationRateUpstreamDetailWeek()
				row = table_detail_productivity[i]

				item['region'] = self.clean_tags(row[0])
				item['company'] = self.clean_tags(row[1])
				item['productivity'] = self.clean_tags(row[2])
				item['raw_material'] = self.clean_tags(row[3])
				item['remarks'] = self.clean_tags(row[4])

				item['date'] = self.get_date_from_meta_info(response.url)
				item['filename'] = 'Ma_operation_rate_detail_weekly'

				yield item
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print e
			print '-' * 50
		print '=' * 40


		# for tab_in_html in html_tabs:
		# 	table = html_table_parsing(tab_in_html)

		# 	for i in range(0,len(table)):
		# 		# print table[i]
		# 		self.print_row(table[i])

		# 	print '----------------------------------------------'

		# selector_templ = '#PanelContent > table > tbody > tr:nth-child({0}) > td:nth-child({1})'
		# filename_map = {
		# 	2 : 'MA_Jiangsu',
		# 	3 : 'MA_Zhejiang',
		# 	4 : 'MA_Guangdong',
		# 	5 : 'MA_Fujian',
		# }
		# try:
		# 	for i in range(2,6):
		# 		item = Chem99MaOperationRateUpstreamWeek()
				
		# 		item['product_name'] = u'甲醇'
		# 		item['inv'] = self._strip_html_tags( response.css(selector_templ.format(2,i)).extract_first() ).encode('utf-8')
		# 		item['compare_to_last_week'] = self._strip_html_tags( response.css(selector_templ.format(3,i)).extract_first() ).encode('utf-8')
		# 		item['change'] = self._strip_html_tags( response.css(selector_templ.format(4,i)).extract_first() ).encode('utf-8')
		# 		item['unit'] = u'万吨'

		# 		item['name'] = self.name
		# 		item['filename'] = filename_map[i]

		# 		print self.visited_news
		# 		news_info = self.visited_news.get( self._get_id_from_url(response.url) )
		# 		# print news_info
		# 		if news_info:
		# 			item['date'] = news_info['pubDate']
				
		# 		#item['to_update'] == None
		# 		yield item
		

	def print_row(self, row):
		LEN = len(row)

		line = ''
		for j in range(0, LEN):
			line += self.clean_tags(row[j]) + ',  '

		print line