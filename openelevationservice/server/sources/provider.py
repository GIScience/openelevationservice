# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class ProviderBase(ABC):

    def __init__(self, base_url, output_raster, bbox_extent=None, auth_parameters=None, filename=None, xys=None, buffer=None):
        self.base_url = base_url
        self.output_raster = output_raster
        self.bbox_extent = bbox_extent
        self.auth_parameters = auth_parameters
        self.filename = filename
        self.xys = xys
        self.buffer = buffer

        super(ProviderBase, self).__init__()

    @abstractmethod
    def download_data(self):
        pass

    # @abstractmethod
    # def merge_tiles(self):
    #     pass
