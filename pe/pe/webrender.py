# -*- coding: utf-8 -*-
import time

from selenium import webdriver


class WebpageRenderer(object):

	def renderByCss(self, url, csspath, extractMethod):
		browser = webdriver.Chrome()
		# browser = webdriver.PhantomJS()
		browser.implicitly_wait(5)  # wait until the page is fully loaded.

		browser.get(url)

		targets = browser.find_elements_by_css_selector(csspath)

		data = extractMethod(targets)

		browser.close()

		return data

def extractLink(targets):
	urlList = []
	for tgt in targets:
		try:
			href = tgt.get_attribute('href')
			if href is not None and href.strip() != '':
				href = href.encode('ascii')
				urlList.append(href)
		except:
			print ("Error in element: " + tgt.get_attribute('innerHTML'))

	return urlList

def extractChanraomo(targets):

	if (len(targets) == 0):
		return None

	return targets[0]


if __name__ == '__main__':
	renderMachine = WebpageRenderer()

	url = 'http://www.sci99.com/search/?key=%E5%A1%91%E8%86%9C%E6%94%B6%E7%9B%98%E4%BB%B7&siteid=0'
	csspath = '#form1 .main_l .ul_list .info'

	urlList = renderMachine.renderByCss(url, csspath, extractLink)
	print urlList