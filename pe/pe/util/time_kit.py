# -*- coding: utf-8 -*-
from datetime import date, datetime
import time

class TimeKit:

	@staticmethod
	def str_to_date(date_str, fmt='%Y-%m-%d'):
		time_tuple = time.strptime(date_str, fmt)

		year, month, day = time_tuple[:3]

		return date(year, month, day)