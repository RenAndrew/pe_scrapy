# -*- coding: utf-8 -*-
import sys, time
import traceback
from boxing.spider import SpiderBase, SpiderConfig
from ..util import AutoLoginTool, UrlCrawler, UrlCrawlerConfig,SeleniumLogin

from ..util import get_boxing_table_name_column_name
from ..post_process import AutoUploader
sys.path.append('/shared/boxing/user_spiders')      #useless in pe_scrapy but for boxing.user_spiders project
from user_items import OilchemItem_User, UserItemHelper
from boxing.spider.items import BoxingItemHelper

class OilchemSpiderUser(SpiderBase):
    """ 爬取隆众价格网上塑料数据，直接调用数据API获取数据，自动登录并利用登录后的cookie获取权限 """

    name = 'oilchem_pvc'
    start_urls = [
        'http://news.oilchem.net/login.shtml'   # this is fake
    ]

    CONFIG_NAME = "oilchem_pvc"

    def get_allowed_set(self, debug_sub_crawlers):
        self._is_debug_mode = False
        allowed_crawler_set = set()
        if debug_sub_crawlers is not None:
            debug_mode = debug_sub_crawlers.get("switch")
            if debug_mode == "on":
                allowed_crawler_set = set(debug_sub_crawlers["debug_sub_crawler_list"])
                print "In debuging..."
                self._is_debug_mode = True
        return allowed_crawler_set

    def parse(self, response):
        config = SpiderConfig().get_config(self.CONFIG_NAME)

        login_tool = SeleniumLogin(config['username'], config['password'])
        logined_cookie = login_tool.selelogin()

        # real crawler start here
        allowed_crawler_set = self.get_allowed_set(config.get('debug_sub_crawlers'))
        
        for sub_crawler_info in config['sub_crawlers']:
            sub_spider_name = sub_crawler_info['crawler_name']
            # if self._is_debug_mode and sub_spider_name not in allowed_crawler_set:
            if sub_spider_name not in allowed_crawler_set:
                continue

            header_type = sub_crawler_info.get('header_type', 'oc_user')
            req_url = sub_crawler_info['data_api_url']
            price_id = sub_crawler_info['price_id']

            if config.get('global_time_override'):
                print 'Gloabl time take effect!'
                crawler_config = UrlCrawlerConfig(sub_crawler_info['price_id'], config['global_start_time'], \
                                              config['global_end_time'], sub_crawler_info['crawler_name'])
            else:
                crawler_config = UrlCrawlerConfig(sub_crawler_info['price_id'], sub_crawler_info['start_time'], \
                                              sub_crawler_info['end_time'], sub_crawler_info['crawler_name'])
            crawler = UrlCrawler(crawler_config)

            print '$' * 80
            print 'Start crawling : %s' % crawler_config.crawler_name
            print 'Date range: %s to %s' % (crawler_config.start_time, crawler_config.end_time)

            # target_table = None
            # target_column = None
            # src_column = None
            # update_info = sub_crawler_info.get('update_info')
            # if update_info is not None:
            #     src_column = UserItemHelper().get_en_column_name(update_info['src_column'].encode('utf-8'))
            #     target_table = update_info['target_table'].encode('utf-8')
            #     target_column = update_info['target_column'].encode('utf-8')
            #     target_table, target_column = get_boxing_table_name_column_name(target_table, target_column)

            records = []
            data_type = sub_crawler_info.get('data_type', 'domestic')
            try:
                records = crawler.download_data(req_url, logined_cookie, dtype=data_type)
            except KeyError:
                print
                print '[ERROR] Unknown data type, please check config.'
            except:
                print
                print traceback.format_exc()
                print '[ERROR] Unknown error while crawling, quiting.'

            print '$' * 80
            
            for record in records:
                item = UserItemHelper.get_oilchem_item(sub_spider_name, filename=sub_spider_name, \
                                                        record=record, h_type=header_type)
                if item is not None:
                    # if target_table is not None or target_column is not None:
                    #     item['to_update'] = True
                    #     item['target_table'] = target_table
                    #     item['target_column'] = target_column
                    #     item['src_column'] = src_column
                    # else:
                    #     item['to_update'] = False
                    item['to_update'] = False
                    yield item
                else:
                    print
                    print '[ERROR] failed to parse (data)', record

        #After all item are yield, yield a fake item to generate a fake file as a compelete flag to indicate the post process to start up.
        yield self._generate_compelete_flag()

    def _generate_compelete_flag(self):
        time.sleep(1)   #making sure all the records are fully written to files.
        #generating fake record
        from datetime import datetime,date
        ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        dt = date.today().strftime("%Y-%m-%d")
        flag_file_name = self.CONFIG_NAME + "_compeleted_flag_" + ts
        print flag_file_name
        self.compelete_flag = flag_file_name + '_' + dt + '.csv'

        fake_record = {"date":"*", "product_name":"*","model":"*","region":"*","company_name":"*","quote_price":"999",
                        "unit":"*","change":"*","delta_rate":"*","remarks":"*"}
        fake_item = UserItemHelper.get_oilchem_item("flag_spider", filename=flag_file_name, record=fake_record, h_type="oc_company")
        fake_item['to_update'] = False
        return fake_item

    def closed(self, reason):
        print self.name, reason
        print '$' * 100
        print "Starting to uploading data..."
        crawler_name = self.CONFIG_NAME

        AutoUploader(crawler_name).wait_until_dumping_finished(self.compelete_flag)\
                                  .process_results(crawler_name)\
                                  .upload_excel()