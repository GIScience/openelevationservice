# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class ProviderBase(ABC):

    def __init__(self, base_url, bbox_extent, auth_parameters=None, xys=None, buffer=None):
        self.base_url = base_url
        self.bbox_extent = bbox_extent
        self.auth_parameters = auth_parameters
        self.xys = xys
        self.buffer = buffer
        super(ProviderBase, self).__init__()

    @abstractmethod
    def download_data(self):
        pass

