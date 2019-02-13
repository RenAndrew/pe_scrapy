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
from pe.items import DiMoPrice
from ..chem99_login import SeleniumLogin
from .. import webrender

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

'''
这个爬虫是所有卓越网(http://plas.chem99.com)爬虫的父类
提供基础的登陆功能，继承的爬虫只需要覆盖name和start_urls，以及：
重写parseAfterlogin方法，在这个方法中提取相关的数据生成Item

本类中，生成带headers和cookies的新request，
并重新爬取以获得登陆后的完整网页
'''
class SplashSpiderBase(SpiderBase):
	name = 'splashspiderbase'

    # allowed_domains = ['http://plas.chem99.com/news/30375838.html']
    # 这个start_url是塑料膜类别的索引页面地址，其他类别请覆盖这个地址
	# start_urls = ['http://www.sci99.com/search/?key=%E5%A1%91%E8%86%9C%E6%94%B6%E7%9B%98%E4%BB%B7&siteid=0']

	#Account info
	userName = 'founder123'
	userPassword = '123Qweasd'

	#覆盖两个选择器之一，就可更新从索引页面提取链接的规则
	cssIndexExtractor = None
	xpathIndexExtractor = None

	SEARCH_API_META = {
		"keyword" : "塑膜收盘价",
		"sccid" : 4602
	}

	def __init__(self):
		loginMachine = SeleniumLogin(os.getcwd() + '/')
		loginMachine.setAccount(self.userName, self.userPassword)
		cookies = loginMachine.selelogin('http://plas.chem99.com/news/30375838.html')

		# loginedCookies : 已登录的cookie
		self.loginedCookies = self.cookieStrToSplashCookie(cookies)
		self.loginedCookiesInStr = cookies
		# print self.loginedCookiesInStr
		# print self.loginedCookies

	def start_requests(self):
		linkProducer = LinkProducer(self.loginedCookiesInStr, self.SEARCH_API_META)
		# linkProducer.fetchNewsList()
		self.visitedNews = linkProducer.getVisited()
		linkSource = linkProducer.linkFactory()

		try:
			while True:
				link = linkSource.next()
				yield self.produce_request(link)
		except StopIteration as e:
			pass

		linkProducer.store_visited(self.name + '_visited.dat')


	# splash是一个动态页面渲染引擎，scrapy可以向本地splash申请渲染一个url并返回渲染后的页面
	def produce_request(self, url, callbackMethod=None):
		if callbackMethod is None:
			callbackMethod = self.parse_page
		return SplashRequest(url, callback=callbackMethod, endpoint='execute', args={'lua_source': spl_script, 'wait': 5, 'cookies': self.loginedCookies})

	def parse(self, response):
		# only parse first page, the index page
		yield self.produce_request(response.url, callbackMethod=self.parseIndexPage)

	# def parseIndexPage(self, response):
	# 	#print response.body

	# 	linkUrls = self.extractLink(response)
	# 	for link in linkUrls:
	# 		# yield self.produce_request(link)
	# 		print link

	# 	if self.nextIndexPage(response) is not None:
	# 		nextPageUrl = self.nextIndexPage(response)
	# 		yield self.produce_request(nextPageUrl, callbackMethod=self.parseIndexPage)
	# 	else:
	# 		print 'No Next Index Page!'

	# # For different link extract rule, please rewrite this method
	# def extractLink(self, response):
	# 	print '---------------Extracting links-------------'
	# 	if self.cssIndexExtractor is not None:
	# 		linkUrls = response.css(self.cssIndexExtractor).extract()
	# 	elif self.xpathIndexExtractor is not None:
	# 		linkUrls = response.xpath(self.xpathIndexExtractor).extract()
	# 	else:
	# 		linkUrls = response.css('#form1 div.main_l ul.ul_list li a.info::attr(href)').extract()

	# 	links = []
	# 	for link in linkUrls:
	# 		link = link.encode('ascii').strip()
	# 		print link
	# 		links.append(link)

	# 	print '-' * 40
	# 	return []

	# def nextIndexPage(self, response):
	# 	return None

	def parse_page(self, response):
		print '====================> parse_page'
		# print response.body

		priceName = response.css('#PanelContent tbody tr:nth-child(2) td:nth-child(1)').extract_first()
		priceLow = response.css('#PanelContent tbody tr:nth-child(2) td:nth-child(3)').extract_first()

		# priceName = response.xpath('//*[@id="PanelContent"]//tbody/tr[2]/td[1]/text()').extract_first()
		# priceLow = response.xpath('//*[@id="PanelContent"]//tbody/tr[2]/td[3]/text()').extract_first()

		# if not priceName:
		# 	print 'priceName: ' + str(priceName)
		# 	priceName = response.css('#myRptTable tbody tr:nth-child(2) td:nth-child(1)::text').extract_first()
		# if not priceLow:
		# 	print 'priceLow: ' + str(priceLow)
		# 	priceLow = response.css('#myRptTable tbody tr:nth-child(2) td:nth-child(3)::text').extract_first()
		print priceName, priceLow
		if priceName and priceLow:
			priceName = self._strip_html_tags(priceName)
			priceLow = self._strip_html_tags(priceLow)
		else:
			print '-' * 50
			print response.status
			# print response.body
			print 'Error in parsing...'
			print '-' * 50
			return
			# raise Exception('Error in parsing...')

		priceHigh = priceLow

		# print priceName, priceLow, priceHigh
		newsInfo = self.visitedNews.get( self.getIdFromUrl(response.url) )
		if newsInfo:
			print newsInfo['title']

		yield DiMoPrice(
				name = priceName,
				price_low = priceLow,
				price_high = priceHigh,
			)
		print '='*30

	def cookieStrToSplashCookie(self, cookie_str):
		splashCookie = []

		cookieList = cookie_str.split(';')
		# print cookieList

		for cookie in cookieList:
			if cookie.find('=') == -1:
				continue

			cookieDict = {}
			name, value = cookie.split('=')
			name = name.strip()
			value = value.strip()

			cookieDict['name'] = name
			cookieDict['value'] = value
			cookieDict["domain"] = ".chem99.com"		#That makes cookie valid
			cookieDict["path"] = "/"
			splashCookie.append(cookieDict)

		return splashCookie

	def getIdFromUrl(self, url):
		pos1 = url.find('news/');
		pos2 = url.find('.html');

		try:
			newsId = url[pos1+5 : pos2]
		except:
			return ''

		return newsId

	def _strip_html_tags(self, content_with_html):
		content_pattern = re.compile('>(.*?)<')
		text_without_tag = ''.join(content_pattern.findall(content_with_html))
		return text_without_tag

