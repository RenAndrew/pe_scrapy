#coding:utf-8

import scrapy
from boxing.spider.items import BoxingSpiderItem,BoxingItemHelper

print '----- Loading user_items for user_spiders -----'

# 这些列名已经在系统中存在
_COLUMN_NAMES_ALREADY_HAS = {'filename': '文件名', 
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
   'factory_price': '出厂价'}

#Update column names for user items
#化工-MA库存-周度
BoxingItemHelper.update_column('compare_to_last_week', '环比上周')
BoxingItemHelper.update_column('inv', '库存量')

#化工-MA下游开工-周度
BoxingItemHelper.update_column('operation_rate', '开工率')
BoxingItemHelper.update_column('operation_rate_last_week', '上周开工率')
BoxingItemHelper.update_column('change_compare_to_last_week', '环比涨跌幅')

#化工-MA上游开工-周度
# BoxingItemHelper.update_column('operation_rate', '开工率')   #those are alread exists
# BoxingItemHelper.update_column('operation_rate_last_week', '上周开工率')
# BoxingItemHelper.update_column('compare_to_last_week', '环比上周')
BoxingItemHelper.update_column('operation_rate_last_year', '去年同期')
BoxingItemHelper.update_column('compare_year_on_year', '环比上周')

#化工-MA上游开工-周度 detail
BoxingItemHelper.update_column('region', '区域')
BoxingItemHelper.update_column('productivity', '产能')
BoxingItemHelper.update_column('raw_material', '生产原料')

#PP粉料价格
BoxingItemHelper.update_column('pp_powder_price_low', 'PP粉低端价')
BoxingItemHelper.update_column('pp_powder_price_high', 'PP粉高端价')
BoxingItemHelper.update_column('propene_price_low', '丙烯单体低端价')
BoxingItemHelper.update_column('propene_price_high', '丙烯单体高端价')

#化工-PVC开工-周度
BoxingItemHelper.update_column('province', '省份')
BoxingItemHelper.update_column('producer', '厂家名称')
BoxingItemHelper.update_column('tech_process', '工艺')
BoxingItemHelper.update_column('brand', 'PVC牌号')

#农膜
BoxingItemHelper.update_column('price_shandong', '价格（山东）')
BoxingItemHelper.update_column('price_jiangsu', '价格（江苏）')
BoxingItemHelper.update_column('price_jingjin', '价格（京津）')

#塑料膜
BoxingItemHelper.update_column('increase_daily', '日涨跌')
BoxingItemHelper.update_column('increase_to_last_week', '较上周同期')
BoxingItemHelper.update_column('increase_to_last_month', '较上月同期')
BoxingItemHelper.update_column('increase_to_last_year','较去年同期')

#Oilchem
BoxingItemHelper.update_column('delta_rate','涨跌率')
BoxingItemHelper.update_column('price_market','主流价')
BoxingItemHelper.update_column('price_high','最高价')
# BoxingItemHelper.update_column('region','区域')
BoxingItemHelper.update_column('price_low','最低价')
BoxingItemHelper.update_column('market','市场')


#Base class of User Items
#To override some system settings
class BoxingUserSpiderItem(BoxingSpiderItem):
    @staticmethod
    def get_non_csv_columns():
        return ['filename', 'to_update', 'target_table', 'target_column', 'src_column', 'crawl_time', 'name']

################### For SampleSpider #####################################
class SampleItem(BoxingSpiderItem):
    name = scrapy.Field()
    unit = scrapy.Field()
    cur_price = scrapy.Field()
    week_price = scrapy.Field()
    month_price = scrapy.Field()
    delta = scrapy.Field()


################### For OilchemSpiderTest ###################################
class BaseOilchemItem(BoxingSpiderItem):

    @staticmethod
    def get_type_name():
        raise NotImplementedError('must be overwritten by sub classes')

    @staticmethod
    def get_header_column_headers():
        raise NotImplementedError('must be overwritten by sub classes')


class OilchemItem_User(BaseOilchemItem):
    product_name = scrapy.Field()
    date = scrapy.Field()
    model = scrapy.Field()
    region = scrapy.Field()
    market = scrapy.Field()
    company = scrapy.Field()
    price_low = scrapy.Field()
    price_high = scrapy.Field()
    price_market = scrapy.Field()
    unit = scrapy.Field()
    change = scrapy.Field()
    delta_rate = scrapy.Field()
    remarks = scrapy.Field()

    @staticmethod
    def get_type_name():
        return 'oc_user'

    @staticmethod
    def get_header_column_headers():
        columns = ['product_name', 'date', 'model', 'region', 'market', 'campany', 'price_low', 'price_high', 'price_market', 'unit', 'change', 'delta_rate', 'remarks']
        return [ UserItemHelper.get_cn_column_name(c).decode('utf-8') for c in columns ]

    @staticmethod
    def get_non_csv_columns():
        return ['filename', 'to_update', 'target_table', 'target_column', 'src_column', 'crawl_time', 'name']

