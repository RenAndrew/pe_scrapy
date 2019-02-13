# -*- coding: utf-8 -*-
import scrapy
import time, os

import urllib
import urllib2
import zlib  #for gzip decompression

from scrapy import Spider, Request
from scrapy_splash import SplashRequest


from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作
from selenium.webdriver.common.keys import Keys

from .. import SpiderBase
from pe.items import DiMoPrice
from ..chem99_login import SeleniumLogin
from .. import webrender

# splash lua script
script = """
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
class SplashSpider(SpiderBase):
	name = 'splashspider'

    # allowed_domains = ['http://plas.chem99.com/news/30375838.html']
	start_urls = ['http://www.sci99.com/search/?key=%E5%A1%91%E8%86%9C%E6%94%B6%E7%9B%98%E4%BB%B7&siteid=0']

	# start request
	def produce_request(self, url):
		return SplashRequest(url, callback=self.parseAfterSplash, endpoint='execute', args={'lua_source': script, 'wait': 5, 'cookies': self.loginedCookies})

	userName = 'founder123'
	userPassword = '123Qweasd'

	def __init__(self):
		loginMachine = SeleniumLogin(os.getcwd() + '/')
		loginMachine.setAccount(self.userName, self.userPassword)
		cookies = loginMachine.selelogin('http://plas.chem99.com/news/30375838.html')
		# self.loginedCookies = self.cookieStrToDict(cookies)
		self.loginedCookies = self.cookieStrToSplashCookie(cookies)

		# print self.loginedCookies

		self.loginHeaders = {
			'Accept':'application/json, text/plain, */*',
		    'Accept-Language':'zh-CN,zh;q=0.8',
		    'Connection':'keep-alive',
		    'Content-Type':'application/x-www-form-urlencoded',
		    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'
		}

	def parse(self, response):
		# linkUrls = webrender.WebpageRenderer().renderByCss(response.url, '#form1 .main_l .ul_list .info', webrender.extractLink)
		
		# for link in linkUrls:
		# 	yield self.produce_request(link)
		# 	break;
		yield self.produce_request('http://plas.chem99.com/news/30630684.html')

	def produceRequest(self, url):	#to generate request with cookie
		return scrapy.Request(url=url, callback=self.parseAfterlogin, headers=self.loginHeaders, cookies=self.loginedCookies, errback=self.reqErrorHandler)

	def reqErrorHandler(self, whatHappened):
		print '<<<<<<<<<<<<<<<<<< ERROR >>>>>>>>>>>>>>>'
		print whatHappened

	def parseAfterSplash(self, response):
		print '====================> parseAfterSplash'
		# print response.body
		
		# print response.cookies

		priceName = response.css('#myRptTable > tbody > tr:nth-child(2) > td:nth-child(1)::text').extract_first().strip()
		priceLow = response.css('#myRptTable > tbody > tr:nth-child(2) > td:nth-child(3)::text').extract_first().strip()
		priceHigh = priceLow

		print priceName, priceLow, priceHigh

		yield DiMoPrice(
				name = priceName,
				price_low = priceLow,
				price_high = priceHigh,
			)
		print '='*30


	def parseAfterlogin(self, response):
		# print '======> parseAfterlogin'
		# print response.body
		priceName = response.xpath('//*[@id="PanelContent"]/div[3]/table/tbody/tr[4]/td[1]/text()').extract_first().strip()
		priceLow = response.xpath('//*[@id="PanelContent"]/div[3]/table/tbody/tr[4]/td[2]/text()').extract_first().strip()
		priceHigh = response.xpath('//*[@id="PanelContent"]/div[3]/table/tbody/tr[4]/td[4]/text()').extract_first().strip()

		print priceName, priceLow, priceHigh

		yield DiMoPrice(
				name = priceName,
				price_low = priceLow,
				price_high = priceHigh,
			)

	def cookieStrToDict(self, cookie_str):
		cookieDict = {}

		cookieList = cookie_str.split(';')
		# print cookieList

		for cookie in cookieList:
			if cookie.find('=') == -1:
				continue
			name, value = cookie.split('=')
			name = name.strip()
			value = value.strip()

			# print name, value

			cookieDict[name] = value

		return cookieDict

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
