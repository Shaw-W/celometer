#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import traceback

import ProcReader.util as util_utils

from ProcReader.ProcReaderClass import ProcReader
from ProcReader.settings import PROC_LOAD_STAT


class LoadStatReader(ProcReader):
    def __init__(self, name='load_stat'):
        super(LoadStatReader, self).__init__(name=name)

    def get_data(self):
        load_stat = {}
        load_info = None
        f = None

        try:
            if util_utils.is_exist(PROC_LOAD_STAT):
                f = open(PROC_LOAD_STAT)
                load_info = f.read().split()
                if load_info and len(load_info) == 5:
                    load_stat['load_1_min'] = {
                        'volume': float(load_info[0]), 'unit': ''}
                    load_stat['load_5_min'] = {
                        'volume': float(load_info[1]), 'unit': ''}
                    load_stat['load_15_min'] = {
                        'volume': float(load_info[2]), 'unit': ''}
                    load_stat['thread_num'] = load_info[3]
                    load_stat['last_pid'] = load_info[4]
        except Exception as e:
            print('LoadStatReader Unexpected Error Occured: ' +
                  str(traceback.print_exc()))
        finally:
            if f:
                f.close()
            return load_stat


# test
if __name__ == "__main__":
    load = LoadStatReader()
    util_utils.print_list(load.get_data())
