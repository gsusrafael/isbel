#!/usr/bin/env python
'''
Created on 29/07/2010

@author: jesus
'''
__author__ = "Jesus Rafael Sanchez Medrano"

import sys
import time
import random
import gamin
import threading
#import subprocess

from datetime import datetime

return_path = ''
dateformat = '%Y-%m-%d %H:%M:%S'
_response = ''

class SystemOutput:
    def __init__(self):
        pass
    
    def log_stdout(self, message):
        sys.stdout.write(str(message) +'\n')
    
    def log_stderr(self, message):
        sys.stderr.write(str(message) +'\n')

class DirectoryNotifier(SystemOutput):
    def __init__(self):
        SystemOutput.__init__(self)
        self.lock = threading.Lock()
        self.value = 0
        self.return_path = ''
        self._response = ''

    def callback(self, path, event):
        self.lock.acquire() # critical section
        
        if event == gamin.GAMCreated:
            self.return_path = path
            
            file_date = datetime.strftime(datetime.now(), dateformat)
            self.log_stdout("archivo %s creado en fecha => %s \n" % (path, file_date))
            
            archivo = open("/home/pos/salida" + path, "r")
            data = archivo.readlines()
            self._response = "|".join(i.replace("\n", "") for i in data if i > 0)
            #archivo.writelines(["Prueba de archivo " + path + "\n"])
            archivo.close()
        else:
            pass
        
        self.lock.release()
        
notifier = DirectoryNotifier() # Variable que contiene la instancia de captura de eventos para Centinela
monitor = gamin.WatchMonitor()  # Variable que contiene el objeto de Centinela de Monitoreo de GAMIN
monitor.watch_directory("/home/pos/salida", notifier.callback)

response = _response

class DirectoryWorkerNotifier(SystemOutput, threading.Thread):
    def run(self):
        i = 0
        while True:
            monitor.handle_one_event()
            time.sleep(random.randint(10, 100) / 1000.0)
            self.log_stdout('%s %s %d %s' % (self.getName(), "-- Tarea", i, "terminada"))
            i = i + 1

if __name__ == '__main__':
    for i in range(10):
        DirectoryWorkerNotifier().start() # start a worker
        print DirectoryWorkerNotifier().isAlive()