class OilchemItem_Iter(BaseOilchemItem):
    product_name = scrapy.Field()
    date = scrapy.Field()
    model = scrapy.Field()
    region = scrapy.Field()
    
    price_type = scrapy.Field()
    low_price = scrapy.Field()
    high_price = scrapy.Field()
    middle_price = scrapy.Field()
    price_in_cny = scrapy.Field()
    unit = scrapy.Field()
    change = scrapy.Field()
    delta_rate = scrapy.Field()
    remarks = scrapy.Field()

    @staticmethod
    def get_type_name():
        return 'oc_inter'

    @staticmethod
    def get_header_column_headers():
        columns = ['product_name', 'date', 'model', 'region', 'campany', 'price_type', 'low_price', 'high_price', \
                    'middle_price', 'unit', 'price_in_cny', 'change', 'delta_rate', 'remarks']
        return [ UserItemHelper.get_cn_column_name(c).decode('utf-8') for c in columns ]

    @staticmethod
    def get_non_csv_columns():
        return ['filename', 'to_update', 'target_table', 'target_column', 'src_column', 'crawl_time', 'name']


class UserItemHelper(object):
    OC1 = 'oc_user'
    OC2 = 'oc_inter'

    @staticmethod
    def get_cn_column_name(en_column):
        return CN_COLUMN_NAMES_USER.get(en_column, en_column)

    @staticmethod
    def get_en_column_name(cn_column):
        return EN_COLUMN_NAMES_USER.get(cn_column)

    @staticmethod
    def get_oilchem_item(spider_name, filename, record, h_type):
        item = None
        if h_type == UserItemHelper.OC1:
            if record['price_low'] != '*':
                item = OilchemItem_User(filename=filename, name=spider_name, product_name=record['product_name'], date=record['date'], model=record['model'], region=record['region'], market=record['market'], company=record['company'], price_low=record['price_low'], price_high=record['price_high'], price_market=record['price_market'], unit=record['unit'], change=record['change'], delta_rate=record['delta_rate'], remarks=record['remarks'] )
        elif h_type == UserItemHelper.OC2:
            if record['price_low'] != '*':
                item = OilchemItem_Iter(filename=filename, name=spider_name, product_name=record['product_name'], \
                  date=record['date'], model=record['model'], region=record['region'], delta_rate=record['delta_rate'],\
                  low_price=record['price_low'], high_price=record['price_high'], middle_price=record['price_mid'], price_type=record['price_type'],\
                  price_in_cny=record['price_cny'], unit=record['unit'], change=record['change'], remarks=record['remarks'] )
        else:
            print '[ERROR] h_type "{}" not implemented'
                    
        return item

################### For SplashSpiderBase ###############################

class Chem99PeSumoPrice(BoxingUserSpiderItem):    	#塑料膜
    product_name = scrapy.Field()
    model = scrapy.Field()        #规格
    price = scrapy.Field()
    increase_daily = scrapy.Field()
    increase_to_last_week = scrapy.Field()
    increase_to_last_month = scrapy.Field()
    increase_to_last_year = scrapy.Field()
    unit = scrapy.Field()

class PeNongmoPrice(BoxingUserSpiderItem):        #农膜
    product_name = scrapy.Field()
    price_shandong = scrapy.Field()
    price_jiangsu = scrapy.Field()
    price_jingjin = scrapy.Field()

#农膜
class Chem99NongmoPrice(BoxingUserSpiderItem):        
    product_name = scrapy.Field()
    price_shandong = scrapy.Field()
    price_jiangsu = scrapy.Field()
    price_jingjin = scrapy.Field()


#化工-MA库存-周度
class Chem99MaInv(BoxingUserSpiderItem):
    product_name = scrapy.Field()
    inv = scrapy.Field()        #库存量
    compare_to_last_week = scrapy.Field() #环比上周
    change = scrapy.Field()        #涨跌幅
    unit = scrapy.Field()

#化工-MA上游开工-周度
class Chem99MaOperationRateUpstreamWeek(BoxingUserSpiderItem):
  operation_rate = scrapy.Field()    #开工率
  operation_rate_last_week = scrapy.Field() #
  compare_to_last_week = scrapy.Field() #环比上周
  operation_rate_last_year = scrapy.Field() #去年同期
  compare_year_on_year = scrapy.Field() #同比
  unit = scrapy.Field()


#化工-MA上游开工-周度 detail
class Chem99MaOperationRateUpstreamDetailWeek(BoxingUserSpiderItem):
  region = scrapy.Field()    #
  company = scrapy.Field() #
  productivity = scrapy.Field() 
  raw_material = scrapy.Field() 
  remarks = scrapy.Field() 
  unit = scrapy.Field()

#化工-MA下游开工-周度
class Chem99MaOperationRateDownstreamWeek(BoxingUserSpiderItem):
  product_name = scrapy.Field()
  operation_rate = scrapy.Field()    #
  operation_rate_last_week = scrapy.Field() #
  change_compare_to_last_week = scrapy.Field()   #涨跌幅

#化工-PVC开工-周度
class Chem99PvcOpRateWeek(BoxingUserSpiderItem):
  area = scrapy.Field()
  province = scrapy.Field()
  producer = scrapy.Field()
  tech_process = scrapy.Field()
  brand = scrapy.Field()
  operation_rate = scrapy.Field()

#PP粉料价格
class Chem99PPPowderPrice(BoxingUserSpiderItem):
  region = scrapy.Field()
  pp_powder_price_low = scrapy.Field()
  pp_powder_price_high = scrapy.Field()
  propene_price_low = scrapy.Field()    #丙烯单体
  propene_price_high = scrapy.Field()

###################Sci 99################################
class Sci99Ldpe(BoxingUserSpiderItem):
  spec = scrapy.Field()
  price = scrapy.Field()
  area = scrapy.Field()
  regoin = scrapy.Field()
  