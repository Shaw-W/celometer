#!/usr/bin/env python
# -*- encoding: utf-8 -*-

BASE_RATE = 1024

# cpu.py
PROC_CPU_INFO = '/proc/cpuinfo'
PROC_CPU_STAT = '/proc/stat'

# disk.py
PROC_DISK_STAT = '/proc/diskstats'
PROC_FILE_SYST = '/proc/filesystems'
DISK_UNIT_LIST = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
DISK_RATE_LIST = (
    pow(BASE_RATE, 0), pow(BASE_RATE, 1),
    pow(BASE_RATE, 2), pow(BASE_RATE, 3),
    pow(BASE_RATE, 4), pow(BASE_RATE, 5),
)
DISK_ETC_MTAB = '/etc/mtab'

# load.py
PROC_LOAD_STAT = '/proc/loadavg'

# mem.py
PROC_MEM_INFO = '/proc/meminfo'
MEM_UNIT_LIST = ('KB', 'MB', 'GB')
MEM_RATE_LIST = (
    pow(BASE_RATE, 0), pow(BASE_RATE, 1),
    pow(BASE_RATE, 2),
)

# net.py
PROC_NET_DEV = '/proc/net/dev'

# uptime.py
PROC_UPTIME_INFO = '/proc/uptime'

# daemon.py
DEV_STD_IN = '/dev/stdin'
DEV_STD_OUT = '/dev/stdout'
DEV_STD_ERR = '/dev/stderr'

# httpserver.py
READER_PATH = '/usr/local/procagent'
READERS_LIST = [
    'ProcReader.cpu.CPUUsageReader',
    'ProcReader.mem.MemInfoReader',
    'ProcReader.load.LoadStatReader',
    'ProcReader.disk.DiskUsageReader',
    'ProcReader.net.NetStatReader',
    'ProcReader.uptime.UptimeReader',
]

# readermanager.py
MANAGE_PIDFILE = '/tmp/readercls.pid'
MANAGE_STDIN = '/dev/null'
MANAGE_STDOUT = '/dev/null'
MANAGE_STDERR = '/dev/null'
MANAGE_WR_URL = 'http://127.0.0.1:8655/'
