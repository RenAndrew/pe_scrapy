# -*- coding: utf-8 -*-

#化工-MA上游开工-周度
from splash_base import SplashSpiderBase

from user_items import Chem99MaOperationRateUpstreamWeek,Chem99MaOperationRateUpstreamDetailWeek

from ..util import html_table_parsing

def filter_title(field):
	if not u'年' in field:
		return False
	else:
		return True

class Chem99MaOpUpstreamWeek(SplashSpiderBase):
	name = 'chem99_ma_op_up'

	SEARCH_API_META = {
		"keyword" : "国内甲醇装置有效开工率",
		"sccid" : 0,
		"filter" : {
			"field" : "Title",
			"method" : filter_title
		}
	}

	LOGIN_TYPE = 'CHEM_LOGIN'

	# DEBUG_URL = 'http://chem.chem99.com/news/30417035.html'

	def parse_page(self, response):
		print '====================> parse chem99_ma_operation_rate_upstream'

		try:
			html_tabs = response.css('#PanelContent table').extract()

			table_op_rate = html_table_parsing(html_tabs[0])   #开工率
			table_detail_productivity = html_table_parsing(html_tabs[1])	#国内部分甲醇装置变动情况

			for i in range(1,3):
				item = Chem99MaOperationRateUpstreamWeek()
				item['operation_rate'] = self.clean_tags(table_op_rate[1][i])
				item['operation_rate_last_week'] = self.clean_tags(table_op_rate[2][i])
				item['compare_to_last_week'] = self.clean_tags(table_op_rate[3][i])
				item['operation_rate_last_year'] = self.clean_tags(table_op_rate[4][i])
				item['compare_year_on_year'] = self.clean_tags(table_op_rate[5][i])
				
				item['name'] = self.name
				item['unit'] = '%'
				item['date'] = self.get_date_from_meta_info(response.url)

				if i == 1: 		#全国开工率
					item['filename'] = 'China_MA_operation_rate_weekly'
				else:		#西北开工率
					item['filename'] = 'Nortwest_China_MA_operation_rate_weekly'

				yield item

			for i in range(1, len(table_detail_productivity)):
				item = Chem99MaOperationRateUpstreamDetailWeek()
				row = table_detail_productivity[i]

				item['region'] = self.clean_tags(row[0])
				item['company'] = self.clean_tags(row[1])
				item['productivity'] = self.clean_tags(row[2])
				item['raw_material'] = self.clean_tags(row[3])
				item['remarks'] = self.clean_tags(row[4])
				item['unit'] =  u'万吨'
				item['date'] = self.get_date_from_meta_info(response.url)
				item['filename'] = 'Ma_operation_rate_detail_weekly'

				yield item
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print e
			print '-' * 50
		print '=' * 40