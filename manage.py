# -*- coding: utf-8 -*-

from flask.cli import FlaskGroup

from openelevationservice.server import utils

import os
import logging
import requests
from bs4 import BeautifulSoup

#log = logger(__name__)

#app = create_app()
#cli = FlaskGroup(create_app=create_app)

#@cli.command()
def download():
    """Downloads SRTM tiles to disk"""
    base_url = r'http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/'
    
    # Create session for authentication
    session = requests.Session()
    session.auth = ('data_public', 'GDdci')
    response = session.get(base_url)
    
    soup = BeautifulSoup(response.content)
    
    for link in soup.find_all('a', attrs={'href': lambda x: x.startswith('srtm')}):
        print(link.text)
 
if __name__ == "__main__":
    download()