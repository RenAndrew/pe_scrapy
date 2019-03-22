# -*- coding: utf-8 -*-

def html_table_parsing(table_html):
	head, tbody, tail = strip_head_tail(table_html)

	tab_rows, max_col = cut_rows(tbody)

	tab_matrix = []
	slots = [0 for x in range(0,max_col)]

	for i in range(0,len(tab_rows)):
		row = tab_rows[i]
		data_row = []
		cur_idx = 0		#row's index
		for j in range(0,max_col):
			if slots[j] > 0:	#slot is not empty, must copy the above cell in the table, that is row span operation
				data_row.append(tab_matrix[i-1][j])
				slots[j] = slots[j] - 1
				
			else:
				data_row.append(row[cur_idx][0])
				if row[cur_idx][1]:		#there is row span set
					slots[j] = row[cur_idx][1] - 1
				cur_idx += 1
			# print data_row[j],' '
		tab_matrix.append(data_row)

	return tab_matrix

def strip_head_tail(thtml):
	ph1 = thtml.find('tbody')
	if ph1 == -1:
		return None
	ph2 = thtml.find('>', ph1)
	if ph2 == -1:
		return None

	head = thtml[0:ph2+1]

	table_body = thtml[ph2+1:]
	ptail = table_body.find('</tbody')

	if ptail == -1:
		return (head, table_body, None)

	tail = table_body[ptail:]
	table_body = table_body[0:ptail]

	return (head, table_body, tail)

def cut_rows(tbody):
	tr_rows = []
	max_col_num = 0
	while(len(tbody) != 0):
		pBeg1 = tbody.find('<tr')
		if pBeg1 == -1:
			break;
		pBeg2 = tbody.find('>', pBeg1)
		if pBeg2 == -1:
			print "unclosed <tr>"
			break;
		pEnd1 = tbody.find('</tr')
		if pEnd1 == -1:
			print "unclosed <tr>"
			break;
		pEnd2 = tbody.find('>', pEnd1)

		row = tbody[pBeg2+1:pEnd1]
		tbody = tbody[pEnd2+1:]

		row_tds = cut_tds(row)
		tr_rows.append(row_tds)
		if len(row_tds) > max_col_num:
			max_col_num = len(row_tds)
		# max_col_num += 1

		# print cut_tds(row)
		# print '---------'
		# if max_col_num > 3:
		# 	break;
	return (tr_rows,max_col_num)

def cut_tds(row):
	tds = []
	while (len(row) != 0):
		rowspan_v = None
		colspan_v = 1	#default span is once
		pBeg1 = row.find('<td')
		if pBeg1 == -1:
			break;
		pBeg2 = row.find('>', pBeg1)
		if pBeg2 == -1:
			print "unclosed <td>"
			break;
		# get the rowspan & colspan value
		pRowSpan = row.find('rowspan', pBeg1, pBeg2)
		if pRowSpan != -1:
			attr = row[pRowSpan : pBeg2]
			rowspan_v = int(attr.split('=')[1].strip().strip('\"'))

		pColSpan = row.find('colspan', pBeg1, pBeg2)
		if pColSpan != -1:
			attr = row[pColSpan : pBeg2]
			colspan_v = int(attr.split('=')[1].strip().strip('\"'))
			
		pEnd1 = row.find('</td')
		if pEnd1 == -1:
			print "unclosed <td>"
			break;
		pEnd2 = row.find('>', pEnd1)
		td_content = row[pBeg2+1 : pEnd1].strip()
		row = row[pEnd2+1:]

		while colspan_v > 0:
			colspan_v = colspan_v - 1
			tds.append(  (td_content, rowspan_v)  )		#if both rowspan and colspan is set on this td, what happend?

	return tds