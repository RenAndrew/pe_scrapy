# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

###################################
# basics
###################################


class BoxingSpiderItem(scrapy.Item):
    name = scrapy.Field()
    crawl_time = scrapy.Field()
    date = scrapy.Field()

    filename = scrapy.Field()   # WARNING! filename column will not appear in the exported csv

    to_update = scrapy.Field()
    target_table = scrapy.Field()
    target_column = scrapy.Field()
    src_column = scrapy.Field()

    @staticmethod
    def get_non_csv_columns():
        return ['filename', 'to_update', 'target_table', 'target_column', 'src_column']

########################################
####	Item of this project	########
########################################

class PeSumoPrice(BoxingSpiderItem):		#塑料膜
	product_name = scrapy.Field()
	model = scrapy.Field()		#规格
	price = scrapy.Field()
	increase_daily = scrapy.Field()
	increase_to_last_week = scrapy.Field()
	increase_to_last_month = scrapy.Field()
	increase_to_last_year = scrapy.Field()

	@staticmethod
	def get_non_csv_columns():
		return ['filename', 'to_update', 'target_table', 'target_column', 'src_column', 'crawl_time']


CN_COLUMN_NAMES = {
    # basic
    'filename': '文件名',
    'name': '名称',
    'crawl_time': '爬取时间',
    'unit': '单位',
    'cur_price': '现价格',
    'week_price': '周价格',
    'month_price': '月价格',
    'delta': '涨跌',
    '_id': 'ID',
    'quote_date': '报价日期',
    'product_name': '产品名称',
    'model': '规格型号',
    'area': '地区',
    'price_type': '价格类型',
    'low_price': '低端价',
    'high_price': '高端价',
    'middle_price': '中间价',
    'unit': '单位',
    'change': '涨跌幅',
    'price_in_cny': '人民币价',
    'unknown': '--',
    'remarks': '备注',
    'date': '日期',
    'commodity': '商品',
    'spot_or_future': '期/现货',
    'close_price': '收盘价',
    'daily_change': '比上日',
    'remarks': '备注',
    'company': '生产企业',
    'factory_price': '出厂价',

    #塑膜价格字段
    'price' : '价格',
    'increase_daily' : '日涨跌',
    'increase_to_last_week' : '较上周同期',
    'increase_to_last_month' : '较上月同期',
    'increase_to_last_year' : '较去年同期',
}

EN_COLUMN_NAMES = {value: key for key, value in CN_COLUMN_NAMES.items()}


class BoxingItemHelper(object):

    OC1 = 'oc1'
    OC2 = 'oc2'
    OC3 = 'oc3'

    @staticmethod
    def get_cn_column_name(en_column):
        return CN_COLUMN_NAMES.get(en_column, en_column)

    @staticmethod
    def get_en_column_name(cn_column):
        return EN_COLUMN_NAMES.get(cn_column)

###################################################


class DiMoPrice(scrapy.Item):
	name = scrapy.Field()
	price_low = scrapy.Field()
	price_high = scrapy.Field()


    