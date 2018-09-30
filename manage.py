# -*- coding: utf-8 -*-

from flask.cli import FlaskGroup

from openelevationservice.server.utils import logger
from openelevationservice.server import SETTINGS

import os
import logging
import requests
import zipfile
from bs4 import BeautifulSoup

try:
    from io import BytesIO
except:
    from StringIO import StringIO

log = logger.get_logger(__name__)

#app = create_app()
#cli = FlaskGroup(create_app=create_app)

#@cli.command()
def download():
    """Downloads SRTM tiles to disk"""
    base_url = r'http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/'
    outdir = os.path.join(os.getcwd(), 'tiles') 
    
    # Create session for authentication
    session = requests.Session()
    session.auth = tuple(SETTINGS['srtm_parameters'].values())
    response = session.get(base_url)
    
    soup = BeautifulSoup(response.content)
    
    # First find all 'a' tags starting href with srtm*
    counter = 0
    for link in soup.find_all('a', attrs={'href': lambda x: x.startswith('srtm')}):
        counter += 1
        if counter == 50:
            break
        else:
            # Then load the zip data in memory
            with zipfile.ZipFile(BytesIO(session.get(base_url + link.text).content)) as zip_obj:
                # Loop through the files in the zip
                for filename in zip_obj.namelist():
                    # Don't extract the readme.txt
                    if filename != 'readme.txt':
                        data = zip_obj.read(filename)
                        # Write byte contents to file
                        with open(os.path.join(outdir, filename), 'wb') as f:
                            f.write(data)
        
        log.debug("Downloaded file {}".format(link.text))
        
 
if __name__ == "__main__":
    download()