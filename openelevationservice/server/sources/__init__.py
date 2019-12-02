from openelevationservice.server.sources import srtm, gmted

PROVIDER_MAPPING = {
    'srtm': srtm.Srtm,
    'gmted': gmted.Gmted
    # 'etopo1': etopo1.Etopo1
}