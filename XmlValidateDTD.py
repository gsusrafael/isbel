#!/usr/bin/env python
'''
Created on 05/10/2010

@author: jesus
'''
from xml.parsers.xmlproc import xmlproc #@UnresolvedImport
from xml.parsers.xmlproc import xmlval  #@UnresolvedImport
from xml.parsers.xmlproc import xmldtd  #@UnresolvedImport
from xml.parsers.xmlproc import utils   #@UnresolvedImport

class ValidateError(Exception): pass

def ValidateXML(xml_filename, dtd_filename):
    """Validate a given XML file with a given external DTD.

    If the XML file is not valid, an error message will be printed
    to sys.stderr, and the program will be terminated with a non-zero
    exit code.  If the XML file is valid, nothing will be printed.
    """
    dtd = xmldtd.load_dtd(dtd_filename)
    parser = xmlproc.XMLProcessor()
    parser.set_application(xmlval.ValidatingApp(dtd, parser))
    parser.dtd = dtd
    parser.ent = dtd
    # If you want to override error handling, subclass
    # xml.parsers.xmlproc.xmlapp.ErrorHandler and do
    #   parser.set_error_handler(MyErrorHandler(parser))
    try:
        parser.parse_resource(xml_filename)
        parser.set_error_handler(utils.ErrorRaiser(parser))
    except SystemExit:
        raise ValidateError
    
    # If you have xml data only as a string, use instead
    #   parser.feed(xml_data)
    #   parser.close()

if __name__ == '__main__':
    import sys
    try:
        ValidateXML(sys.argv[1], sys.argv[2])
    except ValidateError:
        print "error de validacion"
        sys.exit(1)