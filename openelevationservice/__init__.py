# -*- coding: utf-8 -*-

from os import getcwd, path, environ
from yaml import safe_load

basedir = path.abspath(path.dirname(__file__))
SETTINGS = safe_load(open(path.join(basedir, 'server', 'ops_settings.yml')))
if "TESTING" in environ:
    SETTINGS['provider_parameters']['table_name'] = SETTINGS['provider_parameters']['table_name'] + '_test'

TILES_DIR = path.join(getcwd(), 'tiles')