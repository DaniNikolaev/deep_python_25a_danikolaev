# pylint: disable = deprecated-module
from distutils.core import Extension, setup

module = Extension('custom_json', sources=['custom_json.c'])

setup(name='custom_json',
      version='1.0',
      description='Custom JSON parser',
      ext_modules=[module])
