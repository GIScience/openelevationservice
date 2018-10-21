# -*- coding: utf-8 -*-

from openelevationservice.server.api import error_codes


class InvalidUsage(Exception):

    def __init__(self, status_code=500, error_code=None, message=None):
        """
        :param status_code: the HTTP status code
        :type status_code: integer

        :param error_code: internal error code
        :type payload: integer
        
        :param message: custom error message
        :type message: string
        """

        Exception.__init__(self)

        if status_code is not None:
            self.status_code = status_code
            
            if message is None:
                message = error_codes[error_code]
            else:
                message = ' '.join([error_codes[error_code],
                                    message])

            self.error = {
                "code": error_code,
                "message": message
            }

    def to_dict(self):
        rv = dict(self.error or ())
        return rv