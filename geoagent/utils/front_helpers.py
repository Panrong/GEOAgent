import pandas as pd
import streamlit as st
from geoagent.utils.geo_helpers import search_geo_records, get_metadata, download_supp_files, GEO_PATH

def search_records(keywords: str, max_records: int) -> pd.DataFrame:
    print(f"Searching for {keywords} with max {max_records} records")
    return pd.DataFrame(search_geo_records(keywords, max_records)).set_index("accession")

def parse_metadata(geo_ids: list[str], parse_subsamples: bool=False) -> pd.DataFrame:
    meta_infos = {}
    for geo_id in geo_ids:
        st.write(f"Parsing metadata for {geo_id}")
        meta_infos[geo_id] = get_metadata(geo_id, parse_subsamples)
    return pd.DataFrame.from_dict(meta_infos, orient="index")

def download_data(geo_ids: list[str], file_types: list[str]):
    st.write(f"Total records to download: {len(geo_ids)}")
    st.write(f"--Target file types: {file_types}")
    st.write(f"--Save path: {GEO_PATH}")    
    for geo_id in geo_ids:
        st.write(f"Downloading {geo_id}...")
        download_supp_files(geo_id, file_types)
    st.write("Download completed!")


if __name__ == "__main__":
    result  = search_records("COVID-19", 10)