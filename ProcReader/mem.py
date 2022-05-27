#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import traceback

from collections import OrderedDict

import ProcReader.util as util_utils

from ProcReader.ProcReaderClass import ProcReader
from ProcReader.settings import (BASE_RATE, PROC_MEM_INFO,
                                 MEM_RATE_LIST, MEM_UNIT_LIST)


class MemInfoReader(ProcReader):
    def __init__(self, name='mem_info'):
        super(MemInfoReader, self).__init__(name=name)

    def _change_unit(self, value, force_unit=None):
        if force_unit:
            if force_unit in MEM_UNIT_LIST:
                tmp_value = float(value) / \
                    MEM_RATE_LIST[MEM_UNIT_LIST.index(force_unit)]
                result = {
                    'volume': round(tmp_value, 2),
                    'unit': force_unit,
                }
                return result
            else:
                result = {
                    'volume': round(value, 2),
                    'unit': 'KB',
                }
                return result
        else:
            result = {}
            for unit, rate in zip(MEM_UNIT_LIST, MEM_RATE_LIST):
                tmp_value = float(value) / rate
                if ((tmp_value >= 0 and tmp_value < BASE_RATE) or
                        (MEM_UNIT_LIST.index(unit) == len(MEM_UNIT_LIST)-1)):
                    result = {
                        'volume': round(tmp_value, 2),
                        'unit': unit,
                    }
                    return result
            return result

    def get_data(self):
        mem_info = OrderedDict()
        try:
            if util_utils.is_exist(PROC_MEM_INFO):
                with open(PROC_MEM_INFO) as f:
                    for line in f:
                        tmp = line.split(':')
                        if len(tmp) == 2:
                            volume_unit = tmp[1].strip().split(' ')
                            if len(volume_unit) == 2:
                                tmp_value = self._change_unit(
                                    value=(volume_unit[0]), force_unit='MB')
                            elif len(volume_unit) == 1:
                                tmp_value = {
                                    'volume': (volume_unit[0]),
                                    'unit': '',
                                }
                            mem_info[tmp[0].strip()] = tmp_value
        except Exception as e:
            print('MemInfoReader Unexpected Error Occured: ' +
                  str(traceback.print_exc()))
        finally:
            return mem_info


# test
if __name__ == "__main__":
    mem_info = MemInfoReader()
    util_utils.print_list(mem_info.get_data())
