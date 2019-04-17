#!/bin/bash

SCRAPY_SRC_HOME_PATH='/home/ren/work/git_repos/pe_scrapy/pe'

BOXING_USER_SPIDER_PATH='/shared/boxing/user_spiders'

echo `date "+%Y-%m-%d %H:%M:%S"`
echo 'Copying py files from '$SCRAPY_SRC_HOME_PATH' to '$BOXING_USER_SPIDER_PATH

if [ ! -d "$BOXING_USER_SPIDER_PATH/spiders" ]; then
	mkdir -p $BOXING_USER_SPIDER_PATH/spiders
fi

if [ ! -d "$BOXING_USER_SPIDER_PATH/util" ]; then
	mkdir -p $BOXING_USER_SPIDER_PATH/util
fi

#copy util
cp $SCRAPY_SRC_HOME_PATH/pe/util/*.py $BOXING_USER_SPIDER_PATH/util/
#cp $SCRAPY_SRC_HOME_PATH/pe/spiders_import.py $BOXING_USER_SPIDER_PATH/__init__.py #deprecated

cp $SCRAPY_SRC_HOME_PATH/pe/spiders/__init__.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/splash_base.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_ma_inv.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_ma_op_downstream.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_ma_op_upstream.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_pp_powder_price.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_pvc.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_nongmo.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/chem99_pe.py $BOXING_USER_SPIDER_PATH/spiders/
cp $SCRAPY_SRC_HOME_PATH/pe/spiders/sci99_ldpe_renewed.py $BOXING_USER_SPIDER_PATH/spiders/


cp $SCRAPY_SRC_HOME_PATH/user_spider_root/*	$BOXING_USER_SPIDER_PATH/

