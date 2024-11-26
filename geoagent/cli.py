import argparse
import json

import os
import pandas as pd

from geoagent.utils.geo_helpers import search_geo_records, get_metadata, download_supp_files
from geoagent.utils.metadata_helpers import SuppFileHelper
# from geoagent.tools import GeoCountMatrixReader



def cli():
    parser = argparse.ArgumentParser(
        description="A CLI tool to run geoagent",
    )

    parser.add_argument("--llm", type=str, default="qwen1.5-72b-chat")
    parser.add_argument("--parallel", type=int, default=1, help="The number of parallel tasks")

    subparsers = parser.add_subparsers(dest="subparser_name")

    search_subparser = subparsers.add_parser("search", help="Search GEO records")
    search_subparser.add_argument("query", type=str, help="The keywords to search")
    search_subparser.add_argument("--limit", type=int, help="The maximum number of results to return", default=10)
    search_subparser.add_argument("--cache_dir", type=str, help="The directory to download the data", required=False, default=None)
    search_subparser.add_argument("--output", type=str, help="The output file path", required=False, default=None)
    
    metadata_subparser = subparsers.add_parser("metadata", help="Extract metadata from searched results")
    metadata_subparser.add_argument("--cache_dir", type=str, help="search result file directory")
    metadata_subparser.add_argument("--download_data", type=bool, help="if download all data", default=False)


    args = parser.parse_args()
    if args.subparser_name == "search":
        results = search_geo_records(args.query, max_records=args.limit)

        if args.cache_dir:
            if not os.path.exists(args.cache_dir):
                os.makedirs(args.cache_dir)
            search_df_path = os.path.join(args.cache_dir, f"search_results.csv")
            pd.DataFrame(results).to_csv(search_df_path, encoding="utf-8")
            geo_ids = [x["accession"] for x in results]
            print(f"Downloading {geo_ids} to {args.cache_dir}")
            for geo_id in geo_ids:
                download_supp_files(geo_id, cache_path=args.cache_dir)

        if args.output:
            pd.DataFrame(results).to_csv(args.output, encoding="utf-8")
        else:
            print(json.dumps(results, indent=2))


    elif args.subparser_name == "metadata":
        root_dir = args.cache_dir
        search_file_path = os.path.join(root_dir, "search_results.csv")
        output_path = os.path.join(root_dir, "metadata.csv")

        geo_ids = pd.read_csv(search_file_path)["accession"].tolist()
        print(f"Extracting metadata for {geo_ids}")

        meta_infos = {}
        for geo_id in geo_ids:
            _geo_soft_dir = os.path.join(root_dir, geo_id, "Soft")
            meta_infos[geo_id] = get_metadata(geo_id, parse_subsamples=True, cache_dir=_geo_soft_dir)
        
        pd.DataFrame.from_dict(meta_infos, orient="index") \
            .to_csv(output_path, encoding="utf-8")
        
        sfh = SuppFileHelper(output_path)
        with open(output_path.replace("metadata.csv", "supp_file_analysis.json"), "w") as f:
            json.dump(sfh.analyze_gses(), f, indent=4)

        print("x")
        if args.download_data:
            # to-do: download all files
            pass

    
    elif args.subparser_name == "count_matrix":
        count_matrix_reader = GeoCountMatrixReader(llm=args.model)
        adata = count_matrix_reader.process_gsm(args.gsm_id)
        adata.write_h5ad(args.output)

    else:
        raise NotImplementedError


if __name__ == "__main__":
    cli()