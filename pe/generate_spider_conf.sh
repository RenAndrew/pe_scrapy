#!/bin/bash

CONF_PATH="./pe/conf"
SPIDER_NAME=$1
CONF_FILE_NAME=${CONF_PATH}/${SPIDER_NAME}.conf

echo "Generating $SPIDER_NAME to conf/$SPIDER_NAME.conf..."

if [ ! -f "${CONF_FILE_NAME}" ]; then
	touch "${CONF_FILE_NAME}"
else
	echo "Configuration already exists!"
	read -p "Do you mean to override it?(y/n)" option
	if [ ${option} = "y" ]; then
		rm -f ${CONF_FILE_NAME}
		echo "Regenerating the configuration..."
	else
		exit 0
	fi
fi

echo "[program:spider_${SPIDER_NAME}]" >> ${CONF_FILE_NAME}
echo "command=/usr/bin/python -m boxing.spider -s ${SPIDER_NAME} -c" >> ${CONF_FILE_NAME}
echo "process_name=%(program_name)s
numprocs=1
directory=/shared/boxing/runtime
umask=022
priority=999
autostart=false
autorestart=false
startsecs=1
startretries=0
exitcodes=0
stopsignal=QUIT
stopwaitsecs=1
user=bruce
stdout_logfile=/shared/boxing/log/spider/%(program_name)s_out.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stdout_events_enabled=false
redirect_stderr=true
stderr_logfile=/shared/boxing/log/spider/%(program_name)s_out.log
serverurl=AUTO" >> ${CONF_FILE_NAME}

echo "Compeleted."