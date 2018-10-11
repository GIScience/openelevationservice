# -*- coding: utf-8 -*-

from openelevationservice.server import create_app
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.config import SETTINGS
from openelevationservice.server.db_import.models import db

import os
import requests
import subprocess
import zipfile
from bs4 import BeautifulSoup

try:
    from io import BytesIO
except:
    from StringIO import StringIO

log = get_logger(__name__)
tiles_dir = os.path.join(os.getcwd(), 'tiles')

app = create_app()

@app.cli.command()
def download():
    """Downloads SRTM tiles to disk"""
    base_url = r'http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/'
    
    # Create session for authentication
    session = requests.Session()
    session.auth = tuple(SETTINGS['srtm_parameters'].values())
    response = session.get(base_url)
    
    soup = BeautifulSoup(response.content)
    
    # First find all 'a' tags starting href with srtm*
    for link in soup.find_all('a', attrs={'href': lambda x: x.startswith('srtm')}):
        # Then load the zip data in memory
        with zipfile.ZipFile(BytesIO(session.get(base_url + link.text).content)) as zip_obj:
            # Loop through the files in the zip
            for filename in zip_obj.namelist():
                # Don't extract the readme.txt
                if filename != 'readme.txt':
                    data = zip_obj.read(filename)
                    # Write byte contents to file
                    with open(os.path.join(tiles_dir, filename), 'wb') as f:
                        f.write(data)
        
        log.debug("Downloaded file {}".format(link.text))
        

@app.cli.command()
def create():
    db.create_all()
    log.debug("Table {} was created.".format(SETTINGS['provider_parameters']['table_name']))
    
    
@app.cli.command()
def drop():
    db.drop_all()
    log.debug("Table {} was dropped.".format(SETTINGS['provider_parameters']['table_name']))
    

@app.cli.command()
def importdata(): 
    pg_settings = SETTINGS['provider_parameters']
    log.info("Starting to import data...")
    
    cmd_raster2pgsql = 'raster2pgsql -a -I -C -F -P -M tiles/*.tif {}'.format(pg_settings['table_name'])
    cmd_psql = ' | psql -h {host} -p {port} -U {user_name} -d {db_name}'.format(**pg_settings['host'],)
    
    # Copy all env variables and add PGPASSWORD
    env_current = os.environ.copy()
    # TODO: Resort to passwd file:
    # https://www.postgresql.org/docs/9.6/static/libpq-pgpass.html
    env_current['PGPASSWORD'] = pg_settings['password']
    
    try:
        subprocess_out = subprocess.check_output([cmd_raster2pgsql, cmd_psql], 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.STDOUT,
                                               env=env_current)
    except subprocess.CalledProcessError as e:
        log.error("Shell exited with code: {}\nMessage: {}".format(e.returncode,
                                                                  e.output))
        raise
    
    log.info("Imported data successfully!")
    
if __name__=='__main__':
    create()