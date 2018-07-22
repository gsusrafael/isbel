#!/usr/bin/env python
__author__ = "Jesus Rafael Sanchez Medrano"

import os
import sys
import errno
import SocketServer
import threading
import XmlConfigParser as xcp

from datetime import datetime
from daemon import Daemon
from XmlValidateDTD import ValidateError, ValidateXML
from SocketService import SocketServiceHandler
from xml.etree import cElementTree as ElementTree #@UnresolvedImport

try:
    try:
        ValidateXML('/etc/isbel.xml', '/etc/isbel.dtd')
        xmltree = ElementTree.parse('/etc/isbel.xml')
    except ValidateError:
        ValidateXML('isbel.xml', 'isbel.dtd')
        xmltree = ElementTree.parse('isbel.xml')
except IOError:
    print "error de validacion"
    sys.exit(1)

configroot = xmltree.getroot()
xmlconfig = xcp.XmlDictConfig(configroot)

# nombre del log de salida
errlogname = xmlconfig['LogConfig']['ErrLogName']

# ruta en donde se almacenaran los logs
logpath = xmlconfig['LogConfig']['LogPath']

# formato de fechas del log
logdateformat = xmlconfig['LogConfig']['LogDateFormat']

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

class SocketDaemon(Daemon):
    def run(self):
        socket_port = int(xmlconfig['SocketConfig']['SocketPort'])
        socket_listen= xmlconfig['SocketConfig']['ListenAddress']
        try:
            socket_server = ThreadedTCPServer((socket_listen, socket_port),
                                               SocketServiceHandler)
            socket_server.timeout = 3

        except IOError:
            datenow = datetime.strftime(datetime.now(), logdateformat)
            msg = 'El puerto esta siendo utilizado por otro servicio'
            sys.stderr.write('[%s] :: %s\n' % (msg, datenow))

        ip, port = socket_server.server_address

        server_thread = threading.Thread(target=socket_server.serve_forever())
        server_thread.setName("SocketDaemon")
        server_thread.setDaemon(True)
        server_thread.start()

    def status(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        try:
            os.kill(pid, 0)
        except OSError, err:
            if err.errno == errno.ESRCH:
                sys.stdout.write("%s Not running\n" % sys.argv[0])
                sys.exit(0)
            elif err.errno == errno.EPERM:
                sys.stdout.write("No permission to signal PID: %d !\n" % pid)
                sys.exit(-1)
            else:
                sys.stdout.write("Unknown error\n")
                sys.exit(-255)
        else:
            sys.stdout.write("%s is running, PID: %d\n" % (sys.argv[0], pid))
            sys.exit(0)

if __name__ == "__main__":
    daemon = SocketDaemon(pidfile='/tmp/SocketDaemon.pid',
                          stderr=logpath + '/' + errlogname)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print "Iniciando %s..." % sys.argv[0]
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print "Deteniendo %s" % sys.argv[0]
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print "Restableciendo %s" % sys.argv[0]
            daemon.restart()
        elif 'status' == sys.argv[1]:
            print "Estado de %s" % sys.argv[0]
            daemon.status()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)
