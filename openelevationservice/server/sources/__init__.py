from openelevationservice.server.sources import srtm, gmted, etopo1

PROVIDER_MAPPING = {
    'srtm': srtm.Srtm,
    'gmted': gmted.Gmted,
    'etopo1': etopo1.Etopo1
}