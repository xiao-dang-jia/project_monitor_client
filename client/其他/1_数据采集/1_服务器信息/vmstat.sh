##################################################
vmstat
##################################################

procs -----------memory---------- ---swap-- -----io---- --system-- -----cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 0  0      0 32169004 171280 231396    0    0     0     0    3    3  0  0 100  0  0

####
#### cs + us 的占比
vmstat|awk 'NR==3 {print $13+$14"%"}'
####

####
#### free cpu
vmstat|awk 'NR==3 {print $4/1024"MB"}'
####

# 日志中需要获取这三个：m_dim	m_value	m_logger
示例: cpu_usage 0 xxxx

####
#### 设备使用率
iostat -dx|awk 'BEGIN{max=0} {if($14+0>max+0) max=$14} END{print max"%"}'

#### IOPS bandwidth


1.

2.

3. API数据 - 有数据时，脚本直接插入该数据进入数据库。


