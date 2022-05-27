#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import time

from collections import OrderedDict

import ProcReader.util as util_utils

from ProcReader.ProcReaderClass import ProcReader
from ProcReader.settings import PROC_NET_DEV


class NetStatReader(ProcReader):
    def __init__(self, name='net_stat'):
        super(NetStatReader, self).__init__(name=name)

    def _get_net_data(self):
        net_stat = OrderedDict()
        title_dict = OrderedDict()
        total_item = 0

        # try:
        if util_utils.is_exist(PROC_NET_DEV):
            with open(PROC_NET_DEV) as f:
                for line in f:
                    if line.strip().startswith('Inter'):
                        tmp = line.strip().split('|')
                        for i in range(1, len(tmp)):
                            title_dict[tmp[i].strip()] = []
                    elif line.strip().startswith('face'):
                        tmp = line.strip().split('|')
                        for i in range(1, len(tmp)):
                            title_dict[title_dict.items()[i-1][0]
                                       ] = tmp[i].strip().split()
                            total_item += len(title_dict.items()[i-1][i])
                    else:
                        tmp_data = OrderedDict()
                        tmp = line.strip().split(':')

                        value = tmp[1].strip().split()
                        if len(value) == total_item:
                            cnt = 0
                            for t_item in title_dict.items():
                                tmp_data[t_item[0]] = {}
                                for i_t in t_item[1]:
                                    tmp_data[t_item[0]][i_t] = value[cnt]
                                    cnt += 1
                        else:
                            print('NetStatReader num of items Error Occured!')
                        net_stat[tmp[0]] = tmp_data

        total_data = {
            'net_bytes_in': 0,
            'net_bytes_out': 0,
            'net_pkts_in': 0,
            'net_pkts_out': 0,
        }

        for key, value in net_stat.items():
            if key.startwith('eth'):
                total_data['net_bytes_in'] += int(
                    value['Receive']['bytes'])
                total_data['net_bytes_out'] += int(
                    value['Transmit']['bytes'])
                total_data['net_pkts_in'] += int(
                    value['Receive']['packets'])
                total_data['net_pkts_out'] += int(
                    value['Transmit']['packets'])
        # except Exception as e:
        #     print('NetStatReader Unexpected Error Occured: ' +
        #           str(sys.exc_info()[1]))
        # finally:
        return net_stat, total_data

    def get_data(self):
        net_state_1, total_data_1 = self._get_net_data()
        time.sleep(0.5)
        net_state_2, total_data_2 = self._get_net_data()

        flow_data = {}
        flow_data['net_bytes_in'] = {
            'volume': int((total_data_2['net_bytes_in'] - total_data_1['net_bytes_in'])/intvl),
            'unit': 'B/s',
        }
        flow_data['net_bytes_out'] = {
            'volume': int((total_data_2['net_bytes_out'] - total_data_1['net_bytes_out'])/intvl),
            'unit': 'B/s',
        }
        flow_data['net_pkts_in'] = {
            'volume': int((total_data_2['net_pkts_in'] - total_data_1['net_pkts_in'])/intvl),
            'unit': 'p/s',
        }
        flow_data['net_pkts_out'] = {
            'volume': int((total_data_2['net_pkts_out'] - total_data_1['net_pkts_out'])/intvl),
            'unit': 'p/s',
        }
        flow_data['net_bytes_in_sum'] = {
            'volume': int(total_data_2['net_bytes_in']),
            'unit': 'B',
        }
        flow_data['net_bytes_out_sum'] = {
            'volume': int(total_data_2['net_bytes_out']),
            'unit': 'B',
        }
        return flow_data


# test.py
if __name__ == '__main__':
    net_stat = NetStatReader()
    net_stat.get_data()
