#!/bin/bash

SCRAPY_SRC_HOME_PATH='/home/ren/work/git_repos/pe_scrapy/pe'

BOXING_USER_SPIDER_PATH='/shared/boxing/user_spiders'

echo `date "+%Y-%m-%d %H:%M:%S"`
echo 'Copying py files from '$SCRAPY_SRC_HOME_PATH' to '$BOXING_USER_SPIDER_PATH

cp $SCRAPY_SRC_HOME_PATH/pe/util/*.py $BOXING_USER_SPIDER_PATH/util/

cp $SCRAPY_SRC_HOME_PATH/pe/spiders/splash_base.py $BOXING_USER_SPIDER_PATH/spiders/