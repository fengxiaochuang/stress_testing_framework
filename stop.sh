ps -ef |grep import |grep -v grep|awk '{print $2}'|xargs kill -9
