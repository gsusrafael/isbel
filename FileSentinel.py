#!/usr/bin/env python
'''
Created on 12/03/2011

@author: jesus
'''

import signal
import threading
import pyinotify
from centurian import FileNotifier 
#import os
#import sys

#'''
#from xml.etree import cElementTree as ElementTree #@UnresolvedImport
#from XmlConfigParser import XmlDictConfig
#from XmlValidateDTD import ValidateError, ValidateXML
#
#try:
#    try:
#        ValidateXML('/etc/isbel_client.xml', '/etc/isbel_client.dtd')
#        xmltree = ElementTree.parse('/etc/isbel_client.xml')
#    except ValidateError:
#        ValidateXML('isbel_client.xml', 'isbel_client.dtd')
#        xmltree = ElementTree.parse('isbel_client.xml')
#except IOError:
#    print "error de validacion"
#    sys.exit(1)
#
#configroot = xmltree.getroot()
#xmlconfig = XmlDictConfig(configroot)
#'''

wm = pyinotify.WatchManager()
mon = pyinotify.Notifier(wm, FileNotifier.ProcessFile())

wm.add_watch('/home/megaflex/espejo/envia', pyinotify.IN_CREATE, rec=True) #@UndefinedVariable

signal.signal(signal.SIGINT, FileNotifier.FileMonitor.stop)
signal.signal(signal.SIGTERM, FileNotifier.FileMonitor.stop)
        
threadLock = threading.Lock()
threads = []

if __name__ == '__main__':
    for i in range(10):
        thread_notifier = FileNotifier.FileMonitor(mon)
        thread_notifier.setName("FileMonitor-%d" % i)
        thread_notifier.getName()
        thread_notifier.start()
        threads.append(thread_notifier)