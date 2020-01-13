# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.sources.provider import ProviderBase
from openelevationservice.server.db_import import raster_processing

from os import path
import requests
import zipfile

from io import BytesIO

log = get_logger(__name__)


class Etopo1(ProviderBase):

    def __init__(
            self,
            base_url=SETTINGS['tables']['further_sources']['sources']['etopo1']['url'],
            output_raster='bathymetry_raster.tif',
            bbox_extent=SETTINGS['tables']['further_sources']['extent'],
            auth_parameters=None,
            filename='ETOPO1_Bed_g_geotiff.tif'
    ):
        super(Etopo1, self).__init__(base_url, output_raster, bbox_extent, auth_parameters, filename)

    def download_data(self):
        """Download tiles and save to disk."""

        if not path.exists(path.join(TILES_DIR, self.filename)):
            with zipfile.ZipFile(BytesIO(requests.get(self.base_url).content)) as zip_obj:
                # Loop through the files in the zip
                for file in zip_obj.namelist():
                    data = zip_obj.read(file)
                    # Write byte contents to file
                    with open(path.join(TILES_DIR, file), 'wb') as f:
                        f.write(data)
            log.debug("Downloaded file {} to {}".format(file, TILES_DIR))
        else:
            log.debug("{} already exists in {}".format(self.filename, TILES_DIR))

        # clip raster tile by defined extent
        log.info("Starting tile processing ...")
        raster_processing.clip_raster(self.filename, self.output_raster, self.bbox_extent)

    def merge_tiles(self):
        pass
