#!/usr/bin/env python
'''
Created on 05/03/2011

@author: jesus
'''
import md5
import sys

class MD5FileSum:
    '''
    Clase que se encarga de generar los checksums MD5 de los objectos de archivos
    '''
    def __init__(self, filename):
        self._fname = filename
        
    def sumfile(self, fobj):
        '''
        Retorna una matriz asociativa md5 para un objeto con el metodo read().
        '''
        m = md5.new()
        while True:
            d = fobj.read(8096)
            if not d:
                break
            m.update(d)
        return m.hexdigest()
    
    def md5sum(self):
        '''
        Retorna una matriz asociativa md5 para un nombre de archivo, o el 
        stdin si el nombre del archivo es "-".
        '''
        if self._fname == '-':
            ret = self.sumfile(sys.stdin)
        else:
            try:
                f = file(self._fname, 'rb')
            except IOError:
                return 'Failed to open file'
            ret = self.sumfile(f)
            f.close()
        return ret


# if invoked on command line, print md5 hashes of specified files.
if __name__ == '__main__':
    for fname in sys.argv[1:]:
        cksum = MD5FileSum(fname)
        print '%32s  %s' % (cksum.md5sum(), fname)