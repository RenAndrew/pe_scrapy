# -*- coding: utf-8 -*-
import sys
from boxing.spider import SpiderBase, SpiderConfig
from ..util import AutoLoginTool, UrlCrawler, UrlCrawlerConfig

from ..util import get_boxing_table_name_column_name
sys.path.append('/shared/boxing/user_spiders')      #useless in pe_scrapy but for boxing.user_spiders project
from user_items import OilchemItem_User, UserItemHelper
from boxing.spider.items import BoxingItemHelper

class OilchemSpiderUser(SpiderBase):
    """ 爬取隆众价格网上塑料数据，直接调用数据API获取数据，自动登录并利用登录后的cookie获取权限 """

    name = 'oilchem_all'
    start_urls = [
        'http://news.oilchem.net/login.shtml'
    ]

    # SETTINGS = {
    #     'LOG_LEVEL' : 'ERROR',
    # }

    def parse(self, response):
        config = SpiderConfig().get_config('oilchem_user')

        login_tool = AutoLoginTool(config['username'], config['password'])
        logined_cookie = login_tool.submit_login_form(response.headers['Set-Cookie'])

        # real crawler start here
        
        for sub_crawler_info in config['sub_crawlers']:
            sub_spider_name = sub_crawler_info['crawler_name']
            header_type = sub_crawler_info.get('header_type', 'oc_user')
            req_url = sub_crawler_info['data_api_url']

            price_id = sub_crawler_info['price_id']

            crawler_config = UrlCrawlerConfig(sub_crawler_info['price_id'], sub_crawler_info['start_time'], sub_crawler_info['end_time'])
            crawler = UrlCrawler(crawler_config)

            target_table = None
            target_column = None
            src_column = None
            update_info = sub_crawler_info.get('update_info')
            if update_info is not None:
                src_column = UserItemHelper().get_en_column_name(update_info['src_column'].encode('utf-8'))
                target_table = update_info['target_table'].encode('utf-8')
                target_column = update_info['target_column'].encode('utf-8')
                target_table, target_column = get_boxing_table_name_column_name(target_table, target_column)

            records = []
            data_type = sub_crawler_info.get('data_type', 'domestic')
            if data_type == 'domestic':
                records = crawler.download_data(req_url, logined_cookie)
                #break
            elif data_type == 'international':
                #records = crawler.download_data(req_url, logined_cookie, dtype=data_type)
                break
            else:
                print
                print '[ERROR] Unknown data type, please check config.'
                break
            
            for record in records:
                item = UserItemHelper.get_oilchem_item(sub_spider_name, filename=sub_spider_name, record=record, h_type=header_type)
                if item is not None:
                    if target_table is not None or target_column is not None:
                        item['to_update'] = True
                        item['target_table'] = target_table
                        item['target_column'] = target_column
                        item['src_column'] = src_column
                    else:
                        item['to_update'] = False
                    yield item
                else:
                    print
                    print '[ERROR] failed to parse (data)', record