import scrapy


class SpiderBase(scrapy.Spider):
    # name = ''
    # start_urls = []

    def closed(self, reason):
        print self.name, reason