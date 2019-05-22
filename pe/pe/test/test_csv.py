# -*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import os

path = './pe/work/csv/oilchem_ma/2019-05-18/'
file = 'MA华南_2019-05-18.csv'
print path + file

data=pd.read_csv(path+file)

# print data[data['日期'] in set(['2019-05-17'])]

# is_in_dates = ( data['日期'].values in set(['2019-05-17']) )

# print data.query('日期 before 2019-05-01')

# date_not_allowed = {'date': ['2018-05-18', '2018-05-21'],
# 					'nothing' : ['', '']}

# dt_not_allowed = DataFrame(date_not_allowed).set_index('date')

# data = data.rename(columns = {u'日期':'date'})

# print data.head()

# except_dates_list = list(data['日期'])
# print except_dates_list
# except_dates_list.remove('2019-05-16')

# df = data[data['日期'].isin(except_dates_list)]

# df = DataFrame(data, columns=['日期', 'price_market'])

df = DataFrame()
df["date"] = data['日期']
df['price_market'] = data["price_market"]

df =df.set_index('date')

df.drop(['2019-05-15', '2019-05-16', '2019-05-30'], inplace=True, errors='ignore')
print df.head(20)