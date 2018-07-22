#!/usr/bin/env python
'''
Created on 12/10/2010

@author: jesus
'''
#import logging
import logging.handlers

class SocketLogger:
    def __init__(self, filename, mode, level):
        """
        Creacion de objeto para creacion de logs
        """
        #
        # Declaracion de parametros de clase
        #
        
        # Nombre de archivo de log
        self._filename = filename
        # Modo de almacenamiento
        self._mode = mode
        # Nivel por defecto de registro
        self._level = level
        
        # Parametros que necesitan ser referenciados
        self._dateformat = None
        self._app_name = None
        self._formatter = None
        self._logformat = None
        self._size = None
        self._parts = None
        self._handler = None
        self._logger = None
        
    def dateformat(self, dateformat):
        """
         Metodo para declarar el formato de fecha
        """
        self._dateformat = dateformat
        
    def logformat(self, logformat):
        """
         Metodo para declarar el formato del log
        """
        self._logformat = logformat
        
    def application_name(self, app_name):
        """
         Metodo para declarar el nombre de la aplicacion
        """
        self._app_name = app_name
        
    def set_level(self, level):
        """
         Metodo para declarar el nivel de registro
        """
        self._level = level
        
    def logsize(self, size):
        """
         Metodo para declarar el tamanio del registro de acciones
        """
        self._size = size
        
    def logparts(self, parts):
        """
         Metodo para declarar la cantidad de registros a mantener
        """
        self._parts = parts
        
    def dolog(self):
        """
         Metodo para mandar la ejecucion del logger
        """
        # Declaramos el formato de registro (log y fecha)
        self._formatter = logging.Formatter(self._logformat, self._dateformat)
        # Declaramos el objeto de captura y procesamiento del log
        self._handler = logging.handlers.RotatingFileHandler(
                                                 filename=self._filename,
                                                 mode=self._mode,  
                                                 maxBytes=int(self._size),
                                                 backupCount=int(self._parts))
        # Declaramos el nombre de la instancia que hace el registro
        self._logger = logging.getLogger(self._app_name)
        
        # Aplicamos el formato al objeto de captura y procesamiento del log
        self._handler.setFormatter(self._formatter)
        # Aplicamos el nivel por defecto de registro de acciones
        self._logger.setLevel(self._level)
        # Aplicamos el objeto de captura y procesamiento del log
        self._logger.addHandler(self._handler)
    
    def logdebug(self, message):
        """
        Metodo para mensajes de depuracion (debug)
        """
        self._logger.debug(message)
        
    def loginfo(self, message):
        """
        Metodo para mensajes de informacion (info)
        """
        self._logger.info(message)

    def logwarn(self, message):
        """
        Metodo para mensajes de advertencia (warning)
        """
        self._logger.warning(message)

    def logerror(self, message):
        """
        Metodo para mensajes de error (error)
        """
        self._logger.error(message)
        
    def logcrit(self, message):
        """
        Metodo para mensajes criticos (critical)
        """
        self._logger.critical(message)
        
if __name__ == "__main__":
    log = SocketLogger("/home/jesus/prueba.log", "a", logging.DEBUG)
    log.dateformat("%Y-%m-%d %H:%M:%S")
    log.logsize(80)
    log.logparts(3)
    log.application_name("prueba")
    log.logformat("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log.dolog()
    
    for i in range(100):
        log.logdebug("Esto es una prueba de mi objeto de logger")
        log.logerror("hola")
        