class LinkProducer(object):

	baseUrl = 'http://plas.chem99.com/news/'
	itemsInEachPage = 25
	searchApiUrl = 'http://www.sci99.com/search/ajax.aspx'

	DEBUG_MODE = False
	DEBUG_URL = 'http://plas.chem99.com/news/29796650.html'

	def __init__(self, cookieInStr, meta):
		self.headers = {
			"Accept" : "application/json, text/plain, */*",
			"Accept-Language" : "zh-CN,zh;q=0.8",
			"Connection" : "keep-alive",
			"Content-Type" : "application/x-www-form-urlencoded",
			"User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36",
			"Host" : "www.sci99.com",
			"Origin" : "http://www.sci99.com",
			"cookie" : cookieInStr,
			"X-Requested-With" : "XMLHttpRequest"
		}

		self.pageIndex = 1	#current page index

		self.postData = {
			"action" : "getlist",
			"keyword" : meta["keyword"],
			"sccid" : 0,
			"pageindex" : self.pageIndex,
			"siteids" : 0,
			"pubdate" : "",
			"orderby" : "true"
		}

		newsListRetJson = self.fetchNewsList()
		self.pageIndex += 1
		self.totalPages = newsListRetJson['totalPages']
		self.newsDict = self.formattingNewsUrl( newsListRetJson['hits'] )

		self.visitedNewsDict = {}

	def linkFactory(self):
		if self.DEBUG_MODE:
			yield self.DEBUG_URL
			return

		while self.pageIndex <= self.totalPages:
			if self.newsDict is None:
				raise Exception('No news source!')

			for newsId in self.newsDict:
				newsInfo = self.newsDict[newsId]
				print 'Yielding =======> ' + newsInfo['url']
				self.recordVisited(newsId, newsInfo)
				yield newsInfo['url']

			self.nextNewsPage()
			
		# yield 'http://plas.chem99.com/news/29329428.html'

	def nextNewsPage(self):
		self.pageIndex += 1
		self.postData['pageindex'] = self.pageIndex
		newsListRetJson = self.fetchNewsList()
		self.newsDict = self.formattingNewsUrl( newsListRetJson['hits'] )

	def fetchNewsList(self):
		data = urllib.urlencode(self.postData)
		req = urllib2.Request(self.searchApiUrl, headers=self.headers, data=data)
		response = urllib2.urlopen(req)
		retdata = response.read()

		retJson = demjson.decode(retdata)

		return retJson[0]

	def formattingNewsUrl(self, hitsList):
		newsPageDict = {}

		print '-' * 40
		print 'Page: ' + str(self.pageIndex)

		for newsItem in hitsList:
			newsId = newsItem['NewsKey'].encode('ascii')
			url = newsItem['URL'].encode('ascii') + 'news/' + newsId + ".html"
			title = newsItem['Title'].encode('utf-8')
			title = title.replace('<b>', '').replace('</b>', '')
			pubTime = newsItem['PubTime'].encode('ascii')
			ta = time.strptime(pubTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
			pubDate = str(ta.tm_year) + '-' + str(ta.tm_mon) + '-' + str(ta.tm_mday)
			sccid = newsItem['SCCID'].encode('ascii')
			className = newsItem['ClassName'].encode('ascii')

			print ('ID: %d: %s | %s | %s' % (int(newsId), url, title, pubDate))

			newsInfo = {
				"url" : url,
				"title" : title,
				"pubDate" : pubDate,
				"className" : className
			}
			
			newsPageDict[newsId] = newsInfo

		return newsPageDict

	def recordVisited(self, newsId, newsInfo):
		self.visitedNewsDict[newsId] = newsInfo

	def getVisited(self):
		return self.visitedNewsDict

	def store_visited(self, file_name):
		pass
