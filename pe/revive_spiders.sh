#!/bin/bash

./cp_to_boxing.sh
/usr/bin/supervisorctl -c /opt/boxing/etc/supervisor/supervisord.conf update

systemctl restart boxing