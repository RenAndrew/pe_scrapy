# -*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import os
import traceback
from openpyxl import Workbook

from boxing.spider import SpiderConfig

from db_checkset import DbChecksetMaker

#Build the excel upload file from csv files which are crawlered by oilchem spider
class ExcelBuilder(object):
	CSV_PATH='../work'
	# CSV_PATH='../work/MA_test'

	def __init__(self, config_name='oilchem_ma', csv_path='../work', xls_outdir='../work/out'):
		config = SpiderConfig().get_config(config_name)
		self._extract_column_reference(config['sub_crawlers'])
		self.config_name = config_name
		self.config = config

		self.CSV_PATH = csv_path
		self.XLS_OUTDIR = xls_outdir
		if not os.path.exists(self.XLS_OUTDIR):
			os.makedirs(self.XLS_OUTDIR)

		self._checkset = None

	def check_before(self, checkset):
		self._checkset = checkset
		return self

	def build(self):
		file = self.join_csv_files()\
				   .attach_lacking_columns()\
				   .store_as_xlsx()

		return file

	def remove_before_latest_date(self, csvdata):
		if self._checkset is not None and self._checkset.get('max_date') is not None:
			latest_date = self._checkset.get('max_date')
			csvdata = csvdata[csvdata['日期'] > latest_date]
			return csvdata
		else:
			return csvdata

	def remove_dates_exists_in_db(self, csvdata):
		if self._checkset is not None and self._checkset.get('check_list') is not None:
			check_list = self._checkset.get('check_list')
			return csvdata.drop(check_list, inplace=True, errors='ignore') #ignore errors when element does not exists
		else:
			return csvdata


	def generate_dataframe_from(self, csv_file_with_path, crawler_name):
		print csv_file_with_path
		rawdata = pd.read_csv(csv_file_with_path)
		rawdata = self.remove_before_latest_date(rawdata)
		frame = DataFrame()	#emtpy frame

		frame['日期'] = rawdata['日期']
		columns_needed = self.column_ref_tab.get(crawler_name)
		if columns_needed is not None and len(columns_needed) > 0:
			# Add needed column(s) and rename column name
			for i in range(0, len(columns_needed)):
				used_column = columns_needed[i]['used_column']
				column_rename = columns_needed[i]['renamed_as']
				frame[column_rename] = rawdata[used_column]
		else:
			print ('No column needed of %s!' % crawler_name)
			print ('Could you please check the config? ')
			print ('-' * 50)

		frame = frame.set_index('日期')

		return self.remove_dates_exists_in_db(frame)


	def join_csv_files(self):
		data_by_date = {}	#collect each date of data
		
		print ('Included files: ')
		for csv_file in os.listdir(self.CSV_PATH):
			if not os.path.isfile(os.path.join(self.CSV_PATH, csv_file)):
				continue
			try:
				crawler_name, date_tag = self._file_name_parser(csv_file)
			except:
				print traceback.format_exc()
				continue
			print crawler_name
			# print date_tag
			csv_file_with_path = os.path.join(self.CSV_PATH, csv_file)
			frame = self.generate_dataframe_from(csv_file_with_path, crawler_name)
			
			if data_by_date.get(date_tag) is None:	#First data frame, directly add
				data_by_date[date_tag] = frame
			else:
				data_by_date[date_tag] = data_by_date[date_tag].join(frame)	#join two frame at the index field

		self.df_list_by_date = data_by_date

		return self

	#The lacking columns are those the crawler does not fetch but the upload program requires
	#just make those columns empty and attach to the table
	def attach_lacking_columns(self):
		lacking_columns = self.config.get('lacking_columns')

		if lacking_columns is None:
			return

		for date_tag, df in self.df_list_by_date.items():
			empty_content_columns = {
				'日期' : df.index.values
			}
			for column in lacking_columns:
				column = column.encode('utf-8')
				empty_content_columns[column] = ['' for i in range(0, len(df.index))]

			frame_of_lacking_columns = DataFrame(empty_content_columns).set_index('日期')
			# print frame_of_lacking_columns.ix[:10]
			self.df_list_by_date[date_tag] = self.df_list_by_date[date_tag].join(frame_of_lacking_columns)

		return self

	#for debug
	def _store_df(self, df, filename):
		filename = os.path.join(self.XLS_OUTDIR, filename)

		wb = Workbook()
		sh = wb.active

		header = ['日期'] + list(df)
		sh.append(header)

		for index, row in df.iterrows():
			xls_row = [index] + list(row)
			sh.append(xls_row)
			
		wb.save(filename = filename)

	def store_as_xlsx(self):
		if self.df_list_by_date is None:
			return False

		filename_templ = os.path.join(self.XLS_OUTDIR, self.config_name)

		for date_tag, df in self.df_list_by_date.items():
			filename_with_date = (filename_templ+ '_' + date_tag + '.xlsx')
			print "Output to %s" % filename_with_date
			workbook = Workbook()
			sheet1 = workbook.active
			sheet1.title = self.config_name

			# header = ['日期'] + df.columns.values.tolist()
			header = ['日期'] + list(df)
			sheet1.append(header)

			for index, row in df.iterrows():
				xls_row = [index] + list(row)
				sheet1.append(xls_row)
				
			workbook.save(filename = filename_with_date)
			workbook.close()

		return True

	def _file_name_parser(self, file_name):
		suffix = file_name.split('.')[1]
		if suffix != "csv":
			raise Exception("%s is not csv file!" % file_name)
		p1 = file_name.rfind('_')
		crawler_name = file_name[:p1]
		date_tag = file_name[p1+1:].split('.')[0]

		return (crawler_name, date_tag)

	def _extract_column_reference(self, sub_crawlers):
		self.column_ref_tab = {}
		for sub_crawler in sub_crawlers:
			used_data_columns = sub_crawler.get('used_data_columns')
			columns_needed = []
			is_first_nameless = True
			for src_column in used_data_columns:
				if type(src_column) == type({}):
					columns_needed.append({"used_column" : src_column['used_column'].encode('utf-8'),\
										   "renamed_as" : src_column['renamed_as'].encode('utf-8')})	#All encode to ascii
				else:
					if is_first_nameless:
						renamed_as = sub_crawler['crawler_name'].encode('utf-8')
						is_first_nameless = False
					else:
						renamed_as = src_column.encode('utf-8')

					columns_needed.append({"used_column" : src_column.encode('utf-8'),\
										   "renamed_as" : renamed_as})

			self.column_ref_tab[sub_crawler['crawler_name'].encode('utf-8')] = columns_needed



if __name__ == '__main__':
	# csv_combiner = ExcelBuilder(csv_path='../work/MA_test')
	#csv_combiner = ExcelBuilder(xls_outdir='../work/temp')
	csv_combiner = ExcelBuilder(csv_path='./pe/work/csv/oilchem_ma/2019-05-17', xls_outdir='./pe/work/')
	csv_combiner.join_csv_files()
	print '-' * 80
	csv_combiner.attach_lacking_columns()
	csv_combiner.store_as_xlsx()