# -*- coding: utf-8 -*-

from openelevationservice import __version__, SETTINGS
import time

class ResponseBuilder():
    """Builds the basis for a query response."""
    
    def __init__(self):
        """
        Initializises the query builder.
        """
        self.attribution = SETTINGS['attribution']
        self.version = __version__
        self.timestamp = int(time.time())