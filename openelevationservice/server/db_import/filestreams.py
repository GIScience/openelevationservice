# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger

from os import path, environ, getcwd
import requests
import subprocess
import zipfile
from bs4 import BeautifulSoup

try:
    from io import BytesIO
except:
    from StringIO import StringIO
    
log = get_logger(__name__)

def downloaddata(xy_range):
    
    base_url = r'http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/'
    
    # Create session for authentication
    session = requests.Session()
    session.auth = tuple(SETTINGS['srtm_parameters'].values())
    response = session.get(base_url)
    
    soup = BeautifulSoup(response.content)
    
    # First find all 'a' tags starting href with srtm*
    for link in soup.find_all('a', attrs={'href': lambda x: x.startswith('srtm')}):
        link_text = link.text.split('_')
        # Check if referenced geotif link is in xy_range
        if int(link_text[1]) in range(*xy_range[0]) and int(link_text[2].split('.')[0]) in range(*xy_range[1]):
            # Then load the zip data in memory
            with zipfile.ZipFile(BytesIO(session.get(base_url + link.text).content)) as zip_obj:
                # Loop through the files in the zip
                for filename in zip_obj.namelist():
                    # Don't extract the readme.txt
                    if filename != 'readme.txt':
                        data = zip_obj.read(filename)
                        # Write byte contents to file
                        with open(path.join(TILES_DIR, filename), 'wb') as f:
                            f.write(data)
        
            log.debug("Downloaded file {}".format(link.text))
            

def raster2pgsql(xy_range=[[0,73], [0, 25]]):
    
    pg_settings = SETTINGS['provider_parameters']
    
    # Copy all env variables and add PGPASSWORD
    env_current = environ.copy()
    env_current['PGPASSWORD'] = pg_settings['password']
    
    cmd_raster2pgsql = r"raster2pgsql -s 4326 -a -C -P -M -t 50x50 {filename} {tablename} | psql -q -h {host} -p {port} -U {user_name} -d {db_name}"
    # -s: raster SRID
    # -a: append to table (assumes it's been create with 'create()')
    # -C: apply all raster Constraints
    # -P: pad tiles to guarantee all tiles have the same width and height
    # -M: vacuum analyze after import
    # -t: specifies the pixel size of each row. Important to keep low for performance!
  
    cmd_psql = ""
    
    for x in range(*xy_range[0]):
        for y in range(*xy_range[1]):
            filename = path.join(TILES_DIR, 
                                 '_'.join(['srtm',
                                           '{:02d}'.format(x),
                                           '{:02d}'.format(y)
                                           ])
                                            + '.tif')
            
            cmd_raster2pgsql = cmd_raster2pgsql.format(**{'filename': filename,
                                                          'tablename':pg_settings['table_name']},
                                                       **pg_settings)
            
            raster2pgsql = subprocess.Popen(cmd_raster2pgsql, 
                                             stdout=subprocess.DEVNULL, 
                                             stderr=subprocess.PIPE,
                                             shell=True,
                                             env=env_current
                                             )
            
            stdout, stderr = raster2pgsql.communicate()
#            
            if raster2pgsql.returncode != 0:
                raise subprocess.CalledProcessError(1, cmd_raster2pgsql + cmd_psql)
                
            log.debug("Imported file {}".format(filename))