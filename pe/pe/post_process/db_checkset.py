# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  String,Column,Integer

from boxing import DatabaseConfig

#checkset是每个数据表的唯一索引字段（dt，也就是日期）的集合，
#用于对已经存在的数据进行去重，保证使用追加方式添加数据时，数据不重复
class DbChecksetMaker(object):
	def __init__(self):

		self._conn_str_data = DatabaseConfig().db_conn_str_data

	# def __init__(self, ip, username, password, port=3306, db="boxing"):
	# 	self._user = username
	# 	self._passwd = password
	# 	self._ip = ip
	# 	self._port = port
	# 	self._db = db

	# def set_connect_info(self, ip, port=3306, db="boxing"):
	# 	self._ip = ip
	# 	self._port = port
	# 	self._db = db

	def make_checkset(self, table_name, check_type='date_list'):
		# conn_str = "mysql+pymysql://{}:{}@{}:{}/{}"\
		# 				.format(self._user, self._passwd, self._ip, self._port,self._db)
		mysql_engine = create_engine(self._conn_str_data)

		MysqlSession = sessionmaker(bind=mysql_engine)

		db_session = MysqlSession()

		date_checkset = {
			'max_date' : None,
			'check_list' : None
		}
		if check_type == 'date_list':
			#选择表中去重后的日期列表
			query_sql = "select distinct dt from {};".format(table_name)
			result_set = db_session.execute(query_sql).fetchall()

			date_list = []
			for row in result_set:
				date_list.append(str(row[0]))	#datetime to string type

			date_checkset['check_list'] = date_list
		elif check_type == 'max_date':
			query_sql = "select max(dt) from {};".format(table_name)
			result_set = db_session.execute(query_sql).fetchall()

			for row in result_set:
				date_checkset['max_date'] = str(row[0])	#datetime to string type

		print date_checkset

		db_session.close()

		return date_checkset

if __name__ == '__main__':
	checkset_maker = DbChecksetMaker()
	# checkset_maker.set_connect_info('localhost')

	checkset_maker.make_checkset('ma_cn_cargo_price_daily', 'max_date')

