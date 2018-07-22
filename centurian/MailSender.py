#!/usr/bin/env python
'''
Created on 06/08/2010

@author: jesus
'''
        
import os
import atexit
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders

class ConnectionError(smtplib.SMTPException):
    """
        Clase para manejar los errores de conexion hacia el servidor SMTP
    """
    pass
 
class LoginError(smtplib.SMTPException):
    """
        Clase para manejar los errores de autenticacion con el servidor SMTP
    """ 
    pass

class DisconnectionError(smtplib.SMTPException): 
    """
        Clase para manejar los errores de desconexion desde el servidor SMTP
    """
    pass

class EmailSendError(smtplib.SMTPException): 
    """
        Clase para manejar los errores de envio de correo
    """
    pass

class Smtp:
    """
        Clase utilizada para el envio de mensajes de correo electronicos
        por medio a SMTP, tambien tiene la facilidad de adjuntar varios
        archivos
    """
    def __init__(self, host, user, password, port=25, debug=False):
        """
            Los parametros utilizados por el constructor son los siguientes:
            
            host = Direccion de anfitrion o IP para la conexion
            port = Puerto de conexion
            user = usuario con el que se autenticara dicha conexion
            password = clave de autenticacion de dicha conexion
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._debug = debug
        
        self._message = None
        self._subject = None
        self._from_addr = None
        self._rcpt_to = None
        self._server = None
        self._attachments = []
        
        atexit.register(self.close) #our close() method will be automatically executed upon normal interpreter termination

        self.connect()

    def connect(self):
        if all([self._host, self._port, self._user, self._password]):
            try:
                self._server = smtplib.SMTP(self._host, self._port)
                self._server.set_debuglevel(self._debug) # Activa el modo de depuracion
                self._server.ehlo_or_helo_if_needed()
                
                if self._server.has_extn('STARTTLS'): # Validamos si el servidor soporta SSL
                    self._server.starttls()
                    self._server.ehlo_or_helo_if_needed()

            except smtplib.SMTPException, e:
                raise ConnectionError("Connection failed! %s " % e)

            try:
                self._server.login(self._user, self._password)
            except smtplib.SMTPException, e:
                raise LoginError("Login Failed! %s " % e)

    def close(self):
        if self._server:
            try:
                self._server.quit()
            except smtplib.SMTPException, e:
                raise DisconnectionError("Disconnection failed! %s" % e)

    def message(self, message):
        self._message = message

    def subject(self, subject):
        self._subject = subject

    def from_addr(self, email):
        self._from_addr = email

    def rcpt_to(self, email):
        self._rcpt_to = email
        
    def attach(self, file):
        if os.path.exists(file):
            self._attachments.append(file)

    def load_attachments(self, m_message):
        for file in self._attachments:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file,"rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
            m_message.attach(part)
            
        return m_message

    def send(self, content_type='plain', charset='UTF-8'):
        if all([self._message, self._subject, self._from_addr, self._rcpt_to]):
            m_message = MIMEMultipart()

            m_message['From'] = self._from_addr
            m_message['To'] = self._rcpt_to
            m_message['Date'] = formatdate(localtime=True)
            m_message['Subject'] = self._subject
            m_message['X-Mailer'] = "Python X-Mailer"

            m_message.attach(MIMEText(self._message, content_type, charset))

            m_message = self.load_attachments(m_message)

            try:
                self._server.sendmail(self._from_addr, self._rcpt_to, m_message.as_string())
            except smtplib.SMTPException, e:
                raise EmailSendError("Email has not been sent %s " % e)
    
if __name__ == '__main__':
    mailer = Smtp('smtp.gmail.com', 'jesusrafael@gmail.com', 'tormentor')
    mailer.subject("Correo de prueba")
    mailer.message("Prueba de mensaje")
    mailer.from_addr('jesusrafael@gmail.com')
    mailer.rcpt_to('jesus@codigolibre.org')
    mailer.attach('/home/jesus/prueba.sdb')
    mailer.attach('/home/jesus/yed.jnlp')
    mailer.send()