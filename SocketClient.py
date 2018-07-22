#!/usr/bin/env python
'''
Created on 21/02/2011

@author: jesus
'''
import socket
import signal
import sys

#from XmlConfigParser import XmlDictConfig
#from XmlValidateDTD import ValidateError, ValidateXML
#from xml.etree import cElementTree as ElementTree #@UnresolvedImport

class SocketClient:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        
        self._connsock = None
        self._outputframe = None
        self._dataframe = None 
        self._socket_buffer = None
    
    def connect(self):
        """ Setup client socket and connect """ 
        self._connsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connsock.connect((self._host, self._port))
        
    def send(self, dataframe):
        """ Send the data frame to the server """
        self._dataframe = dataframe
        self._connsock.sendall(self._dataframe)
    
    def buffer(self, socket_buffer):
        """ Sets the connection buffer """
        self._socket_buffer = socket_buffer
    
    def receive(self):
        """ Receives the dataframe for returning output """
        self._outputframe =  self._connsock.recv(self._socket_buffer)
        return self._outputframe
    
    def close(self):
        """ Keyboard Interrupt handler and cleanup routine """
        # Close the client socket
        self._connsock.close()
        sys.exit(0)

if __name__ == "__main__": 
    try:
        sconn = SocketClient("localhost", 2020)
        sconn.connect()
        # Catch some signals
        signal.signal(signal.SIGINT, sconn.close)
        signal.signal(signal.SIGTERM, sconn.close)
    
        sconn.buffer(1024)
        sconn.send("prueba")
        x = sconn.receive()
        print x.strip()
        sconn.close()
    except IOError:
        print "Error de salida"