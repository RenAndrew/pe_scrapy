# -*- coding: utf-8 -*-
import scrapy
import time, os
import re

import urllib
import urllib2
import zlib  #for gzip decompression
# import time, datetime
import json
import demjson

from scrapy import Spider, Request
from scrapy_splash import SplashRequest

from .. import SpiderBase
from pe.items import PeSumoPrice
from ..chem99_login import SeleniumLogin
from .. import webrender

'''
这个爬虫是所有卓越网(http://plas.chem99.com)爬虫的父类
提供基础的登陆功能，继承的爬虫只需要覆盖name和start_urls，以及：
重写parseAfterlogin方法，在这个方法中提取相关的数据生成Item

本类中，生成带headers和cookies的新request，
并重新爬取以获得登陆后的完整网页
'''
class SplashSpiderBase(Spider):
	name = 'splashbase'

    # allowed_domains = ['http://plas.chem99.com/news/30375838.html']
    # 这个start_url是塑料膜类别的索引页面地址，其他类别请覆盖这个地址
	# start_urls = ['http://www.sci99.com/search/?key=%E5%A1%91%E8%86%9C%E6%94%B6%E7%9B%98%E4%BB%B7&siteid=0']

	#Account info
	config = {
		'username' : 'founder123',
		'password' : '123Qweasd'
	}

	#spider settings, not in settings.py
	settings = {
		'SPLASH_URL' : 'http://localhost:8050',

		'DOWNLOADER_MIDDLEWARES' : {
			'scrapy_splash.SplashCookiesMiddleware': 723,
    		'scrapy_splash.SplashMiddleware': 725,
    		'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810
		},

		'SPIDER_MIDDLEWARES' : {
   			'scrapy_splash.SplashDeduplicateArgsMiddleware' : 100,
		},

		'DUPEFILTER_CLASS' : 'scrapy_splash.SplashAwareDupeFilter',
		'HTTPCACHE_STORAGE' : 'scrapy_splash.SplashAwareFSCacheStorage',

		'DOWNLOAD_DELAY' : 3,
		'RANDOMIZE_DOWNLOAD_DELAY' : True
	}

	SEARCH_API_META = {
		"keyword" : "塑膜收盘价",
		"sccid" : 4602
	}

	# splash lua script
	spl_script = """
         function main(splash, args)
         	 splash:set_custom_headers({
			     ["Accept"] = "application/json, text/plain, */*",
			     ["Accept-Language"] = "zh-CN,zh;q=0.8",
			     ["Connection"] = "keep-alive",
			     ["Content-Type"] = "application/x-www-form-urlencoded",
			     ["User-Agent"] = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36",
			 })
         	 splash:init_cookies(args.cookies)
             assert(splash:go(args.url))
             assert(splash:wait(args.wait))
             --return splash:get_cookies()
             return splash:html()
         end
         """

	fields_zn2en_mapping_dict = {
			u'BOPP光膜' : 'BOPP_guangmo',
			u'BOPET印刷膜' : 'BOPET_yinshuamo',
			u'BOPA印刷级' : 'BOPA_yinshuaji',
			u'CPP镀铝基材' : 'CPP_dulvjicai',
			u'PE缠绕膜' : 'PE_chanraomo',
			u'胶带母卷' : 'jiaodaimujuan',
			u'VMPET' : 'VMPET',
			u'VMCPP' : 'VMCPP',
		}

	def __init__(self):
		autologin_tool = SeleniumLogin(os.getcwd() + '/')
		autologin_tool.set_account(self.config['username'], self.config['password'])
		cookies = autologin_tool.selelogin('http://plas.chem99.com/news/30375838.html')

		# logined_cookies : 已登录的cookie
		self.logined_cookies = self._cookie_format_to_splash(cookies)
		self.logined_cookies_str = cookies
		# print self.logined_cookies_str
		# print self.logined_cookies

	def start_requests(self):
		link_producer = LinkProducer(self.logined_cookies_str, self.SEARCH_API_META)
		self.visited_news = link_producer.get_visited()		#get the detailed info of the news
		link_source = link_producer.link_factory()

		try:
			while True:
				link = link_source.next()
				yield self.produce_request(link)
		except StopIteration as e:
			pass

		link_producer.store_visited(self.name + '_visited.dat')

	# splash是一个动态页面渲染引擎，scrapy可以向本地splash申请渲染一个url并返回渲染后的页面
	def produce_request(self, url, callback_method=None):
		if callback_method is None:
			callback_method = self.parse_page
		return SplashRequest(url, callback=callback_method, endpoint='execute', args={'lua_source': self.spl_script, 'wait': 5, 'cookies': self.logined_cookies})

	def parse_page(self, response):
		print '====================> parse_page'

		try:
			for i in range(2,9):
				item = PeSumoPrice()
				selector_templ = '#PanelContent tbody tr:nth-child({0}) td:nth-child({1})'
				
				item['product_name'] = self._strip_html_tags( response.css(selector_templ.format(i, 1)).extract_first() ).encode('utf-8')
				item['model'] = self._strip_html_tags( response.css(selector_templ.format(i,2)).extract_first() ).encode('utf-8')
				item['price'] = self._strip_html_tags( response.css(selector_templ.format(i,3)).extract_first() ).encode('utf-8')
				item['increase_daily'] = self._strip_html_tags( response.css(selector_templ.format(i,4)).extract_first() )
				item['increase_to_last_week'] = self._strip_html_tags( response.css(selector_templ.format(i,5)).extract_first() )
				item['increase_to_last_month'] = self._strip_html_tags( response.css(selector_templ.format(i,6)).extract_first() )
				item['increase_to_last_year'] = self._strip_html_tags( response.css(selector_templ.format(i,7)).extract_first() )

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
			print e
			print '-' * 50
		print '=' * 40

	def _cookie_format_to_splash(self, cookie_str):
		splash_cookie = []

		cookie_list = cookie_str.split(';')
		# print cookieList

		for cookie in cookie_list:
			if cookie.find('=') == -1:
				continue

			cookie_dict = {}
			name, value = cookie.split('=')
			name = name.strip()
			value = value.strip()

			cookie_dict['name'] = name
			cookie_dict['value'] = value
			cookie_dict["domain"] = ".chem99.com"		#That makes cookie valid
			cookie_dict["path"] = "/"
			splash_cookie.append(cookie_dict)

		return splash_cookie

	def _get_id_from_url(self, url):
		pos1 = url.find('news/');
		pos2 = url.find('.html');

		try:
			news_id = url[pos1+5 : pos2]
		except:
			return ''

		return news_id

	def _strip_html_tags(self, content_with_html):
		content_with_html = content_with_html.replace('\n', '')  #delete \n to make regexp work
		content_pattern = re.compile('>(.*?)<')
		text_without_tag = ''.join(content_pattern.findall(content_with_html))
		return text_without_tag.strip()

	def _filename_according_to(self, product_name):
		file_name = self.fields_zn2en_mapping_dict.get(product_name)
		if file_name is None:
			return 'dnot_known_name'
		else:
			return file_name

