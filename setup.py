# -*- coding: utf-8 -*-

import os
from setuptools import find_packages
from distutils.core import setup

import re

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements

def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links


setup(
    name = u'PySPED',
    version = '0.1dev_alanjds_branch',
    description = u'Sistema Público de Escrituração Digital em Python',
    author = u'Aristides Caldeira',
    author_email = u'aristides.caldeira@taugars.com.br',
    packages = find_packages(),
    package_data = {'pysped.nfe.manual_401': [os.path.join(u'schema', u'pl_006g', u'*'),
                                              os.path.join(u'schema', u'PL_006j', u'*')],
                    'pysped.nfe.danfe': [os.path.join(u'fonts', u'*')],
                    'pysped.relato_sped': [os.path.join(u'fonts', u'*')],
                    'pysped.xml_sped': [os.path.join(u'schema', u'*'),
                                        os.path.join(u'cadeia-certificadora', u'README'),
                                        os.path.join(u'cadeia-certificadora', u'*.* '),
                                        os.path.join(u'cadeia-certificadora', u'certificados', u'*')]},
    include_package_data=True,
    zip_safe = False,
    dependency_links = ['https://github.com/joaoalf/geraldo/tarball/master#egg=Geraldo-0.4dev_joaoalf_branch'],
    install_requires= parse_requirements('requirements.txt'),
)
