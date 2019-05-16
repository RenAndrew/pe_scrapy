#!/bin/bash

RESULT_SRC_PATH='/home/ren/work/git_repos/pe_scrapy/pe/result'

RESULT_DST_PATH='/home/ren/boxing/result_bak'

echo `date "+%Y-%m-%d %H:%M:%S"`
echo 'Moving data files from '$RESULT_SRC_PATH' to '$RESULT_DST_PATH

for folder in $RESULT_SRC_PATH/*; do
	if [ `ls $folder | wc -l` -eq 0 ]; then	#empty folder
		continue
	fi
	for file in $folder/*; do
		# echo $file
		timestamp=`echo ${file##*_} | cut -d '.' -f1`
		# echo $timestamp
		if [ ! -d ${RESULT_DST_PATH}/${timestamp} ]; then
			mkdir -p ${RESULT_DST_PATH}/${timestamp}
		fi

		mv $file ${RESULT_DST_PATH}/${timestamp}/
		# mv -r $folder/
	done
	# echo $folder
	echo "Moving $folder"
	echo '----------------------'
done