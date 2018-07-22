#!/usr/bin/env python
'''
Created on 25/07/2010

@author: jesus
'''

import threading
from threading import Thread
import subprocess
import gamin
import time
import os

ruta = ''

class NotifierDaemon:
    path_to_check = "."
    
    def __init__(self, callback_function):
        self.__monitor = gamin.WatchMonitor()
        self.__monitor.watch_directory(self.path_to_check, callback_function)
        
    def notify(self):
        self.__monitor.handle_one_event()
        
    def unlink(self):
        self.__monitor.stop_watch(self.path_to_check)
        self.__monitor.disconnect()
        del self.__monitor
        pass

def callback(path, event):
    global ruta
    ruta = path
    
    if event == gamin.GAMCreated:
        print "archivo %s creado \n" % path
    elif event == gamin.GAMDeleted:
        pass
        #print "archivo %s borrado \n" % path
    elif event == gamin.GAMChanged:
        pass

def notifier_start():
    NotifierDaemon.path_to_check = "/tmp/monitoreo"
    notifier = NotifierDaemon(callback)
    print "Iniciando proceso"
    
    while ruta <> "termina":
        #q.get()
        notifier.notify()
        time.sleep(.1)

    notifier.unlink()
    
if __name__ == '__main__':
    for i in range(10):
        thread_notifier = Thread(target = notifier_start, verbose=True)
        thread_notifier.getName()
        thread_notifier.start()