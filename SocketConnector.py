#!/usr/bin/env python
'''
Created on 26/02/2011

@author: jesus
'''

import sys
import signal
import SocketClient

from xml.etree import cElementTree as ElementTree #@UnresolvedImport
from XmlConfigParser import XmlDictConfig
from XmlValidateDTD import ValidateError, ValidateXML

try:
    try:
        ValidateXML('/etc/isbel_client.xml', '/etc/isbel_client.dtd')
        xmltree = ElementTree.parse('/etc/isbel_client.xml')
    except ValidateError:
        ValidateXML('isbel_client.xml', 'isbel_client.dtd')
        xmltree = ElementTree.parse('isbel_client.xml')
except IOError:
    print "error de validacion"
    sys.exit(1)

configroot = xmltree.getroot()
xmlconfig = XmlDictConfig(configroot)

# nombre base del archivo de cola
spool_name = xmlconfig['General']['SpoolName']

# extension de cola
spool_ext = xmlconfig['General']['SpoolExtension']

# Ruta de entrada de cola 
in_spool = xmlconfig['General']['InSpool']

# Ruta de salida de cola 
out_spool = xmlconfig['General']['OutSpool']

# Direccion de host hacia donde se conectara
destination_address = xmlconfig['SocketConfig']['DestinationAddress']

# Puerto de conexion destinada
socket_port = int(xmlconfig['SocketConfig']['SocketPort'])

# Buffer de archivo
socket_buffer = int(xmlconfig['SocketConfig']['SocketBuffer'])

if __name__ == "__main__":
    try:
        sconn = SocketClient.SocketClient(destination_address, socket_port)
        sconn.connect()
        
        # Catch some signals
        signal.signal(signal.SIGINT, sconn.close)
        signal.signal(signal.SIGTERM, sconn.close)
    
        sconn.buffer(socket_buffer)
        try:
            with open(out_spool + '/' + spool_name + spool_ext, "r") as fsend:
                breaklines = ""
                fsendlines = fsend.readlines()
                
                for i in fsendlines:
                    breaklines = breaklines + i.strip("\n")
                    
                if fsendlines:
                    sconn.send(breaklines.rstrip("@"))
                else:
                    sconn.send("\n")
                fsend.close()

            with open(in_spool + '/' + spool_name + spool_ext, "w+") as fget:
                fget.write(sconn.receive())
                fget.close()
        except IOError:
            print "ERROR: No se puede generar el archivo"
            sys.exit(1)
        
        sconn.close()
    except IOError:
        try:
            with open(in_spool + '/' + spool_name + spool_ext, "w") as fget:
                fget.write("9|1|Conexion rechazada|\n")
                fget.close()
        except IOError:
            print "ERROR: No se puede generar el archivo"
            sys.exit(1)
    else:
        try:
            with open(in_spool + '/' + spool_name + spool_ext, "w") as fget:
                fget.write("9|1|Error de conexion|\n")
                fget.close()
        except IOError:
            print "ERROR: No se puede generar el archivo"
            sys.exit(1)