#!/usr/bin/env python
'''
Created on 20/07/2010

@author: jesus
'''
try:
    set
except NameError:
    from sets import Set as set #@deprecated

from datetime import datetime
from xml.etree import cElementTree as ElementTree #@UnresolvedImport

from XmlConfigParser import XmlDictConfig
from XmlValidateDTD import ValidateError, ValidateXML
from ProcessLogger import SocketLogger

import SocketServer
import threading
import logging
import subprocess
import sys
import os
import socket

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
xmlconfig = XmlDictConfig(configroot)

class SocketServiceHandler(SocketServer.BaseRequestHandler):
    '''
        Objetivo:
            recibir las peticiones de datos que vienen a
            traves del socket, encapsularlas en memoria
            para hacer la persistencia en archivo y luego
            procesarlas hacia otras interfaces externas.
    '''

    timeout = 1

    # separador de campos
    field_separator = xmlconfig['DataFrames']['FieldSeparator']

    # separador de registros
    record_separator = xmlconfig['DataFrames']['RecordSeparator']

    # listado de ip permitidas segun el archivo de configuracion
    client_allow = xmlconfig['AccessControl']['Allow']

    # format de fecha en parametros generales
    dateformat = xmlconfig['General']['DateFormat']

    # nombre base del archivo
    file_name = xmlconfig['General']['FileName']

    # extension de archivo
    file_ext = xmlconfig['General']['FileExtension']

    # configurar la ruta donde se almacenara el archivo
    # de entrada a MegaFlex
    in_path = xmlconfig['General']['InPath']

    # configurar la ruta donde se almacenara el archivo
    # de salida a MegaFlex
    out_path = xmlconfig['General']['OutPath']

    # comando de interface de datos hacia MegaFlex
    interface_command = xmlconfig['General']['InterfaceCommand']

    # buffer para transferencia de datos de socket
    socket_buffer = int(xmlconfig['SocketConfig']['SocketBuffer'])

    # ruta en donde se almacenaran los logs
    logpath = xmlconfig['LogConfig']['LogPath']

    # nombre del log de salida
    outlogname = xmlconfig['LogConfig']['OutLogName']

    # formato de fechas del log
    logdateformat = xmlconfig['LogConfig']['LogDateFormat']

    # formato de estructura del log
    logformat = xmlconfig['LogConfig']['LogFormat']

    # Tamanio del log antes de dividirse
    logsize = int(xmlconfig['LogConfig']['LogSize']) * 1024

    # Cantidad de partes del log a conservar
    logparts = int(xmlconfig['LogConfig']['LogParts'])

    # Variable de instancia de logger, con el modo de append
    slog = SocketLogger(logpath + "/" + outlogname, "a", logging.DEBUG)

    # Formato de fecha de log
    slog.dateformat(logdateformat)

    # Tamanio maximo de log para ser dividido
    slog.logsize(logsize)

    # Cantidad de partes del log
    slog.logparts(logparts)

    # Nombre de la facilidad de log
    slog.application_name("SocketService")

    # Formato de log
    slog.logformat(logformat)

    # Ejecucion de log
    slog.dolog()

    def log_stdout(self, message, socket_output=None):
        try:
            if socket_output:
                self.request.send( str(message) +'\n')
        except IOError:
            pass

        self.slog.logdebug(message)

    def reply_error(self, message):
        self.request.send( str(message) +'\n')

    def setup(self):
        if self.server.timeout is not None:
            self.request.settimeout(self.server.timeout)
        else:
            self.request.settimeout(3)

        self.slog.loginfo("('%s', %s) connectado" %
                           (self.client_address[0], self.client_address[1]))

    def handle(self):
        # Obtiene la direccion IP que se esta conectando al socket
        ipv4addr = self.client_address[0]
        curr_trhead = threading.currentThread()
        self.slog.loginfo("Abriendo hilo de conexion <%s>" % curr_trhead.getName())

        # Verifica que el cliente se encuentre en la lista de permitidos
        #if ipv4addr in self.client_allow:
        if True:
            # De encontrarse el cliente, permite continuar con los comandos
            while True:
                try:
                    # Recibe datos de peticion del socket
                    batch_data = self.request.recv(self.socket_buffer)

                    # Eliminamos todo rastro de caracter en blanco
                    batch_raw_data = batch_data.strip()
                    # Partimos los registros por separador
                    batch_data_list = batch_raw_data.split(self.record_separator)

                    # Seccion de datos de cabecera
                    # Leemos los valores de la lista para cabecera
                    head_raw_data = batch_data_list[0]

                    # Partimos la data por el separador, en una lista
                    head_data_list = head_raw_data.split(self.field_separator)
                    self.slog.loginfo("IP: [%s], cabecera: <%s> " % (ipv4addr, head_data_list))
                    # Fin de datos cabecera

                    for i in batch_data_list[1:-1]:
                        self.slog.loginfo("IP: [%s], datos: <%s> " % (ipv4addr, i.split(self.field_separator)))

                    # Seccion de datos de terminador
                    # Leemos los valores de la lista para terminador
                    tail_raw_data = batch_data_list[-1]

                    # Partimos la data por el separador, en una lista
                    tail_data_list = tail_raw_data.split(self.field_separator)
                    self.slog.loginfo("IP: [%s], terminal: <%s> " % (ipv4addr, tail_data_list))
                    # Fin de datos terminador

                    # Validamos que venga la misma cantidad de elementos entre cabecera y terminador
                    if ( len(head_data_list) == 10 and len(tail_data_list) == 10 ) and \
                       ( len(head_data_list) == len(tail_data_list) ):
                        # Seccion de validacion de cabecera con terminador

                        cmp_head = set(head_data_list)
                        cmp_tail = set(tail_data_list)

                        # Hacemos una comparacion entre cada uno de los elementos de la lista de datos
                        cmp_delta = list(cmp_head.intersection(cmp_tail))

                        # Verificamos si coinciden, para continuar
                        if len(cmp_delta) == 10:
                            try:
                                # Seccion de variables de cabecera
                                h_t_trama = int(head_data_list[0])
                                h_fecha_ticket = int(head_data_list[1].strip('f'))
                                h_grupo_banca = int(head_data_list[2].strip('g'))
                                h_stan = int(head_data_list[3].strip('s'))
                                h_count = int(head_data_list[4])
                                h_tid = str(head_data_list[5])
                                h_valor_ticket = int(head_data_list[6])
                                h_hora_ticket = int(head_data_list[7].strip('h'))
                                h_mtp = int(head_data_list[8].strip('m'))
                                h_pc = str(head_data_list[9].strip('p'))
                                # Fin de variables cabecera

                                # Seccion de variables de terminador
                                t_t_trama = int(head_data_list[0])
                                t_fecha_ticket = int(head_data_list[1].strip('f'))
                                t_grupo_banca = int(head_data_list[2].strip('g'))
                                t_stan = int(head_data_list[3].strip('s'))
                                t_count = int(head_data_list[4])
                                t_tid = str(head_data_list[5])
                                t_valor_ticket = int(head_data_list[6])
                                t_hora_ticket = int(head_data_list[7].strip('h'))
                                t_mtp = int(head_data_list[8].strip('m'))
                                t_pc = str(head_data_list[9].strip('g'))
                                # Fin de variables terminador

                            except TypeError:
                                self.reply_error('1|1|Contenido de trama no valido|')
                                self.slog.logerror('[Contenido de trama no valido]')
                                return

                            if int(h_count) == len(batch_data_list[1:-1]) and \
                               int(t_count) == len(batch_data_list[1:-1]):
                                # Nombre completo de archivo
                                file_date = datetime.strftime(datetime.now(), self.dateformat) # Fecha de archivo
                                file_nameid = str(h_stan) + '_' + self.file_name + '_' + file_date + self.file_ext

                                try:
                                    file_handle = open(self.in_path + '/' + file_nameid, 'w') # Abre archivo para escritura

                                    # Escribe cabecera de la trama en archivo
                                    file_handle.writelines( str("%1d%08d%06d%06d%04d%s%09d%011d%04d%s\n" %
                                                                 (h_t_trama,
                                                                  h_fecha_ticket,
                                                                  h_grupo_banca,
                                                                  h_stan,
                                                                  h_count,
                                                                  h_tid.rjust(8,'0'),
                                                                  h_valor_ticket,
                                                                  h_hora_ticket,
                                                                  h_mtp,
                                                                  h_pc.rjust(7,'0')
                                                                 )
                                                              )
                                                         )

                                    # Inicio de cuerpo de archivo
                                    for i in batch_data_list[1:-1]:
                                        lst_body_data = i.split(self.field_separator)

                                        tipo_jugada = int(lst_body_data[0])
                                        loteria = int(lst_body_data[1])
                                        valor_jugada = int(lst_body_data[2])
                                        jugada1 = lst_body_data[3]
                                        jugada2 = lst_body_data[4]
                                        jugada3 = lst_body_data[5]

                                        # Escribiendo el cuerpo del archivo
                                        file_handle.writelines( str("%01d%02d%07d%s%s%s\n" %
                                                                   (tipo_jugada,
                                                                    loteria,
                                                                    valor_jugada,
                                                                    jugada1.rjust(2,'0'),
                                                                    jugada2.rjust(2,'0'),
                                                                    jugada3.rjust(2,'0')
                                                                   )
                                                                  )
                                                             )
                                    # Fin de cuerpo de archivo

                                    # Escribe terminador de la trama en archivo
                                    file_handle.writelines( str("%1d%08d%06d%06d%04d%s%09d%011d%04d%s\n" %
                                                               (t_t_trama,
                                                                t_fecha_ticket,
                                                                t_grupo_banca,
                                                                t_stan,
                                                                t_count,
                                                                t_tid.rjust(8,'0'),
                                                                t_valor_ticket,
                                                                t_hora_ticket,
                                                                t_mtp,
                                                                t_pc.rjust(7,'0')
                                                               )
                                                              )
                                                         )

                                    file_handle.close() # Cierra la escritura del archivo

                                    # Para creacion de tramas hacia HAS
                                    #
                                    # print "|".join(i.replace("\n", "") for i in x if i > 0)
                                    #
                                    command = [self.interface_command, self.in_path + '/' + file_nameid]
                                    try:
                                        retcode = subprocess.Popen(command,
                                                                   shell=False,
                                                                   close_fds=True)
                                        retcode.communicate(None)

                                        if retcode.returncode < 0:
                                            self.reply_error("1|1|Child was terminated by signal %d|" % -retcode.returncode)
                                            self.slog.logerror('[Child was terminated by signal %d]' % -retcode.returncode)

                                        elif retcode.returncode == 0:
                                            try:
                                                fdata = open(self.out_path + '/' + file_nameid, "r")
                                                pdata = fdata.readlines()
                                                fdata.close()
                                                response = self.field_separator.join(i.replace("\n", "")
                                                                                     for i in pdata if i > 0)
                                            except IOError as (errno, strerror):
                                                self.reply_error("1|1|I/O error (%d): %s, en la construccion de respuesta|" %
                                                               (errno, strerror))
                                                self.slog.logerror('[I/O error (%d): %s, en la construccion de respuesta]' %
                                                                 (errno, strerror))
                                                return

                                        else:
                                            self.reply_error("1|1|Child returned %d|" % retcode.returncode)
                                            self.slog.logerror("[Child returned %d]" % retcode.returncode)

                                    except OSError, e:
                                        self.reply_error("1|1|Execution failed: %s|" % e)
                                        self.slog.logerror("[Execution failed: %s]" % e)
                                        return

                                    self.request.send(response + "|")
                                    self.slog.loginfo("IP: [%s], respuesta: <%s> " % (ipv4addr, response))


                                except IOError as (errno, strerror):
                                    self.reply_error("1|1|I/O error(%d): %s|" % (errno, strerror))
                                    self.slog.logerror("[I/O error(%d): %s]" % (errno, strerror))

                                finally:
                                    os.remove(self.in_path + '/' + file_nameid)
                                    os.remove(self.out_path + '/' + file_nameid)
                                    return

                            else:
                                self.reply_error('1|1|Contenido de trama no valido|')
                                self.slog.logerror('[Contenido de trama no valido]')
                                return
                        else:
                            self.reply_error('1|1|Datos no validos para cabecera|')
                            self.slog.logerror('[Datos no validos para cabecera]')
                            return
                    else:
                        self.reply_error('1|1|Trama invalida|')
                        self.slog.logerror('[Trama invalida]')
                        return

                except socket.timeout:
                    self.reply_error('1|1|Tiempo de espera agotado|')
                    self.slog.logerror('[::TIEMPO DE ESPERA AGOTADO::]')
                    return

            else: # Si no esta en la lista
                self.reply_error('1|1|La direccion IP: %s No esta permitida para el acceso|' %
                                 str(self.client_address[0]))
                self.slog.logerror('La direccion IP: %s No esta permitida para el acceso' %
                                 str(self.client_address[0]))
                return

    def handle_timeout(self):
        self.reply_error('1|1|Tiempo agotado para solicitud|')
        return

    def finish(self):
        curr_trhead = threading.currentThread()
        self.slog.loginfo("Cerrando hilo de conexion <%s>" % curr_trhead.getName())
        self.slog.loginfo("('%s', %s) desconnectado" %
                          (self.client_address[0], self.client_address[1]))

if __name__ == '__main__':
    class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
        '''
            Mix-In Class for TCP Socket Server with Threads
        '''
        pass

    # puerto donde escucha el socket
    socket_port = int(xmlconfig['SocketConfig']['SocketPort'])
    socket_listen= xmlconfig['SocketConfig']['ListenAddress']

    try:
        socket_server = ThreadedTCPServer((socket_listen, socket_port),
                                    SocketServiceHandler)
        socket_server.timeout = 1

    except IOError:
        sys.stderr.write('El puerto se encuentra en uso por otro servicio\n')
        sys.exit(3)

    ip, port = socket_server.server_address

    server_thread = threading.Thread(target=socket_server.serve_forever(5))
    server_thread.setDaemon(True)
    server_thread.start() # inicio del socket
