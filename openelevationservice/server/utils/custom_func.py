from geoalchemy2.functions import GenericFunction

class ST_SnapToGrid(GenericFunction):
    """
    Defines PostGIS function, which is not natively supported by geoalchemy2.
    """
    name = 'ST_SnapToGrid'
    type = None