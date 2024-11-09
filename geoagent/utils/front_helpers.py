import pandas as pd
from geoagent.utils.geo_helpers import search_geo_records, get_metadata

def search_records(keywords: str, max_records: int) -> pd.DataFrame:
    print(f"Searching for {keywords} with max {max_records} records")
    return pd.DataFrame(search_geo_records(keywords, max_records)).set_index("accession")

def parse_metadata(geo_ids: list[str]) -> pd.DataFrame:
    print(f"Parsing metadata for {geo_ids}")
    meta_infos = {_id: get_metadata(_id) for _id in geo_ids}
    return pd.DataFrame.from_dict(meta_infos, orient="index")


if __name__ == "__main__":
    result  = search_records("COVID-19", 10)