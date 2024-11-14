import os
import pandas as pd
import streamlit as st

from geoagent.utils.geo_helpers import search_geo_records, get_metadata, download_supp_files, list_downloaded_files

def search_records(keywords: str, max_records: int) -> pd.DataFrame:
    print(f"Searching for {keywords} with max {max_records} records")
    return pd.DataFrame(search_geo_records(keywords, max_records)).set_index("accession")

def download_data(search_df: pd.DataFrame, out_dir: str) -> None:
    geo_ids = search_df.index.to_list()
    st.write(f"Save search results...")
    search_df.to_csv(os.path.join(out_dir, "search_df.csv"), encoding="utf-8")
    st.write(f"Total records to download: {len(geo_ids)}") 
    progress_bar = st.progress(0)
    for i, geo_id in enumerate(geo_ids):
        st.write(f"Downloading {geo_id}...")
        download_supp_files(geo_id, out_dir)
        progress_bar.progress((i+1) / len(geo_ids))
    st.write("Download completed!")


def parse_metadata(search_df: pd.DataFrame, out_dir: str, is_parse_subsample: bool) -> pd.DataFrame:
    geo_ids = search_df.index.tolist()
    print(f"Extracting metadata for {geo_ids}")
    metadata_file = os.path.join(out_dir, "metadata.csv")

    meta_infos = {}
    progress_bar = st.progress(0)
    for i, geo_id in enumerate(geo_ids):
        _geo_soft_dir = os.path.join(out_dir, geo_id, "Soft")
        meta_infos[geo_id] = get_metadata(geo_id, parse_subsamples=is_parse_subsample, cache_dir=_geo_soft_dir)
        progress_bar.progress((i+1) / len(geo_ids))
    
    metadata_df = pd.DataFrame.from_dict(meta_infos, orient="index")
    metadata_df.to_csv(metadata_file, encoding="utf-8")

    downloaded_files = list_downloaded_files(out_dir)

    return metadata_df, downloaded_files