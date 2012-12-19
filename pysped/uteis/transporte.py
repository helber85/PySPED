#coding: utf-8
# Mecanismos de transporte SOAP usando SUDS sobre conexão SSL por Certificado
# Adaptado de: http://stackoverflow.com/a/6532645/798575 

import urllib2
from suds.client import Client
from suds.transport.http import HttpTransport, Reply, TransportError
from suds.bindings import binding
from OpenSSL import crypto
import tempfile
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
    def __init__(self, key, cert, password=None, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert

        # httplib only accepts PEM, not PFX
        if self.key.lower().endswith(('pfx', 'p12')) and self.cert == self.key:
            #Lets get a PEM Key and Cert
            p12 = crypto.load_pkcs12(file(self.key, 'rb').read(), password)
            pem_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
            pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())

            self.pem_key_file = tempfile.NamedTemporaryFile()
            self.pem_key_file.write(pem_key)
            self.pem_key_file.flush()

            self.pem_cert_file = tempfile.NamedTemporaryFile()
            self.pem_cert_file.write(pem_cert)
            self.pem_cert_file.flush()

            self.key = self.pem_key_file.name
            self.cert = self.pem_cert_file.name

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

        connection = url.open(request, timeout=tm)
        return connection

if __name__ == '__main__':
    ## Apenas para testar...

    # These lines enable debug logging; remove them once everything works.
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    #logging.getLogger('suds.transport').setLevel(logging.DEBUG)
    #logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
    #logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

    import os
    key_path = os.environ['SPED_KEY_PATH'] # '/path/to/YOUR_KEY_AND_CERT.pem
    key_password = os.environ.get('SPED_KEY_PASSWORD', '') # Senha vazia? Mesmo??
    cert_path = os.environ.get('SPED_CERT_PATH', key_path) # Juntos KEY e CERT?
    test_url = 'https://homologacao.nfe.fazenda.sp.gov.br/cteWEB/services/cteStatusServico.asmx?WSDL'

    transport = HttpsCertTransport(key_path, cert_path, password=key_password)
    
    # SOAP server expects a SOAP 1.2 envelope, not a SOAP 1.1 envelope
    # and will complain if this hack isn't done.
    binding.envns = ('soap12', 'http://www.w3.org/2003/05/soap-envelope')
    c = Client(test_url,
        transport=transport,
        prettyxml=True,
    )

    print c
    
    head_node = c.factory.create('cteCabecMsg')
    head_node.cUF = '35' # São Paulo
    head_node.versaoDados = '1.04'
    c.set_options(soapheaders=[head_node])
    
    response = c.service.cteStatusServicoCT()
    print response
    
    ### Agora comparando a mensagem adquirida com a desejada:
    logging.getLogger('suds.client').setLevel(logging.INFO)
    # A mensagem "desejada" foi copiada da documentação oficial em:
    # https://homologacao.nfe.fazenda.sp.gov.br/cteWEB/services/cteStatusServico.asmx?op=cteStatusServicoCT
    desired_message = \
"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Header>
    <cteCabecMsg xmlns="http://www.portalfiscal.inf.br/cte/wsdl/CteStatusServico">
      <cUF>35</cUF>
      <versaoDados>1.04</versaoDados>
    </cteCabecMsg>
  </soap12:Header>
  <soap12:Body>
    <cteDadosMsg xmlns="http://www.portalfiscal.inf.br/cte/wsdl/CteStatusServico"><!-- xml --></cteDadosMsg>
  </soap12:Body>
</soap12:Envelope>"""

    desired_response = c.service.cteStatusServicoCT(__inject={'msg':desired_message})
    
    if response.xMotivo == desired_response.xMotivo:
        print u'\n\nSUCESSO! Resposta idêntica à esperada pela documentação'