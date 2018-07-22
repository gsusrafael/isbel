#!/usr/bin/env python
'''
Created on 19/04/2011

@author: jesus
'''
import sys
import time
import random
import subprocess
import ThreadRepeater
import pyinotify

class ModVerify(pyinotify.ProcessEvent):
    def _run_builder(self):
        try:
            retcode = subprocess.call('/usr/local/bin/runmfr.sh',
            #retcode = subprocess.call('/usr/bin/xeyes',
                                      shell=True,
                                      close_fds=True)
            if retcode < 0:
                print "La generacion de los archivos ha fallado", -retcode
            else:
                print "La generacion completada", retcode
        except OSError, e:
            print >> sys.stderr, "Ejeecution fallida:", e    
            
#    def process_default(self, event):
#        if event.maskname == 'IN_MODIFY':
#            print 'default: ', event.maskname
        
    def process_IN_MODIFY(self, event):
        event_list = [] # Contenedor de nombres de archivos
        
        # Validador de los archivos que estan siendo
        # modificados
        if event.pathname not in ['/home/megaflex/files/mfar020d', 
                                '/home/megaflex/files/mfar021']:
            # Retorna en caso que no sean los archivos que 
            # esperamos que esten siendo modificados 
            return
        
        # Verificamos si la lista esta vacia, para entonces
        # agregar 1 solo elemento
        if len(event_list) == 0:
            event_list.append(event.pathname)
        if len(event_list) == 1:
            print "Ejecutando builder para %s" % event.pathname
            self._run_builder()
            del(event_list)
    
def databuild(imon):
    print "procesando eventos..."
    imon.process_events()

    # Verificacion de eventos pendientes
    if imon.check_events():
        #Tiempo de espera para accion
        time.sleep(random.randint(10, 100) / 1000.0) 
        # retorno de eventos pendientes por monitoreo
        imon.read_events()
    del(imon)

wm = pyinotify.WatchManager()
mon = pyinotify.Notifier(wm, ModVerify())
wm.add_watch('/home/megaflex/files', pyinotify.ALL_EVENTS, rec=True)

repeater = ThreadRepeater.RepeatTimer(interval=20, 
                                   function=databuild,
                                   args=[mon])
repeater.start()