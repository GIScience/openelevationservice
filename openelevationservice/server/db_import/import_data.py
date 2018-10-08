# -*- coding: utf-8 -*-
from openelevationservice.server.config import SETTINGS

import subprocess
import os

def import_data(tiles_dir):
    pg_settings = SETTINGS['provider_parameters']
    
    cmd = 'raster2pgsql -a -I -C -F -P -M {}/*.tif {} | sudo -u {} psql -d {}'.format(tiles_dir,
                                          pg_settings['table_name'],
                                          pg_settings['user_name'],
                                          pg_settings['db_name']