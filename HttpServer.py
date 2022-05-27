#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import time
import json
import subprocess
import threading

from datetime import datetime
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

from ProcReader.settings import (READER_PATH, READERS_LIST)


def not_insance_address_string(self):
    host, port = self.client_address[:2]
    return '%s (no getfqdn)' % host


BaseHTTPRequestHandler.address_string = not_insance_address_string


class Handler(BaseHTTPRequestHandler):
    content = {}
    intvl = 10
    ts_get = ''
    reader_path = READER_PATH
    readersters = READERS_LIST

    def do_GET(self):
        args_str = 'python %s/ReaderManager.py restart' % (Handler.reader_path)
        if self.path == '/getdata':
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            Handler.ts_get = time.asctime(time.localtime())

            t_content = datetime.strptime(
                Handler.content['timestamp'], "%a %b %d %H:%M:%S %Y")
            t_last_get = datetime.strptime(
                Handler.ts_get, "%a %b %d %H:%M:%S %Y")

            if (t_last_get - t_content).seconds < 60:
                Handler.content['status'] = 'NORMAL'
            else:
                Handler.content['status'] = 'READERING_TIMEOUT'
                Handler.content['data'] = {}
                ping_Popen = subprocess.Popen(args=args_str, shell=True)
            obj_str = json.dumps(Handler.content)
            self.send_header("Content-Length", str(len(obj_str)))
            self.end_headers()
            self.wfile.write(obj_str.encode())
            self.wfile.write('\n')
        elif self.path == '/getintvl':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(Handler.intvl)
            self.wfile.write('\n')
        elif self.path == '/getreadersters':
            self.send_response(200)
            self.send_header("Content-Length", "text/json")
            reader_str = json.dumps(Handler.readersters)
            self.send_header("Content-Length", str(len(reader_str)))
            self.end_headers()
            self.wfile.write(reader_str.encode())
            self.wfile.write('\n')
        elif self.path == '/rstsvr':
            ping_Popen = subprocess.Popen(args=args_str, shell=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write('Restart server OK!')
            self.wfile.write('\n')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/setdata':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.content = eval(data.encode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.content))
            self.write.write('\n')
        elif self.path == '/setintvl1':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.intvl = eval(data.encode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.intvl))
            self.write.write('\n')
        elif self.path == '/setreadersters':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.readersters = eval(data.decode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.readersters))
            self.wfile.write('\n')
        else:
            self.send_response(404)
            self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


if __name__ == '__main__':
    server = None
    try:
        server = ThreadedHTTPServer(('0.0.0.0', '8655'), Handler)
        if sys.argv[1]:
            Handler.reader_path = sys.argv[1]
        print('Starting server, use <Ctrl-C> to stop')
        server.serve_forever()
    except Exception as e:
        if server:
            server.socket.close()
