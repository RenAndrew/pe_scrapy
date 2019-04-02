# -*- coding: utf-8 -*-

from splash_base import SplashSpiderBase

from user_items import Chem99NongmoPrice

def filter_weekly_news(title):
		
	if title.find(u'农膜周评') != -1:
		# print '*' * 50
		# print title
		# print '*' * 50
		return True
	else:
		return False

class Chem99NongmoPriceDaily(SplashSpiderBase):
	name = 'chem99_nongmo'

	# DEBUG_URL = 'http://plas.chem99.com/news/30375838.html'

	SEARCH_API_META = {
		"keyword" : "农膜日评",
		"sccid" : 4520,
		"filter" : {
			"field" : "Title",
			"method" : filter_weekly_news
		}
	}

	fields_zn2en_mapping_dict = {
			u'双防膜' : 'Shuangfangmo',
			u'白膜' : 'Baimo',
			u'地膜' : 'Dimo',
			u'西瓜膜' : 'Xiguamo',
		}

	def parse_page(self, response):
		print '====================> parse nongmo'
		selector_templ = '#PanelContent div:nth-child(4) tbody tr:nth-child({0}) td:nth-child({1})'
		try:
			for i in range(2,5):
				item = Chem99NongmoPrice()
				
				item['product_name'] = self._strip_html_tags( response.css(selector_templ.format(i, 1)).extract_first() ).encode('utf-8')
				item['price_shandong'] = self._strip_html_tags( response.css(selector_templ.format(i,2)).extract_first() ).encode('utf-8')
				item['price_jiangsu'] = self._strip_html_tags( response.css(selector_templ.format(i,3)).extract_first() ).encode('utf-8')
				item['price_jingjin'] = self._strip_html_tags( response.css(selector_templ.format(i,4)).extract_first() ).encode('utf-8')
				
				item['name'] = self.name
				item['filename'] = self._filename_according_to(item['product_name'].decode('utf-8'))

				news_info = self.visited_news.get( self._get_id_from_url(response.url) )
				if news_info:
					item['date'] = news_info['pubDate']
				
				#to_update is None
				yield item
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print response.css('.news_content h1').extract_first()
			print e
			print '-' * 50
		print '=' * 40