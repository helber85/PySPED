#coding: utf-8
# Mecanismos de transporte SOAP usando SUDS sobre conexão SSL por Certificado
# Adaptado de: http://stackoverflow.com/a/6532645/798575 

import urllib2
from suds.client import Client
from suds.transport.http import HttpTransport, Reply, TransportError
import httplib

class HTTPSCertAuthHandler(urllib2.HTTPSHandler):  
    def __init__(self, key, cert):  
        urllib2.HTTPSHandler.__init__(self)  
        self.key = key  
        self.cert = cert  

    def https_open(self, req):  
        #Rather than pass in a reference to a connection class, we pass in  
        # a reference to a function which, for all intents and purposes,  
        # will behave as a constructor 
        return self.do_open(self.getConnection, req) 

    def getConnection(self, host, timeout=300):  
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)  

class HttpsCertTransport(HttpTransport):
    def __init__(self, key, cert, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert

    def u2open(self, request):
        """
        Open a connection.
        @param request: A urllib2 request.
        @type request: urllib2.Request.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout
        url = urllib2.build_opener(HTTPSCertAuthHandler(self.key, self.cert))  
        if self.urllib2.ver() < 2.6:
            socket.setdefaulttimeout(tm)
            connection = url.open(urllib2request)
        else:
            connection = url.open(urllib2request, timeout=tm)
        
        return connection

if __name__ == '__main__':
    ## Apenas para testar...

    # These lines enable debug logging; remove them once everything works.
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    logging.getLogger('suds.transport').setLevel(logging.DEBUG)

    import os
    key_path = os.environ.get('SPED_KEY_PATH', '/path/to/YOUR_KEY_AND_CERT.pem')
    key_password = os.environ.get('SPED_KEY_PASSWORD', 'DEADBEEF')
    cert_path = os.environ.get('SPED_CERT_PATH', key_path)

    c = Client('https://YOUR_URL_HERE',
        transport = HttpsCertTransport('YOUR_KEY_AND_CERT.pem', 'YOUR_KEY_AND_CERT.pem')
    )

    print c