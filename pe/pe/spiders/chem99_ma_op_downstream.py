# -*- coding: utf-8 -*-

#化工-MA下游开工-周度
from splash_base import SplashSpiderBase

from user_items import Chem99MaOperationRateDownstreamWeek

def filter_sccid(field):
	if field == '458':
		return False
	else:
		return True

def filter_title(field):
	if not u'年' in field:
		return False
	else:
		return True

class Chem99MaOpDownstreamWeek(SplashSpiderBase):
	name = 'chem99_ma_op_down'

	SEARCH_API_META = {
		"keyword" : "国内甲醇装置有效开工率",
		"sccid" : 0,
		"filter" : [{
			"field" : "SCCID",
			"method" : filter_sccid
		},{
			"field" : "Title",
			"method" : filter_title
		}]
	}

	LOGIN_TYPE = 'CHEM_LOGIN'

	DEBUG_URL = 'http://chem.chem99.com/news/30417097.html'

	def parse_page(self, response):
		print '====================> parse chem99_ma_inv_week'

		selector_templ = '#PanelContent > table > tbody > tr:nth-child({0}) > td:nth-child({1})'
		filename_map = {
			2 : 'MA_Jiangsu',
			3 : 'MA_Zhejiang',
			4 : 'MA_Guangdong',
			5 : 'MA_Fujian',
		}
		try:
			for i in range(2,6):
				item = Chem99MaOperationRateDownstreamWeek()
				
				item['product_name'] = u'甲醇'
				item['inv'] = self._strip_html_tags( response.css(selector_templ.format(2,i)).extract_first() ).encode('utf-8')
				item['compare_to_last_week'] = self._strip_html_tags( response.css(selector_templ.format(3,i)).extract_first() ).encode('utf-8')
				item['change'] = self._strip_html_tags( response.css(selector_templ.format(4,i)).extract_first() ).encode('utf-8')
				item['unit'] = u'万吨'

				item['name'] = self.name
				item['filename'] = filename_map[i]

				print self.visited_news
				news_info = self.visited_news.get( self._get_id_from_url(response.url) )
				# print news_info
				if news_info:
					item['date'] = news_info['pubDate']
				
				#item['to_update'] == None
				yield item
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print e
			print '-' * 50
		print '=' * 40