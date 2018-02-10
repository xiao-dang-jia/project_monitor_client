# 使用说明：

## 1. 启动方法:(常驻进程)

nohup python main.py &

### 2. 前置安装流程

注意: 得用2.7环境, apscheduler 不支持2.6了

1. 首先安装python2.7，建议使用virtualenv
2. 安装python2 及其相关依赖包
   pip install apscheduler
   yum install MySQL-python
   pip install paramiko
   pip install psycopg2
3. 为了可以使用 iostat：yum -y install sysstat
4. 在main.py 中配置 "监控配置数据库信息"：

例子:
host_ip = 'xxxx.xxxx.xxxx.xxxx'
db_nick = 'xxxx'
username = 'xxxx'
password = 'xxxx'
port = 'xxxx'
database = 'xxxx' # 这个是数据库名 很重要
API_URL = 'XXXXXXXXX' # API接口地址

5. 初始化客户端配置数据表

0_initialisation_configure_db.sql

notes:

- 需要配置表的表名是一致的
- 字段命名是一致的

### 3. 代码架构 

SaaS化监控脚本 客户端由6部分模块组成:

1. main.py
2. configure.py
3. initialisation.py
4. class.py
5. scheduler.py
6. api.py

#### 功能

1. main.py
   程序入口
2. configure.py
   读取数据库配置
3. initialisation.py
   初始化 next_checktime
4. monitor_class.py
   监控方法的具体实现
5. scheduler.py
   监控任务的调度
6. api.py
   API接口
