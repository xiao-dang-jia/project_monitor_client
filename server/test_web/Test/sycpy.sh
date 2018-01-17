echo "选择需要备份文件的项目："
read projectname
mkdir $projectname
cp -i ../$projectname/views.py  ./$projectname/views.py
cp -i ../$projectname/admin.py  ./$projectname/admin.py
cp -i ../$projectname/models.py  ./$projectname/models.py
cp -i ../$projectname/urls.py  ./$projectname/urls.py
