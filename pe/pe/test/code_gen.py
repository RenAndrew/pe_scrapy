# -*- coding: utf-8 -*-
import os
import json
from PIL import Image

if __name__ == '__main__':
	code_value_dict = None
	with open('pe/code_test_result.json', 'r') as jfile:
		json_content = jfile.read()
		print json_content
		code_value_dict = json.loads(json_content)
		print type(code_value_dict)

	codeImgFilePath = '/home/ren/work/git_repos/pe_scrapy/pe/pe/work/oilchem/'

	img_list = os.listdir(codeImgFilePath)

	for i in range(0, len(img_list)):
		print '$' * 100
		file_name = img_list[i]
		file_path = os.path.join(codeImgFilePath, img_list[i])

		if not os.path.isfile(file_path):
			continue

		fp = open(file_path, 'rb')
		im = Image.open(fp)
		im.show()
		code_key = file_name.split('.')[0]
		code_value = code_value_dict.get(code_key)
		print code_key
		if code_value is not None:	
			print code_value
			confirm = raw_input('Is code value correct?(y/N) ')
			if confirm == "y":
				print '===================>'
				fp.close()
				continue

		code_value = raw_input('Please input the code value: ')
		code_value_dict[code_key] = code_value
		fp.close()

	with open('pe/code_test_result.json', 'w') as jfile:
		json_content = json.dumps(code_value_dict)
		jfile.write(json_content)

	pause = raw_input('Input Ctrl+C to close all pictures.')