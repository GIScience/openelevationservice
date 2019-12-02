# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger

from os import path, environ
import requests
import zipfile
from bs4 import BeautifulSoup

from io import BytesIO

log = get_logger(__name__)


def srtm_x_value(x_min, x_max):
    """ Define SRTM x value download name. """

    x_value_list = []

    lat_min = -180
    lat_max = -175
    x_srtm_value = 1

    for i in range(0, 360):

        if lat_min < x_min <= lat_max:
            if x_min <= x_max:
                x_value_list.append(x_srtm_value)
                x_min += 5
            else:
                return x_value_list
        else:
            lat_min += 5
            lat_max += 5
            x_srtm_value += 1


def srtm_y_value(y_min, y_max):
    """ Define SRTM y value download name. """

    y_value_list = []

    lon_min = 55
    lon_max = 60
    y_srtm_value = 1

    # if lon > 60 or < -60: no data available
    # TODO: no download instead of boarder tiles
    if y_min > 60:
        return y_srtm_value

    elif y_min < -60:
        y_srtm_value = 24
        return y_srtm_value

    else:
        for i in range(0, 120):

            if lon_max > y_min >= lon_min:
                if y_min <= y_max:
                    y_value_list.append(y_srtm_value)
                    y_min += 5
                    if y_min > 60:
                        return y_value_list
                else:
                    return y_value_list
            else:
                lon_min -= 5
                lon_max -= 5
                y_srtm_value += 1

        return y_value_list


def download_srtm():
    """ Download SRTM data. """

    base_url = SETTINGS['tables'][0]['srtm']['sources'][0]['srtm']['url']
    bbox_extent = SETTINGS['tables'][0]['srtm']['extent']

    x_list = srtm_x_value(bbox_extent['min_x'], bbox_extent['max_x'])
    y_list = srtm_y_value(bbox_extent['min_y'], bbox_extent['max_y'])

    xy_range = [[int(x_list[0]), int(x_list[-1] + 1)],
                [int(y_list[0]), int(y_list[-1] + 1)]]

    # Create session for authentication
    session = requests.Session()

    pw = environ.get('SRTMPASS')
    user = environ.get('SRTMUSER')
    if not user and not pw:
        auth = tuple(SETTINGS['tables'][0]['srtm']['sources'][0]['srtm']['srtm_parameters'].values())
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
        if link_y in range(*xy_range[1]) and link_x in range(*xy_range[0]):
            log.info('yep')
            # Then load the zip data in memory
            if not path.exists(path.join(TILES_DIR, '_'.join(['srtm', str(link_x), str(link_y)]) + '.tif')):
                with zipfile.ZipFile(BytesIO(session.get(base_url + link.text).content)) as zip_obj:
                    # Loop through the files in the zip
                    for filename in zip_obj.namelist():
                        # Don't extract the readme.txt
                        # if filename != 'readme.txt':
                        if filename.endswith('.tif'):
                            data = zip_obj.read(filename)
                            # Write byte contents to file
                            with open(path.join(TILES_DIR, filename), 'wb') as f:
                                f.write(data)
                log.debug("Downloaded file {} to {}".format(link.text, TILES_DIR))
            else:
                log.debug("File {} already exists in {}".format(link.text, TILES_DIR))
