#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import time
import traceback
from collections import OrderedDict

import ProcReader.util as util_utils

from ProcReader.ProcReaderClass import ProcReader
from ProcReader.settings import PROC_CPU_INFO, PROC_CPU_STAT


class CPUInfoReader(ProcReader):
    def __init__(self, name='cpu_info'):
        super(CPUInfoReader, self).__init__(name=name)

    def get_data(self):
        cpu_info = OrderedDict()
        proc_info = OrderedDict()
        nprocs = 0

        try:
            if util_utils.is_exist(PROC_CPU_INFO):
                with open(PROC_CPU_INFO) as f:
                    for line in f:
                        if not line.strip():
                            cpu_info['proc%s' % nprocs] = proc_info
                            nprocs += 1
                            proc_info = OrderedDict()
                        else:
                            if len(line.split(':')) == 2:
                                proc_info[line.split(':')[0].strip()] = line.split(':')[
                                    1].strip()
                            else:
                                proc_info[line.split(':')[0].strip()] = ''
        except Exception as e:
            print('CPUInfoReader Unexpected Error Occured: ' +
                  str(traceback.print_exc()))
        finally:
            return cpu_info


class CPUUsageReader(ProcReader):
    def __init__(self, name='cpu_info'):
        super(CPUUsageReader, self).__init__(name=name)

    def _read_proc_stat(self):
        cpu_line = OrderedDict()
        f = None
        try:
            if util_utils.is_exist(PROC_CPU_STAT):
                f = open(PROC_CPU_STAT)
                lines = f.readlines()
                for line in lines:
                    if line.startswith('cpu'):
                        tmp = line.strip().split()
                        cpu_line[tmp[0]] = tmp[1:len(tmp)]
        except Exception as e:
            print('CPUUsageReader Trace back error: ' +
                  str(traceback.print_exc()))
        finally:
            if f:
                f.close()
            return cpu_line

    def get_data(self):
        cpu_usage = {}
        total_1 = {}
        idle_1 = {}
        total_2 = {}
        idle_2 = {}

        cpu_line_1 = self._read_proc_stat()
        if cpu_line_1:
            for item in cpu_line_1:
                total_1[item] = float(cpu_line_1[item][0]) + float(cpu_line_1[item][1]) + \
                    float(cpu_line_1[item][2]) + float(cpu_line_1[item][3]) + \
                    float(cpu_line_1[item][4]) + float(cpu_line_1[item][5]) + \
                    float(cpu_line_1[item][6])
                idle_1[item] = float(cpu_line_1[item][3])

        time.sleep(1)

        cpu_line_2 = self._read_proc_stat()
        if cpu_line_2:
            for item in cpu_line_2:
                total_2[item] = float(cpu_line_2[item][0]) + float(cpu_line_2[item][1]) + \
                    float(cpu_line_2[item][2]) + float(cpu_line_2[item][3]) + \
                    float(cpu_line_2[item][4]) + float(cpu_line_2[item][5]) + \
                    float(cpu_line_2[item][6])
                idle_2[item] = float(cpu_line_2[item][3])

        if total_1 and total_2:
            for item in total_1:
                # ((t2 - t1) - (i2 - i1)) / (t2 - t1) * 100
                cpu_usage[item] = {
                    'volume': round(100 * (float(total_2[item] - total_1[item]) - float(idle_2[item] - idle_1[item])) / float(total_2[item] - total_1[item])),
                    'unit': '%',
                }

        return cpu_usage


# test
if __name__ == '__main__':
    cpu_info = CPUInfoReader()
    util_utils.print_list(cpu_info.get_data())

    cpu_usage = CPUUsageReader()
    util_utils.print_list(cpu_usage.get_data())
