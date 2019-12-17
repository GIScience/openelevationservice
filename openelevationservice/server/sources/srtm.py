# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.sources.provider import ProviderBase
from openelevationservice.server.db_import import raster_processing

from os import path, environ
import requests
import zipfile
from bs4 import BeautifulSoup

from io import BytesIO

log = get_logger(__name__)


class Srtm(ProviderBase):

    def __init__(
            self,
            base_url=SETTINGS['tables']['terrestrial']['sources']['srtm']['url'],
            output_raster='terrestrial_raster.tif',
            bbox_extent=SETTINGS['tables']['terrestrial']['extent'],
            auth_parameters=SETTINGS['tables']['terrestrial']['sources']['srtm']['srtm_parameters']
    ):
        super(Srtm, self).__init__(base_url, output_raster, bbox_extent, auth_parameters)

    def download_data(self):
        """Download tiles and save to disk."""

        x_list = self.srtm_x_value(self.bbox_extent['min_x'], self.bbox_extent['max_x'])
        y_list = self.srtm_y_value(self.bbox_extent['min_y'], self.bbox_extent['max_y'])

        xy_range = [[int(x_list[0]), int(x_list[-1] + 1)],
                    [int(y_list[0]), int(y_list[-1] + 1)]]

        # Create session for authentication
        session = requests.Session()

        pw = environ.get('SRTMPASS')
        user = environ.get('SRTMUSER')
        if not user and not pw:
            auth = tuple(self.auth_parameters.values())
        else:
            auth = tuple([user, pw])
        session.auth = auth

        log.debug("SRTM credentials: {}".format(session.auth))

        response = session.get(self.base_url)

        soup = BeautifulSoup(response.content, features="html.parser")

        file_counter = 0

        # First find all 'a' tags starting href with srtm*
        for link in soup.find_all('a', attrs={'href': lambda x: x.startswith('srtm') and x.endswith('.zip')}):
            link_parsed = link.text.split('_')
            link_x = int(link_parsed[1])
            link_y = int(link_parsed[2].split('.')[0])
            # Check if referenced geotif link is in xy_range
            if link_y in range(*xy_range[1]) and link_x in range(*xy_range[0]):
                # Then load the zip data in memory
                if not path.exists(path.join(TILES_DIR, '_'.join(['srtm', str(link_x), str(link_y)]) + '.tif')):
                    with zipfile.ZipFile(BytesIO(session.get(self.base_url + link.text).content)) as zip_obj:
                        # Loop through the files in the zip
                        for filename in zip_obj.namelist():
                            if filename.endswith('.tif'):
                                data = zip_obj.read(filename)
                                # Write byte contents to file
                                with open(path.join(TILES_DIR, filename), 'wb') as f:
                                    f.write(data)
                                    file_counter += 1
                    log.debug("Downloaded file {} to {}".format(link.text, TILES_DIR))
                else:
                    log.debug("File {} already exists in {}".format(link.text, TILES_DIR))

        # if only one file exists, clip file by extent
        if file_counter == 1:
            log.info("Starting tile processing ...")
            raster_processing.clip_raster(data, self.output_raster, self.bbox_extent)

    @staticmethod
    def srtm_x_value(x_min, x_max):
        """Define SRTM x value download name."""

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

    @staticmethod
    def srtm_y_value(y_min, y_max):
        """Define SRTM y value download name."""

        y_value_list = []

        lon_min = 55
        lon_max = 60
        y_srtm_value = 1

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

    def merge_tiles(self):
        """Resamples and merges downloaded files to one raster tile."""

        # merge and clip raster by extent
        log.info("Starting tile processing ...")
        merged_filename = raster_processing.merge_raster('srtm_*', 'srtm_merged.tif')

        log.info("Starting tile merging ...")
        raster_processing.clip_raster(merged_filename, self.output_raster, self.bbox_extent)
