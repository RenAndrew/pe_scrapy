# -*- coding: utf-8 -*-
from datetime import date, datetime
import time

class TimeKit:

	@staticmethod
	def str_to_date(date_str, fmt='%Y-%m-%d'):
		time_tuple = time.strptime(date_str, fmt)

		year, month, day = time_tuple[:3]

		return date(year, month, day)

	@staticmethod
	def date_to_str(dt, fmt='%Y-%m-%d'):
		dt_str = fmt.replace('Y', 's').replace('m', 's').replace('d', 's') 
		dt_str = dt_str % (dt.year, TimeKit.time_stringify(dt.month), TimeKit.time_stringify(dt.day))
		return dt_str

	@staticmethod
	def time_stringify(int_val):
		str_val = str(int_val)
		if len(str_val) == 1:
			str_val = '0' + str_val
		return str_val

	@staticmethod
	def max_date(date_list_in_str, fmt='%Y-%m-%d'):
		if len(date_list_in_str) == 0:
			return None

		max_date = TimeKit.str_to_date(date_list_in_str[0], fmt)

		for i in range(1, len(date_list_in_str)):
			dt = TimeKit.str_to_date(date_list_in_str[i])
			if dt > max_date:
				max_date = dt

		return TimeKit.date_to_str(max_date)