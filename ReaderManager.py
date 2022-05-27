#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import sys
import time
import json
import socket
import datetime

import ProcReader.util as util_utils

from collections import OrderedDict

from DaemonClass import Daemon
from ProcReader.settings import (MANAGE_PIDFILE, MANAGE_STDIN,
                                 MANAGE_STDOUT, MANAGE_STDERR,
                                 MANAGE_WR_URL)


class ReaderManager(Daemon):
    _intvl = None
    _wr_url = None
    _readersters = OrderedDict()

    def __init__(self,
                 pidfile=MANAGE_PIDFILE,
                 stdin=MANAGE_STDIN,
                 stdout=MANAGE_STDOUT,
                 stderr=MANAGE_STDERR,
                 intvl=10,
                 wr_url=MANAGE_WR_URL):
        super(ReaderManager, self).__init__(pidfile=pidfile,
                                            stdin=stdin, stdout=stdout, stderr=stderr)
        self._wr_url = wr_url

        tmp_str = util_utils.rd_data('%s%s' % (self._wr_url, 'getintvl'))
        if tmp_str:
            self._intvl = int(tmp_str)
        else:
            self._intvl = intvl

        tmp_list = None
        tmp_str = util_utils.rd_data('%s%s' % (self._wr_url, 'getreadersters'))
        if tmp_str:
            tmp_list = eval(tmp_str)
            if type(tmp_list) == type(''):
                tmp_list = eval(tmp_list)
            for reader in tmp_list:
                p_name, cls = util_utils.load_class(reader)
                if p_name and cls:
                    self._readersters[p_name] = cls()
        else:
            self._readersters = OrderedDict()

    def set_intvl(self, intvl):
        if intvl > 1:
            self._intvl = intvl
            util.wr_data('%s%s' % (self._wr_url, 'setintvl'), intvl)
            self.restart()

    def set_readersters(self, readersters):
        reader_list = eval(readersters)
        self._readersters = OrderedDict()
        for reader in reader_list:
            p_name, cls = util_utils.load_class(reader)
            if p_name and cls:
                self._readersters[p_name] = cls()
        util_utils.wr_data('%s%s' %
                           (self._wr_url, 'setreadersters'), readersters)
        self.restart()

    def _reader(self):
        reader_data = OrderedDict()
        if self._readersters:
            for readerster in self._readersters:
                reader_data[readerster] = {}
                reader_data[readerster]['timestamp'] = time.asctime(
                    time.localtime())
                reader_data[readerster]['data'] = self._readersters[readerster].get_data()
        return reader_data

    def run(self):
        cnt = 0
        while True:
            wr_obj = {}
            try:
                wr_obj['data'] = self._reader()
                wr_obj['timestamp'] = time.asctime(time.localtime())
                wr_obj['hostname'] = socket.gethostname()
                wr_obj['ip_address'] = socket.gethostbyname(wr_obj['hostname'])
            except socket.gaierror as e:
                wr_obj['ip_address'] = ''
            finally:
                util_utils.wr_data('%s%s' % (self._wr_url, 'setdata'), wr_obj)
                time.sleep(self._intvl)
                cnt += 1


if __name__ == '__main__':
    daemon = ReaderManager()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            daemon.start()
        elif sys.argv[1] == 'stop':
            daemon.stop()
        elif sys.argv[1] == 'restart':
            daemon.restart()
        else:
            print('Unknown command')
            sys.exit(2)
    elif len(sys.argv) == 3:
        if sys.argv[1] == 'setintvl':
            if re.match(r'^-?\d+$', sys.argv[2]) or re.match(r'^-?(\.\d+|\d+(\.\d+)?)', sys.argv[2]):
                daemon.set_intvl(int(sys.argv[2]))
                print('Set interval: %s' % sys.argv[2])
        elif sys.argv[1] == 'setreader':
            reader_list = None
            try:
                reader_list = eval(sys.argv[2])
            except:
                print('%s is not a list.' % sys.argv[2])
            if reader_list:
                daemon.set_readersters(sys.argv[2])
    else:
        print('USAGE: %s start/stop/restart' % sys.argv[0])
        sys.exit(2)
