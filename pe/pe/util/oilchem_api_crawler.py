# encoding=utf-8
import json
import sys,os
import tempfile
import time
import urllib
import urllib2
import zlib  # for gzip decompression
import demjson

class UrlCrawlerConfig:
    def __init__(self, price_id, start_time, end_time, crawler_name):
        self.price_id = price_id
        self.start_time = self._translate_date(start_time)
        self.end_time = self._translate_date(end_time)
        self.crawler_name = crawler_name
        # self.specification = specification #new version of oilchem descarded this field.

    #support easy date format
    def _translate_date(self, easy_date):
        if easy_date.find('-') != -1:   #date in standard format, like '2019-1-25'
            return easy_date
        if easy_date == 'today':
            return self._ago()
        if easy_date == 'lastweek':
            return self._ago(days=7)
        if easy_date == 'lastmonth':
            return self._ago(months=1)
        if easy_date == 'lastyear':
            return self._ago(years=1)

        unit_map = {
                'Y' : 0,
                'm' : 0,
                'd' : 0
            }
        slices = easy_date.split('_')
        for date_unit in slices:
            delta, unit = '', ''
            for i in range(0, len(date_unit)):
                if date_unit[i].isdigit():
                    delta += date_unit[i]
                else:
                    if len(delta) < 1:
                        raise Exception("Ileagal date expression!")
                    delta = int(delta)
                    unit = date_unit[i]
                    if unit_map.get(unit) == None:
                        raise Exception("Invalid unit in date expression(%s)!" % unit)
                    unit_map[unit] = delta
                    break

        return self._ago(years=unit_map['Y'], months=unit_map['m'], days=unit_map['d'])

    #get date of some days/months/years ago
    def _ago(self, years=0, months=0, days=0):
        assert (years>=0 and months>=0 and days>=0), ("Only date before today is meaningful!") 
        from datetime import date, timedelta
        date_today = date.today()
        year, month, day = date_today.year, date_today.month, date_today.day
        year = year - years
        month = month - months
        while month <= 0:
            month += 12
            year -= 1

        date_ago = date(year, month, day) - timedelta(days=days)
        return date_ago.strftime("%Y-%m-%d")

class UrlCrawler(object):
    def __init__(self, config):
        self.config = config
        self.unqiue_set = {}
        self.DATATYPE_FIELD_MAPPINGS = {
            "domestic" : {
                "indexDate"         : "date",
                "varietiesName"     : "product_name",
                "specificationsName": "model",
                # "standard" : "",
                "regionName"        : "region",
                "internalMarketName": "market",
                "memberAbbreviation": "company",
                "lprice"            : "price_low",
                "gprice"            : "price_high",
                "indexValue"        : "price_market",
                "unitValuationName" : "unit",
                "riseOrFallSum"     : "change",
                "riseOrFallRate"    : "delta_rate",
                "remark"            : "remarks"
            },
            "international" : {
                "indexDate"          : "date",
                "varietiesName"      : "product_name",
                "specificationsName" : "model",
                "customRegion"       : "region",
                "priceTypeName"      : "price_type",
                "lprice"             : "price_low",
                "gprice"             : "price_high",
                "indexValue"         : "price_mid",
                "unitValuationName"  : "unit",
                "rprice"             : "price_cny",
                "riseOrFallSum"      : "change",
                "riseOrFallRate"     : "delta_rate",
                "remark"             : "remarks"
            },
            "company" : {
                "indexDate"         : "date",
                "varietiesName"     : "product_name",
                "specificationsName": "model",
                "regionName"        : "region",
                "memberAbbreviation": "company_name",
                # "memberName"        : "comany_fullname",
                "indexValue"        : "quote_price",
                "unitValuationName" : "unit",
                "riseOrFallSum"     : "change",
                "riseOrFallRate"    : "delta_rate",
                "remark"            : "remarks"
            }
        }

    def _get_headers(self, cookie):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36',
            'cookie': cookie
        }

        return headers

    def _get_post_body(self, page, page_size):
        body = {
            'id' : self.config.price_id,
            'startTime' : self.config.start_time,
            'endTime' : self.config.end_time,
            'timeType' : 0,
            'pageNum' : page,
            'pageSize' : page_size,
        }

        return urllib.urlencode(body)

    def _req_data(self, req_url, headers, page_size, page_idx):
        if (page_idx < 1 or page_idx > page_size):
            raise "Incorrect page number " + str(page_idx)

        body = self._get_post_body(page_idx, page_size)
        req = urllib2.Request(req_url, headers=headers, data=body)
        response = urllib2.urlopen(req)

        return demjson.decode(response.read())  # the data is in raw javascript format, not json, convert it to json (python object).

    def download_data(self, req_url, cookie, dtype='domestic'):
        mapping_tab = self.DATATYPE_FIELD_MAPPINGS[dtype]   #if not allowed datatype, it throws KeyError excetpion
        print "Data type: %s" % (dtype)  

        page_idx = 1
        page_size = 100
        headers = self._get_headers(cookie)
        data = self._req_data(req_url, headers, page_size, page_idx)  # get the first page of data
        
        num_pages = data.get('pages')
        # num_pages = data['pageInfo'].get('lastPage')
        # print num_pages
        # print data.get('total')
        # print data.get('pages')
        if num_pages is None:
            print 'Data format error!'
            raise Exception("Data format error!")
        
        records = self._extract_items(data, mapping_tab)
        for i in range(2, num_pages+1):
            data = self._req_data(req_url, headers, page_size, i)
            records = records + self._extract_items(data, mapping_tab)
    
        print 'finished downloading data for: ' + req_url
        print "Totally %d unique items." % len(self.unqiue_set)
        self.unqiue_set = {}    #clear the history of download
        return records

    def _extract_items(self, jsonData, mapping_tab):
        rows = jsonData['pageInfo']['list']
        records = []
        for item in rows:
            record = {}
            if not self._is_unique(item['indexDate']):      #if the item exists already!
                continue
            for origin_field, target_field in mapping_tab.items():
                # print target_field, origin_field
                # print item[origin_field]
                record[target_field] = item[origin_field]
            records.append(record)

        return records

    #any index_date checked by _is_unique will be recorded then it is never unique
    def _is_unique(self, index_date):
        if self.unqiue_set.get(index_date):
            print '*********** Get Duplicated items!!! (%s) ***********' % index_date
            return False
        else:
            self.unqiue_set[index_date] = True
            return True

