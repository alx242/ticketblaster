# -*- coding: utf-8 -*-
#
# Handle ticketblaster packaging and distribution
from setuptools import setup

setup(name='ticketblaster',
      version='0.7',
      description='Quick tickets, blasted up using WSGI and a IRC-bot',
      long_description = open('README').read(),
      url='http://github.com/alx242/ticketblaster',
      author='Alexander Schüssler',
      author_email='alex@xalx.net',
      license='MIT',
      packages=['ticketblaster'],
      scripts=['tblaster'],
      zip_safe=False)
