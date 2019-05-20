# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  String,Column,Integer


engine = create_engine("mysql+pymysql://boxing:taurus123@localhost:3306/boxing")

Session = sessionmaker(bind=engine)

session = Session()

result_set = session.execute("select distinct dt from ma_cn_cargo_price_daily;").fetchall()

print type(result_set)
print len(result_set)
print result_set

dt_set = set()

for row in result_set:
	dt_set.add(str(row[0]))

print dt_set