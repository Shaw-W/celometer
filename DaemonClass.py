#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
import time
import atexit

from signal import SIGTERM
from collections import OrderedDict

from ProcReader.settings import (DEV_STD_IN, DEV_STD_OUT,
                                 DEV_STD_ERR)


class Daemon(object):
    def __init__(self,
                 pidfile,
                 stdin=DEV_STD_IN,
                 stdout=DEV_STD_OUT,
                 stderr=DEV_STD_ERR):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def delpid(self):
        os.remove(self.pidfile)

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

        sin = open(self.stdin, 'r')
        sout = open(self.stdout, 'a+')
        serr = open(self.stderr, 'a+', 0)

        os.dup2(sin.fileno(), sys.stdin.fileno())
        os.dup2(sout.fileno(), sys.stdout.fileno())
        os.dup2(serr.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid())
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def run(self):
        pass

    def start(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            pid = None

        if pid:
            msg = "pidfile is already exist. Please check Daemon already running or not."
            sys.stderr.write(msg % self.pidfile)
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            msg = "pidfile does not exist. Please check Daemon already running or not."
            sys.stderr.write(msg % self.pidfile)
            return

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.5)
        except OSError as e:
            err = str(e)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(e))
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()


# test
if __name__ == "__main__":
    daemon = Daemon('/tmp/daemon_test.pid')
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            pass
        elif sys.argv[1] == 'stop':
            pass
        elif sys.argv[1] == 'restart':
            pass
        else:
            print('Unknown command')
            sys.exit(2)
    else:
        print('COMMAND: %s start/stop/restart' % sys.argv[0])
        sys.exit(2)
