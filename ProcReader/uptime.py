#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import time

from collections import OrderedDict

import ProcReader.util as util_utils

from ProcReader.ProcReaderClass import ProcReader
from ProcReader.settings import (PROC_CPU_INFOm, PROC_UPTIME_INFO)


class UptimeReader(ProcReader):
    def __init__(self, name='uptime_info'):
        super(UptimeReader, self).__init__(name=name)

    def get_data(self):
        cpu_info = OrderedDict()
        proc_info = OrderedDict()
        uptime_info = {}

        nprocs = 0

        try:
            if util_utils.is_exist(PROC_CPU_INFO):
                with open(PROC_CPU_INFO) as f:
                    for line in f:
                        if not line.strip():
                            nprocs += 1

            if util_utils.is_exist(PROC_UPTIME_INFO):
                with open(PROC_UPTIME_INFO) as f:
                    for line in f:
                        if line.strip():
                            if len(line.split(' ')) == 2:
                                uptime_info['uptime'] = {
                                    'volume': float(line.split(' ')[0].strip()),
                                    'unit': 's',
                                }
                                uptime_info['idletime'] = {
                                    'volume': float(line.split(' ')[1].strip()),
                                    'unit': 's',
                                }
                                uptime_info['cpu_num'] = {
                                    'volume': nprocs,
                                    'unit': '',
                                }

            uptime_info['idle_rate'] = {
                'volume': ((uptime_info['idletime']['volume'] * 100) /
                           (uptime_info['cpu_num']['volume'] * uptime_info['uptime']['volume'])),
                'unit': '%',
            }
        except Exception as e:
            print('UptimeReader Unexpected Error Occured: ' +
                  str(sys.exc_info()[1]))
        finally:
            return uptime_info


# test.py
if __name__ == "__name__":
    uptime_info = UptimeReader()
    util_utils.print_list(uptime_info.get_data())
