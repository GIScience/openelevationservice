# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger

from os import path, environ, getcwd
import requests
import subprocess
import zipfile
from bs4 import BeautifulSoup
import time

try:
    from io import BytesIO
except:
    from StringIO import StringIO

log = get_logger(__name__)


def downloadsrtm(xy_range=None):
    """
    Downlaods SRTM v4.1 tiles as bytestream and saves them to TILES_DIR.
    
    :param xy_range: The range of tiles in x and y as per grid in 
        http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp
        in 'minx, maxx, miny, maxy.
    :type xy_range: comma-separated range string
    """

    if SETTINGS["sources"][0]["type"] == "cgiar_csi":

        base_url = r'http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/'

        # Create session for authentication
        session = requests.Session()

        pw = environ.get('SRTMPASS')
        user = environ.get('SRTMUSER')
        if not user and not pw:
            auth = tuple(SETTINGS['sources'][0]['srtm_parameters'].values())
        else:
            auth = tuple([user, pw])
        session.auth = auth

        log.debug("SRTM credentials: {}".format(session.auth))

        response = session.get(base_url)

        soup = BeautifulSoup(response.content, features="html.parser")

        # First find all 'a' tags starting href with srtm*
        for link in soup.find_all('a', attrs={'href': lambda x: x.startswith('srtm') and x.endswith('.zip')}):
            link_parsed = link.text.split('_')
            link_x = int(link_parsed[1])
            link_y = int(link_parsed[2].split('.')[0])
            # Check if referenced geotif link is in xy_range
            if link_y in range(*xy_range[0]) and link_x in range(*xy_range[1]):
                log.info('yep')
                # Then load the zip data in memory
                if not path.exists(path.join(TILES_DIR, '_'.join(['srtm', str(link_x), str(link_y)]) + '.tif')):
                    with zipfile.ZipFile(BytesIO(session.get(base_url + link.text).content)) as zip_obj:
                        # Loop through the files in the zip
                        for filename in zip_obj.namelist():
                            # Don't extract the readme.txt
                            if filename != 'readme.txt':
                                data = zip_obj.read(filename)
                                # Write byte contents to file
                                with open(path.join(TILES_DIR, filename), 'wb') as f:
                                    f.write(data)
                    log.debug("Downloaded file {} to {}".format(link.text, TILES_DIR))
                else:
                    log.debug("File {} already exists in {}".format(link.text, TILES_DIR))

    else:

        download_folder = SETTINGS["sources"][0]["type"]
        local_path = getcwd() + "/tiles/"

        # run joerd_docker Dockerfile
        proc_image = subprocess.Popen(
            ["sudo", "docker", "build", "--tag=joerdsources", "-f", "./joerd_docker/Dockerfile", "."])

        return_code_image = proc_image.wait()
        if return_code_image is not None:
            # run docker container
            proc_container = subprocess.Popen(["sudo", "docker", "run", "-d", "joerdsources", "bash"])

            return_code_container = proc_container.wait()
            if return_code_container is not None:
                container = subprocess.Popen(["sudo", "docker", "ps", "-lq"],
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE)
                container_id = container.communicate()[0].rstrip().decode('UTF-8')
                print("container_id:", container_id)

                # copy data from docker container to host
                subprocess.Popen(["sudo", "docker", "cp",
                                  container_id + ":/joerd/" + download_folder + "/",
                                  local_path],
                                 stdout=subprocess.PIPE)
            # remove docker container?


def raster2pgsql():
    """
    Imports SRTM v4.1 tiles to PostGIS.
    
    :raises subprocess.CalledProcessError: Raised when raster2pgsql throws an error.
    """

    # Define access rights and arrange folder structure
    if SETTINGS["sources"][0]["type"] != "cgiar_csi":
        download_folder = SETTINGS["sources"][0]["type"]
        local_path = getcwd() + "/tiles/"

        subprocess.Popen("sudo mv " + local_path + download_folder + "/* " + local_path, shell=True)
        time.sleep(1)
        subprocess.Popen("sudo chmod 776 " + local_path + "*", shell=True)
        time.sleep(1)
        subprocess.Popen(["sudo", "rm", "-r", local_path + download_folder])

    pg_settings = SETTINGS['provider_parameters']

    # Copy all env variables and add PGPASSWORD
    env_current = environ.copy()
    env_current['PGPASSWORD'] = pg_settings['password']

    # Tried to import every raster individually by user-specified xyrange 
    # similar to download(), but raster2pgsql fuck it up somehow.. The PostGIS
    # raster will not be what one would expect. Instead doing a bulk import of all files.
    cmd_raster2pgsql = r"raster2pgsql -s 4326 -a -C -M -P -t 50x50 {filename} {table_name} | psql -q -h {host} -p {port} -U {user_name} -d {db_name}"
    # -s: raster SRID
    # -a: append to table (assumes it's been create with 'create()')
    # -C: apply all raster Constraints
    # -P: pad tiles to guarantee all tiles have the same width and height
    # -M: vacuum analyze after import
    # -t: specifies the pixel size of each row. Important to keep low for performance!

    if path.join(TILES_DIR, '*.tif'):
        cmd_raster2pgsql = cmd_raster2pgsql.format(**{'filename': path.join(TILES_DIR, '*.tif'), **pg_settings})
    else:
        cmd_raster2pgsql = cmd_raster2pgsql.format(**{'filename': path.join(TILES_DIR, '*.img'), **pg_settings})

    proc = subprocess.Popen(cmd_raster2pgsql,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True,
                            env=env_current
                            )

#    for line in proc.stdout:
#        log.debug(line.decode())
#    proc.stdout.close()
    return_code = proc.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd_raster2pgsql)
