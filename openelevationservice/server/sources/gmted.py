# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.sources.provider import ProviderBase

from os import path
import requests

log = get_logger(__name__)


class Gmted(ProviderBase):

    def __init__(self,
                 base_url=SETTINGS['tables']['terrestrial']['sources']['gmted']['url'],
                 bbox_extent=SETTINGS['tables']['terrestrial']['extent'],
                 xys=SETTINGS['tables']['terrestrial']['sources']['gmted'],
                 buffer=0.1
                 ):
        super(Gmted, self).__init__(base_url, bbox_extent, xys, buffer)

    def download_data(self):
        """ Download tiles and save to disk. """

        tiles_list = self.tile_selection()

        log.info("{} GMTED tile(s) will be downloaded.".format(len(tiles_list)))
        for tile in tiles_list:
            if not path.exists(path.join(TILES_DIR, tile[0])):
                with open(path.join(TILES_DIR, tile[0]), 'wb') as f:
                    log.info("Starting to download {}".format(tile[0]))
                    f.write(requests.get(tile[1]).content)
                log.info("Downloaded file {} to {}".format(tile[0], TILES_DIR))
            else:
                log.info("{} already exists in {}".format(tile[0], TILES_DIR))

    @staticmethod
    def intersects(buffered_bbox, bbox):

        if buffered_bbox[0] > bbox[2]:
            return False
        if buffered_bbox[1] > bbox[3]:
            return False
        if buffered_bbox[2] < bbox[0]:
            return False
        if buffered_bbox[3] < bbox[1]:
            return False
        return True

    def url_selection(self, bbox_x, bbox_y):

        # file name for chosen region
        res = '300' if self.xys['ys'] == -90 else '075'
        x_name = "%03d%s" % (abs(bbox_x), "E" if bbox_x >= 0 else "W")
        y_name = "%02d%s" % (abs(bbox_y), "N" if bbox_y >= 0 else "S")
        filename = "%(y)s%(x)s_20101117_gmted_mea%(res)s.tif" % dict(res=res, x=x_name, y=y_name)

        # file url for chosen region
        gmted_dir = "%s%03d" % ("E" if bbox_x >= 0 else "W", abs(bbox_x))
        d_name = "/%(res)sdarcsec/mea/%(dir)s/" % dict(res=res, dir=gmted_dir)
        file_url = self.base_url + d_name + filename

        return filename, file_url

    def tile_selection(self):

        # buffer by 0.1 degrees (48px) around bbox to grab neighbouring tiles
        # to ensure that there's no tile edge artefacts.
        buffered_bbox = [self.bbox_extent['min_x'] - self.buffer,
                         self.bbox_extent['min_y'] - self.buffer,
                         self.bbox_extent['max_x'] + self.buffer,
                         self.bbox_extent['max_y'] + self.buffer]

        tiles_to_download = []
        for y in self.xys['ys']:
            for x in self.xys['xs']:
                bbox = [x, y, x + 30, y + 20]
                if self.intersects(buffered_bbox, bbox):
                    filename, file_url = self.url_selection(x, y)
                    tiles_to_download.append([filename, file_url])
                    log.info(filename)

        return tiles_to_download
