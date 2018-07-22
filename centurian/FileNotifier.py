#!/usr/bin/env python
'''
Created on 12/03/2011

@author: jesus
'''

import os
import time
import random
import Queue
import paramiko
import threading
import pyinotify
import MailSender

paramiko.util.log_to_file('/tmp/paramiko.log')

class ProcessFile(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if all(not event.pathname.endswith(ext) for ext in ['gz']):
            return

        try:
            queueLock.acquire()
            workQueue.put(event.pathname)
            print workQueue.qsize(), event.pathname
        finally:
            queueLock.release()
            
class QueueProcessor(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name
                  
class FileMonitor(threading.Thread):
    '''
    Clase que hereda de threading.Thread para el manejo de la 
    concurrencia
    '''
    def __init__(self, imon, threadID, name, q):
        '''
        Constructor polimofico de clase, este recibe por parametro
        el objeto de gamin para la monitorizacion de los eventos del
        sistema de archivos
        '''
        threading.Thread.__init__(self)
        # Objeto de GAMIN/PyInotify para eventos del sistema de archivos
        self.threadID = threadID
        self.imon = imon
        self.name = name
        self.q = q

    def run(self):
        while self.q.empty(): # En una cola sin elementos
            # Procesando los eventos de PyInotify
            self.imon.process_events()
            
            # Verificacion de eventos pendientes
            if self.imon.check_events():
                #Tiempo de espera para accion
                time.sleep(random.randint(10, 100) / 1000.0) 
                # retorno de eventos pendientes por monitoreo
                self.imon.read_events()
            

def process_data(threadName, q):
    run_command = False
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            try:
                transport = paramiko.Transport(('sys000.dns2go.com', 22)) 
                transport.connect(username='recargas', password='123')
                
                sftp = paramiko.SFTPClient.from_transport(transport)
                sftp.put(data, os.path.join('/home/megaflex/espejo/recibe', 
                              os.path.basename(data)))
                
                sftp.close()
                transport.close()
                
                print workQueue.qsize()
                if workQueue.qsize() == 1 or workQueue.qsize() == 0:
                    run_command = True
                
                print "%s processing %s" % (threadName, data)
            except IOError as strerror: # Si pasa algun error de I/O
                # Libera el seguro de la cola
                #queueLock.release()
                
                # Prepara la rutina de envio de alarma
                mailer = MailSender.Smtp('smtp.gmail.com', 
                                       'jesusrafael@gmail.com', 
                                       'tormentor')
                mailer.subject("Error intentando hacer copia Espejo")
                mailer.message("error tratando de enviar el archivo %s, [%s]" % \
                               (data, strerror))
                mailer.from_addr('jesusrafael@gmail.com')
                mailer.rcpt_to('jesus@codigolibre.org')
                mailer.attach('%s' % (data))
                mailer.send()
                
                # Despliega el siguiente error
                print "error tratando de enviar el archivo %s, [%s]" % \
                      (data, strerror)

        else:
            if run_command:
                print "Ejecutando comando de sincronizacion"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname='sys000.dns2go.com', 
                            port = 22,
                            username = 'recargas',
                            password = '123')
                ssh.exec_command('cd /home/megaflex/objetos')
                ssh.exec_command('TERM=linux sudo runcbl MFR0167')
                ssh.close()
                print "Fin de sincronizacion"
                workQueue.queue.clear()
                del(data)
                run_command = False
            queueLock.release()
        time.sleep(random.randint(10, 100) / 1000.0)

wm = pyinotify.WatchManager()
mon = pyinotify.Notifier(wm, ProcessFile())

wm.add_watch('/home/megaflex/espejo/envia', pyinotify.IN_CREATE, rec=True)

queueLock = threading.Lock()
workQueue = Queue.Queue(4)

threadList = ["QueueProcessor-0", 
             "QueueProcessor-1"]
thread_ID = 1
threads = []

exitFlag = 0

if __name__ == '__main__':
    for i in range(7):
        thread_notifier = FileMonitor(mon, i, "FileMonitor-%d" % i, workQueue)
        thread_notifier.setDaemon(True)
        thread_notifier.start()
    
    for tName in threadList:
        thread = QueueProcessor(thread_ID, tName, workQueue)
        thread.start()
        threads.append(thread)
        thread_ID += 1
    
    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Wait for all threads to complete
    for t in threads:
        t.join()