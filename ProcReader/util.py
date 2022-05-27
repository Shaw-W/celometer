#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import json
import importlib
import urllib.request as urllibReq
import urllib.error as urllibError


def is_exist(filename):
    return os.path.exists(filename)


def print_list(obj_list):
    json_str = json.dumps(obj_list, indent=1)
    print(json_str)


def append_file(content, filename):
    if len(content) != 0:
        output = open(filename, 'a')
        output.write(content)
        output.close()
        return True
    else:
        return False


def load_class(cls_name):
    cls = None
    bse_name = None
    try:
        r = cls_name.rfind('.')
        dft_name = "__main__"
        bse_name = cls_name
        if r > 0:
            dft_name = cls_name[0:r]
            bse_name = cls_name[r+1:]
        mod = importlib.import_module(dft_name)
        cls = getattr(mod, bse_name)
    except:
        return None
    finally:
        return bse_name, cls


def update_conf(conf_name, params):
    w_str = ''
    output = None
    if params:
        for p in params:
            w_str += '%s=%s\n' % (p, params[p])
    if w_str:
        try:
            output = open(conf_name, 'w')
            output.write(w_str)
        except Exception as e:
            print('update conf error')
        finally:
            if output:
                output.close()


def rd_data(url):
    res = None
    try:
        req = urllibReq.Request(url)
        res = urllibReq.urlopen(req, timeout=5)
        return res.read()
    except urllibError.URLError as e:
        print(e.reason)
        return False
    except urllibError.HTTPError as e:
        print(e.code)
        return False
    finally:
        if res:
            res.code()


def wr_data(url, obj):
    data = json.dumps(obj)
    res = None
    try:
        req = urllibReq.Request(
            url, data, {'Content-Type': 'application/json'})
        res = urllibReq.urlopen(req, timeout=5)
        return res.read()
    except urllibError.URLError as e:
        print(e.reason)
        return False
    except urllibError.HTTPError as e:
        print(e.reason)
        return False
    finally:
        if res:
            res.close()
