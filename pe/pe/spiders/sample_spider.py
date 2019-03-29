# encoding='utf-8'
from boxing.spider import SpiderBase
from user_items import SampleItem


class SampleSpider(SpiderBase):

    name = 'sample_spider'
    start_urls = [
        'http://www.sci99.com/',
    ]

    def parse(self, response):
        for dt in response.xpath('//*[@id="gundong1"]/div/dt'):
            yield SampleItem(
                filename=self.name,
                name=dt.xpath('span[1]/a/text()').extract_first(),
                unit=dt.xpath('span[2]/text()').extract_first(),
                cur_price=float(dt.xpath('span[3]/text()').extract_first()),
                delta=float(dt.xpath('span[4]/text()').extract_first()),
                week_price=float(dt.xpath('span[6]/text()').extract_first()),
                month_price=float(dt.xpath('span[7]/text()').extract_first())
            )
