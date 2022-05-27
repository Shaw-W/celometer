#!/bin/bash

workspace=$(cd `dirname $0`; pwd)

# Stop readering
PID_reader=`ps -ef | grep ReaderManager.py | grep -v grep | awk '{print $2}'`
if [ -n "$PID_reader" ]
then
    python ${workspace}/ReaderManager.py stop
    echo "Stop Reading task done"
fi

ps -ef | grep HttpServer.py | grep -v grep | awk '{print $ 2}' | xargs kill

if [ -f "/tmp/httpsvr.log" ]; then
    rm /tmp/httpsvr.log
fi

echo "Stop HttpServer done"

nohup python ${workspace}/HttpServer.py ${workspace} > /tmp/httpsvr.log 2>&1 &
echo "Start HttpServer done"

sleep .5

python ${workspace}/ReaderManager.py start
python ${workspace}/ReaderManager.py setintvl 10
python ${workspace}/ReaderManager.py setreader "['ProcReader.cpu.CPUUsageReader', 'ProcReader.mem.MemInfoReader', 'ProcReader.load.LoadStatReader', 'ProcReader.disk.DiskUsageReader', 'ProcReader.net.NetStatReader', 'ProcReader.uptime.UptimeReader']"
echo "Start Reading task done"
