ps -ef |grep django |grep -v grep | awk '{print $2}'|xargs kill
