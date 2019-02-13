# -*- coding: utf-8 -*-

import os
import time
from collections import defaultdict
from datetime import date, datetime

from scrapy.exporters import CsvItemExporter

from items import BoxingItemHelper


class PePipeline(object):
	def __init__(self):
		self.outfile = open('price_output.dat', 'w+')

	def process_item(self, item, spider):
		print item
		
		self.outfile.write(str(item))
		self.outfile.write('\n')
		return item


class BoxingCsvItemExporter(CsvItemExporter):

    def _write_headers_and_set_fields_to_export(self, item):
        if self.include_headers_line:
            if not self.fields_to_export:
                if isinstance(item, dict):
                    # for dicts try using fields of the first item
                    self.fields_to_export = item.keys()
                else:
                    # use fields declared in Item
                    self.fields_to_export = item.fields.keys()
                for column in type(item).get_non_csv_columns():
                    if column in self.fields_to_export:
                        self.fields_to_export.remove(column)
                cn_col_header = [BoxingItemHelper.get_cn_column_name(col) for col in self.fields_to_export]
            row = list(self._build_row(cn_col_header))
            self.csv_writer.writerow(row)


class BasicPipeline(object):

    def process_item(self, item, spider):
        item['crawl_time'] = datetime.now()
        return item

class CsvDumpPipeline(object):

    def open_spider(self, spider):
        # self.result_folder = os.path.join(spider.settings['result_folder'], spider.name)
        self.result_folder = os.path.join('./', spider.name)
        if not os.path.exists(self.result_folder):
            os.makedirs(self.result_folder)
        self.files = {}
        self.exporters = {}

    def close_spider(self, spider):
        for _, exporter in self.exporters.items():
            exporter.finish_exporting()
        for _, file in self.files.items():
            file.write('\n')
            file.close()

    def process_item(self, item, spider):
        file_id = item['filename']
        if file_id not in self.files:
            file_path = os.path.join(self.result_folder, file_id + '_' + str(date.today()) + '.csv')
            self.files[file_id] = open(file_path, 'a+b')
            self.exporters[file_id] = BoxingCsvItemExporter(self.files[file_id])
            self.exporters[file_id].start_exporting()
        self.exporters[file_id].export_item(item)
        return item
