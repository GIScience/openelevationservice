from openelevationservice.server.sources import srtm, gmted, etopo1, gv_at

PROVIDER_MAPPING = {
    'terrestrial': {'srtm': srtm.Srtm,
                    'gmted': gmted.Gmted},
    'etopo1': etopo1.Etopo1,
    'gv_at': gv_at.Gvat
}
