import pandas as pd
import os
from geoagent.utils.geo_helpers import search_geo_records, get_metadata, download_supp_files

def search(keywords: str, max_records: int):
    return pd.DataFrame(search_geo_records(keywords, max_records)).set_index("accession")

def parse_metadata(geo_ids: list[str], save_path: str):
    meta_infos = {}
    for geo_id in geo_ids:
        meta_infos[geo_id] = get_metadata(geo_id, parse_subsamples=True, save_path=save_path)
    return pd.DataFrame.from_dict(meta_infos, orient="index")

def download_data(geo_ids: list[str], file_types: list[str], save_path: str):
    for geo_id in geo_ids:
        download_supp_files(geo_id, file_types, save_path)
    
if __name__ == "__main__":
    _kw = "immunity"
    _save = "./geo"
    if not os.path.exists(_save):
        os.mkdir(_save)
    search_df = search(_kw, 5)
    geo_ids = list(search_df.index.values)
    meata_df = parse_metadata(geo_ids, _save)
    download_data(geo_ids, [], _save)

