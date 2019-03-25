# -*- coding: utf-8 -*-

#化工-MA下游开工-周度
import copy
from splash_base import SplashSpiderBase
from user_items import Chem99MaOperationRateDownstreamWeek
from ..util import html_table_parsing

def filter_op_down(field):
	if field == u'化工':
		return False
	else:
		return True

def filter_title(field):
	if not u'年' in field:
		return False
	else:
		return True

class Chem99MaOpDownstreamWeek(SplashSpiderBase):
	name = 'chem99_ma_op_down'

	SEARCH_API_META = {
		"keyword" : "甲醇下游周度开工率统计",
		"sccid" : 0,
		"filter" : {
			"field" : "WebSite",
			"method" : filter_op_down
		}
	}

	LOGIN_TYPE = 'CHEM_LOGIN'

	# DEBUG_URL = 'http://chem.chem99.com/news/30417097.html'

	def parse_page(self, response):
		print '====================> parse chem99_ma_op_downstream_week'

		html_tab = response.css('#PanelContent table').extract_first()
		table = html_table_parsing(html_tab)

		filename_map = {
			1 : 'MTO_MTP',
			2 : 'Jiaquan',	#甲醛
			3 : 'Erjiami',	#二甲醚
			4 : 'MTBE',
			5 : 'Cusuan',	#醋酸
			6 : 'Jiasuoquan',	#甲缩醛
			7 : 'DMF',
			8 : 'ALL'
		}

		try:
			for i in range(1,8):

				item = Chem99MaOperationRateDownstreamWeek()
				item['product_name'] = self.clean_tags(table[0][i])
				item['operation_rate'] = self.clean_tags(table[1][i])
				item['operation_rate_last_week'] = self.clean_tags(table[2][i])
				item['change_compare_to_last_week'] = self.clean_tags(table[3][i])

				item['name'] = self.name
				item['filename'] = filename_map[i]
				item['date'] = self.get_date_from_meta_info(response.url)


				item_all = copy.deepcopy(item)
				item_all['filename'] = filename_map[8]
				
				yield item
				yield item_all
		except Exception as e:
			print '-' * 50
			print 'Error in parsing ' + response.url 
			print e
			print '-' * 50
		print '=' * 40