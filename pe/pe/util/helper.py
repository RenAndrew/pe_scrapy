import datetime

import pandas

from boxing.view.structures import ClassInfo

available_tables = []
for sector_name, sector_info in ClassInfo().get_info().items():
    for product_name, product_info in sector_info.items():
        available_tables.extend(list(product_info[0]))
        available_tables.extend(list(product_info[1]))

cn_table_2_en_table = {}
for table in available_tables:
    cn_table_name = ClassInfo().get_desc(table)
    if isinstance(cn_table_name, unicode):
        cn_table_name = cn_table_name.encode('utf-8')
    cn_table_2_en_table[cn_table_name] = table


def get_boxing_table_name_column_name(cn_table_name, cn_col_name):
    try:
        if isinstance(cn_table_name, unicode):
            cn_table_name = cn_table_name.encode('utf-8')
        if isinstance(cn_col_name, unicode):
            cn_col_name = cn_col_name.encode('utf-8')
        table_name = cn_table_2_en_table[cn_table_name]
        col_details = ClassInfo().get_detail(table_name)
        cn_col_2_en_col = {info['desc'].encode('utf-8') if isinstance(info['desc'], unicode) else info['desc']: c for c, info in col_details.items()}
        column_name = cn_col_2_en_col[cn_col_name]
    except KeyError as e:
        print '[ERROR] key not found while processing (table){} (col){} (e)'.format(cn_table_name, cn_col_name) + (e.message or '')
        return None, None

    return table_name, column_name


def to_date_type(x):
    date = None

    if isinstance(x, pandas.Timestamp):
        date = x.to_pydatetime()

    elif isinstance(x, datetime.datetime):
        date = x.date()

    elif isinstance(x, datetime.date):
        date = x

    elif isinstance(x, (str, unicode)):
        try:
            date = datetime.datetime.strptime(x, '%Y-%m-%d').date()
        except:
            date = datetime.datetime.strptime(x, '%Y-%m-%d %H%M%S').date()

    return date