class LinkProducer(object):

	base_url = 'http://plas.chem99.com/news/'
	search_api_url = 'http://www.sci99.com/search/ajax.aspx'

	DEBUG_MODE = False
	DEBUG_URL = 'http://plas.chem99.com/news/29796650.html'

	def __init__(self, cookie, meta):
		self.headers = {
			"Accept" : "application/json, text/plain, */*",
			"Accept-Language" : "zh-CN,zh;q=0.8",
			"Connection" : "keep-alive",
			"Content-Type" : "application/x-www-form-urlencoded",
			"User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36",
			"Host" : "www.sci99.com",
			"Origin" : "http://www.sci99.com",
			"cookie" : cookie,
			"X-Requested-With" : "XMLHttpRequest"
		}

		self.page_index = 0	#current page index

		self.post_data = {
			"action" : "getlist",
			"keyword" : meta["keyword"],
			"sccid" : meta['sccid'],
			"pageindex" : self.page_index,
			"siteids" : 0,
			"pubdate" : "",
			"orderby" : "true"
		}

		if meta.get("filter"):
			self.filter = meta["filter"]
		else:
			self.filter = None

		self.total_pages = self.next_news_page()
		print ('Total pages: ' + str(self.total_pages) )

		self.visited_news_dict = {}

	def link_factory(self):
		if self.DEBUG_MODE:
			yield self.DEBUG_URL
			return

		while self.page_index <= self.total_pages:
			if self.news_dict is None:
				raise Exception('No news source!')

			for news_id in self.news_dict:
				news_info = self.news_dict[news_id]
				# print 'Yielding =======> ' + news_info['url']
				if self._filter_by_field(news_info):
					# print '%' * 200
					continue
				
				self.record_visited(news_id, news_info)
				yield news_info['url']

			# self.next_news_page()
			break		#for test ignore the next page

	def next_news_page(self):
		self.page_index += 1
		self.post_data['pageindex'] = self.page_index
		news_json = self.fetch_news_info_list()
		self.news_dict = self.reformat_news_info( news_json['hits'] )
		return news_json['totalPages']

	def fetch_news_info_list(self):
		data = urllib.urlencode(self.post_data)
		req = urllib2.Request(self.search_api_url, headers=self.headers, data=data)
		response = urllib2.urlopen(req)
		retdata = response.read()

		ret_json = demjson.decode(retdata)

		return ret_json[0]

	def reformat_news_info(self, hits_list):
		news_page_dict = {}

		print '-' * 40
		print 'Page: ' + str(self.page_index)

		for news_item in hits_list:
			news_id = news_item['NewsKey'].encode('ascii')
			url = news_item['URL'].encode('ascii') + 'news/' + news_id + ".html"
			title = news_item['Title'].encode('utf-8')
			title = title.replace('<b>', '').replace('</b>', '')
			pub_time = news_item['PubTime'].encode('ascii')
			ta = time.strptime(pub_time.split('.')[0], '%Y-%m-%dT%H:%M:%S')
			pub_date = str(ta.tm_year) + '-' + str(ta.tm_mon) + '-' + str(ta.tm_mday)
			sccid = news_item['SCCID'].encode('ascii')
			class_name = news_item['ClassName'].encode('utf-8')

			print ('ID: %d: %s | %s | %s' % (int(news_id), url, title, pub_date))

			news_info = {
				"url" : url,
				"title" : title,
				"pubDate" : pub_date,
				"className" : class_name,
				"sccid" : sccid
			}
			
			news_page_dict[news_id] = news_info

		return news_page_dict

	def record_visited(self, news_id, news_info):
		self.visited_news_dict[news_id] = news_info

	def get_visited(self):
		return self.visited_news_dict

	def store_visited(self, file_name):
		visited_news_json = json.dumps(self.visited_news_dict)

		with open(file_name, 'w+') as f:
			f.write(visited_news_json)

	def _filter_by_field(self, news_info):

		if not self.filter:
			return False

		field_name = self.filter["field"]
		field_value = news_info.get(field_name)
		
		if field_value is None:
			print ('Field value is empty!')
			return False

		try:
			is_been_filtered = self.filter["method"](field_value)
			return is_been_filtered
		except:
			return False
