# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  String,Column,Integer

#checkset是每个数据表的唯一索引字段（dt，也就是日期）的集合，
#用于对已经存在的数据进行去重，保证使用追加方式添加数据时，数据不重复
class DbChecksetMaker(object):
	def __init__(self, ip, username, password, port=3306, db="boxing"):
		self._user = username
		self._passwd = password
		self._ip = ip
		self._port = port
		self._db = db

	def set_connect_info(self, ip, port=3306, db="boxing"):
		self._ip = ip
		self._port = port
		self._db = db

	def make_checkset(self, table_name):
		conn_str = "mysql+pymysql://{}:{}@{}:{}/{}"\
						.format(self._user, self._passwd, self._ip, self._port,self._db)
		mysql_engine = create_engine(conn_str)

		MysqlSession = sessionmaker(bind=mysql_engine)

		db_session = MysqlSession()

		#选择表中去重后的日期列表
		query_sql = "select distinct dt from {};".format(table_name)
		result_set = db_session.execute(query_sql).fetchall()

		date_checkset = set()

		for row in result_set:
			date_checkset.add(str(row[0]))		#datetime to string type

		print date_checkset

		db_session.close()

		return date_checkset

if __name__ == '__main__':
	checkset_maker = DbChecksetMaker('localhost', 'boxing', 'taurus123')
	# checkset_maker.set_connect_info('localhost')

	checkset_maker.make_checkset('ma_cn_cargo_price_daily')
