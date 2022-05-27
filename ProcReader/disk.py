#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import time

from collections import OrderedDict

import ProcReader.util as util_utils

from ProcReader.ProcReaderClass import ProcReader
from ProcReader.settings import (DISK_UNIT_LIST, DISK_RATE_LIST,
                                 PROC_DISK_STAT, PROC_FILE_SYST,
                                 DISK_ETC_MTAB, BASE_RATE)


class DiskUsageReader(ProcReader):
    def __init__(self, name='disk_stat'):
        super(DiskUsageReader, self).__init__(name=name)

    def _change_unit(self, value, force_unit=None):
        if force_unit:
            if force_unit in DISK_UNIT_LIST:
                tmp_value = float(
                    value) / DISK_RATE_LIST[DISK_UNIT_LIST.index(force_unit)]
                result = {
                    'volume': round(tmp_value, 2),
                    'unit': force_unit,
                }
                return result
            else:
                result = {
                    'volume': round(value, 2),
                    'unit': 'B',
                }
                return result
        else:
            result = {}
            for unit, rate in zip(DISK_UNIT_LIST, DISK_RATE_LIST):
                tmp_value = float(value) / rate
                if tmp_value >= 1 and tmp_value < BASE_RATE:
                    result = {
                        'volume': round(tmp_value, 2),
                        'unit': unit,
                    }
                    return result
            return result

    def _read_disk_stat(self, dev):
        dev_data = {}
        if dev:
            f = open(PROC_DISK_STAT, 'r')
            for line in f:
                tmp = line.strip().split()
                if tmp[2] in dev:
                    dev_data[tmp[2]] = {}
                    # reads completed
                    dev_data[tmp[2]]['f1'] = float(tmp[3])
                    # reads merged
                    dev_data[tmp[2]]['f2'] = float(tmp[4])
                    # sectors read
                    dev_data[tmp[2]]['f3'] = float(tmp[5])
                    # milliseconds spent reading
                    dev_data[tmp[2]]['f4'] = float(tmp[6])
                    # writes completed
                    dev_data[tmp[2]]['f5'] = float(tmp[7])
                    # writes merged
                    dev_data[tmp[2]]['f6'] = float(tmp[8])
                    # sectors written
                    dev_data[tmp[2]]['f7'] = float(tmp[9])
                    # milliseconds spent writing
                    dev_data[tmp[2]]['f8'] = float(tmp[10])
                    # I/Os currently in progress
                    dev_data[tmp[2]]['f9'] = float(tmp[11])
                    # milliseconds spent doing I/Os
                    dev_data[tmp[2]]['f10'] = float(tmp[12])
                    # weight of milliseconds spent doing I/Os
                    dev_data[tmp[2]]['f11'] = float(tmp[13])
        return dev_data

    def _get_disk_IO(self, dev_list):
        dev_data = {}
        disk_io = {}
        if dev_list:
            for item in dev_list:
                dev_short = item['dev'][item['dev'].rfind('/') + 1:]
                dev_data[dev_short] = {}

            disk_stats_1 = self._read_disk_stat(dev_data)
            time.sleep(1)
            disk_stats_2 = self._read_disk_stat(dev_data)

            for disk in disk_stats_2:
                disk_io[disk] = {}
                disk_io[disk]['rrqm/s'] = disk_stats_2[disk]['f2'] - \
                    disk_stats_1[disk]['f2']
                disk_io[disk]['wrqm/s'] = disk_stats_2[disk]['f6'] - \
                    disk_stats_1[disk]['f6']
                disk_io[disk]['r/s'] = {'volume': disk_stats_2[disk]
                                        ['f1'] - disk_stats_1[disk]['f1'], 'unit': ''}
                disk_io[disk]['w/s'] = {'volume': disk_stats_2[disk]
                                        ['f5'] - disk_stats_1[disk]['f5'], 'unit': ''}
                disk_io[disk]['rsec/s'] = disk_stats_2[disk]['f3'] - \
                    disk_stats_1[disk]['f3']
                disk_io[disk]['wsec/s'] = disk_stats_2[disk]['f7'] - \
                    disk_stats_1[disk]['f7']
                rsec_s = disk_stats_2[disk]['f3'] - disk_stats_1[disk]['f3']
                wsec_s = disk_stats_2[disk]['f7'] - disk_stats_1[disk]['f7']
                disk_io[disk]['rkB/s'] = {'volume': rsec_s *
                                          0.5, 'unit': 'KB/s'}
                disk_io[disk]['wkB/s'] = {'volume': wsec_s *
                                          0.5, 'unit': 'KB/s'}
                disk_io[disk]['avgrq-sz'] = round((disk_io[disk]['rsec/s'] + disk_io[disk]['wsec/s'])/(
                    disk_io[disk]['r/s'] + disk_io[disk]['w/s']), 2)
                disk_io[disk]['avgqu-sz'] = round(
                    disk_stats_2[disk]['f11'] - disk_stats_1[disk]['f11'], 2)
                disk_io[disk]['await'] = round(((disk_stats_2[disk]['f4'] - disk_stats_1[disk]['f4'])+(
                    disk_stats_2[disk]['f8'] - disk_stats_1[disk]['f8']))/(disk_io[disk]['r/s']+disk_io[disk]['w/s']), 2)
                disk_io[disk]['r_await'] = round(
                    (disk_stats_2[disk]['f4'] - disk_stats_1[disk]['f4']) / disk_io[disk]['r/s'], 2)
                disk_io[disk]['w_await'] = round(
                    (disk_stats_2[disk]['f8'] - disk_stats_1[disk]['f8'])/disk_io[disk]['w/s'], 2)
        return disk_io

    def _get_disk_partitions(self, all=False):
        key_list = ['dev', 'mnt', 'fstype']
        phy_devs = []

        f = open(PROC_FILE_SYST, 'r')
        for line in f:
            if not line.startswith('nodev'):
                phy_devs.append(line.strip())

        if 'nfs4' not in phy_devs:
            phy_devs.append('nfs4')
        if 'fuse.glusterfs' not in phy_devs:
            phy_devs.append('fuse.glusterfs')

        ret_list = []
        f = open(DISK_ETC_MTAB, 'r')
        for line in f:
            if not all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phy_devs:
                continue
            if device == 'none':
                device = ''
            ret_list.append(dict(zip(key_list, fields)))
        return ret_list

    def _get_disk_usage(self, path):
        hd = {}
        disk = os.statvfs(path)
        ch_rate = pow(BASE_RATE, 3)
        # Free blocks available to non-super user
        hd['available'] = disk.f_bsize * disk.f_bavail
        # Total number of free blocks
        hd['free'] = disk.f_bsize * disk.f_bfree
        # Total number of blocks in filesystem
        hd['capacity'] = disk.f_bsize * disk.f_blocks
        hd['used'] = float(hd['capacity'] - hd['free'])/hd['capacity']
        return hd

    def get_data(self):
        disk_list = self._get_disk_partitions()
        disk_io = self._get_disk_IO(dev_list)

        total_available = 0
        total_capacity = 0
        total_free = 0

        disk_usage = {}
        for item in disk_list:
            usg = self._get_disk_usage(item['mnt'])

            dev_short = item['dev'][item['dev'].rfind('/') + 1:]
            disk_usage[dev_short] = {}
            disk_usage[dev_short]['mnt'] = item['mnt']
            disk_usage[dev_short]['fstype'] = item['fstype']
            disk_usage[dev_short]['dev'] = item['dev']
            disk_usage[dev_short]['available'] = self._change_unit(
                value=usg['available'], force_unit='GB')
            total_available += disk_usage[dev_short]['available']['volume']

            disk_usage[dev_short]['used'] = round(usg['used'], 4)
            disk_usage[dev_short]['capacity'] = self._change_unit(
                value=usg['capacity'], force_unit='GB')
            total_capacity += disk_usage[dev_short]['capacity']['volume']

            disk_usage[dev_short]['free'] = self._change_unit(
                value=usg['free'], force_unit='GB')
            total_free += disk_usage[dev_short]['free']['volume']

            if dev_short in disk_io:
                disk_usage[dev_short]['io_stat'] = disk_io[dev_short]

        disk_usage['total_available'] = total_available
        disk_usage['total_capacity'] = total_capacity
        disk_usage['total_free'] = total_free

        return disk_usage


# test
if __name__ == '__main__':
    disk = DiskUsageReader()
    util_utils.print_list(disk.get_data())
