#!/bin/bash
curTime=`date +%Y%m%d_%H%M%S `
web_basicdir='/root/pythonproject/test_web'
mkdir -p $curTime
echo "请输入需要更新的应用名："
read project_name
if [ -d "$web_basicdir//$project_name//" ];then
	echo "已找到$project_name项目"
	mkdir $curTime/$project_name
	cp -i $web_basicdir/$project_name/* ./$curTime/$project_name/
	echo "备份成功"
	#cp -i $web_baicdir//Test//$project_name/ .py $web_basicdir/$project_name/
	cp -i ./$project_name/urls.py  /root/pythonproject/test_web/$project_name/
	cp -i ./$project_name/views.py  /root/pythonproject/test_web/$project_name/
	cp -i ./$project_name/models.py  /root/pythonproject/test_web/$project_name/
	cp -i ./$project_name/admin.py  /root/pythonproject/test_web/$project_name/
	echo "上传成功"
	
else
	echo "未找到该项目"
	rmdir -p $curTime
fi
