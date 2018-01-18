#!/bin/bash
. ../virtual_activate
echo -e "请输入需要同步的model所在的app名称：（取消，请按ctrl+c）"
read App_name
echo -e "开始同步..."
python manage.py makemigrations $App_name
python manage.py migrate
echo -e "再次检查"
python manage.py migrate
echo -e "同步结束"
