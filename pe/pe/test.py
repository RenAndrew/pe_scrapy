# -*- coding: utf-8 -*-
import sys
# from boxing.spider import SpiderBase, SpiderConfig
from util import AutoLoginTool, UrlCrawler, UrlCrawlerConfig, SeleniumLogin

start_url = 'https://www.oilchem.net/'
cookie_available = 'refcheck=ok; refpay=0; refsite=; _imgCode=ZHY2; _member_user_tonken_=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZWMiOiIkMmEkMTAkNU9hNGFEME1YV25VazFRb1ozRlhyLnEvMkNwa3dseWRkSU5DTHNnakJEN0gwQ3BDcmFDYi4iLCJuaWNrTmFtZSI6IiIsInBpYyI6IiIsImV4cCI6MTU1NjYxNTY4MywidXNlcklkIjoxNjQ2MzcsImlhdCI6MTU1NjUyOTI4MywianRpIjoiYWI2MzU2ZGYtMzczMS00MWRjLTgwYjItYmY2OTYzN2IzOWM4IiwidXNlcm5hbWUiOiJheHpxMTAxMCJ9.SirW0r1A3tYwxzdACerS22SEfdJyufgTZYFVZdyYMrc'


if __name__ == '__main__':

	cookie_available = SeleniumLogin('axzq1010', 'ax1010zq')
    req_url = 'https://dc.oilchem.net/priceDomestic/history.htm'
    crawler_config = UrlCrawlerConfig('5503', '2018-12-01', 'today')
    crawler = UrlCrawler(crawler_config)

    records = []
    records = crawler.download_data(req_url, cookie_available)
    

    print records