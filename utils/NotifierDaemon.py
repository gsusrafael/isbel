#!/usr/bin/env python
'''
Created on 26/07/2010

@author: jesus
'''

import sys
import DirectoryNotifier
from daemon import Daemon

class NotifierDaemon(Daemon):
    def run(self):
        conjunto_hilos = [] # Arreglo para contener conjunto de hilos 
        for i in range(10):
            hilo = DirectoryNotifier.DirectoryWorkerNotifier() # Objeto de hilos
            hilo.start() # Inicio de hilos
            conjunto_hilos.append(hilo) # Agregagmos los hilos a lista
            print "Hilo %d iniciado" % i
            
        for hilo in conjunto_hilos:
            hilo.join(1) # Unimos los hilos y proporcionamos el tiempo agotado de espera

if __name__ == "__main__":
    daemon = NotifierDaemon(pidfile='/tmp/NotifierDaemon.pid', 
                          stdout='/tmp/NotifierDaemon.log', 
                          stderr='/tmp/NotifierDaemon.err')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print "%s started" % sys.argv[0]
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print "%s stopped" % sys.argv[0]            
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print "%s restarted" % sys.argv[0]
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)