# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.sources.provider import ProviderBase

from os import path
import requests
import zipfile

from io import BytesIO

log = get_logger(__name__)


class Etopo1(ProviderBase):

    def __init__(
            self,
            base_url=SETTINGS['tables']['bathymetry']['sources']['etopo1']['url'],
            bbox_extent=SETTINGS['tables']['bathymetry']['extent']
    ):
        super(Etopo1, self).__init__(base_url, bbox_extent)

    def download_data(self):

        etopo1_filename = 'ETOPO1_Bed_g_geotiff.tif'

        if not path.exists(path.join(TILES_DIR, etopo1_filename)):
            with zipfile.ZipFile(BytesIO(requests.get(self.base_url).content)) as zip_obj:
                # Loop through the files in the zip
                for filename in zip_obj.namelist():
                    data = zip_obj.read(filename)
                    # Write byte contents to file
                    with open(path.join(TILES_DIR, filename), 'wb') as f:
                        f.write(data)
            log.debug("Downloaded file {} to {}".format(filename, TILES_DIR))
        else:
            log.debug("{} already exists in {}".format(etopo1_filename, TILES_DIR))
