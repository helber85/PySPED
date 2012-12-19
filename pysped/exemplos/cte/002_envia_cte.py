# -*- coding: utf-8 -*-

from datetime import datetime
from os.path import abspath, dirname
from pysped.xml_sped.certificado import Certificado
from pysped.uteis import transporte
from pysped.uteis.transporte import Client as SoapClient

FILE_DIR = abspath(dirname(__file__))

if __name__ == '__main__':
    # arquivo 'certificado_caminho.txt' deve conter o caminho para o 'certificado.pfx'
    caminho_certificado = open(FILE_DIR+'/certificado_caminho.txt').read().strip()
    # arquivo 'certificado_senha.txt' deve conter a senha para o 'certificado.pfx'
    senha_certificado = open(FILE_DIR+'/certificado_senha.txt').read().strip()
    
    xml_assinado = open(FILE_DIR+'/xml_teste/000000246_assinado.xml', 'r').read()
    
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    
    test_url = 'https://homologacao.nfe.fazenda.sp.gov.br/cteWEB/services/CteRecepcao.asmx?WSDL'
    socket_factory = transporte.HttpsCertTransport(caminho_certificado,
                                                   caminho_certificado,
                                                   password=senha_certificado)

    c = SoapClient(test_url,
        transport=socket_factory,
        prettyxml=True,
    )
    print c
    
    head_node = c.factory.create('cteCabecMsg')
    head_node.cUF = '35' # São Paulo
    head_node.versaoDados = '1.04'
    c.set_options(soapheaders=[head_node])
    
    resultado = c.service.cteRecepcaoLote(xml_assinado)
    print resultado
