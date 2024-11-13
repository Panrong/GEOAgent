import argparse
import json

import os
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
from geoagent.utils.geo_helpers import search_geo_records, get_metadata, download_supp_files



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
    
    metadata_subparser = subparsers.add_parser("metadata", help="Extract metadata based on GEO ID")
    metadata_subparser.add_argument("geoids", type=str, help="GEO IDs separated by comma or space")
    metadata_subparser.add_argument("--parse_subsamples", type=bool, help="Whether to parse the subsamples", required=False, default=False)
    metadata_subparser.add_argument("--cache_dir", type=str, help="The cache directory", required=False, default=None)
    metadata_subparser.add_argument("--output", type=str, help="The output file path", required=False, default=None)


    # count_matrix_subparser = subparsers.add_parser(
    #     "count_matrix", help="Read the count matrix from a chosen GEO sample"
    # )
    # count_matrix_subparser.add_argument(
    #     "--gsm_id",
    #     type=str,
    #     help="a valid GEO sample ID",
    #     required=True,
    # )
    # count_matrix_subparser.add_argument(
    #     "--output",
    #     type=str,
    #     required=True,
    #     help="The output h5ad file path",
    # )

    # pipeline_extractor_subparser = subparsers.add_parser(
    #     "pipeline_extractor", help="Extract the pipeline from a given paper"
    # )
    # pipeline_extractor_subparser.add_argument(
    #     "--parsed_paper",
    #     type=str,
    #     help="path to the paper in `md` format",
    #     required=True,
    # )
    # pipeline_extractor_subparser.add_argument(
    #     "--output",
    #     type=str,
    #     help="path to the output pipeline file, html or json",
    #     required=True,
    # )

    args = parser.parse_args()

    if args.subparser_name == "search":
        results = search_geo_records(args.query, max_records=args.limit)

        if args.cache_dir:
            if not os.path.exists(args.cache_dir):
                os.makedirs(args.cache_dir)
            search_df_path = os.path.join(args.cache_dir, f"search_results_{args.query.replace(' ', '%')}.csv")
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
        # Split the input string into a list of GEO IDs
        geo_ids = [_id.strip() for _id in args.geoids.replace(',', ' ').split()]

        meta_infos = {}
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {executor.submit(get_metadata, geo_id, args.parse_subsamples, args.cache_dir): geo_id for geo_id in geo_ids}
            for future in as_completed(futures):
                geo_id = futures[future]
                try:
                    meta_infos[geo_id] = future.result()
                except Exception as e:
                    print(f"Error processing {geo_id}: {e}")
        
        if args.output:
            pd.DataFrame.from_dict(meta_infos, orient="index") \
                .to_csv(args.output, encoding="utf-8")
        else:
            print(json.dumps(meta_infos, indent=2))
        
    # elif args.subparser_name == "count_matrix":
    #     count_matrix_reader = GeoCountMatrixReader(llm=args.model)
    #     adata = count_matrix_reader.process_gsm(args.gsm_id)
    #     adata.write_h5ad(args.output)
    # elif args.subparser_name == "pipeline_extractor":
    #     pipeline_extractor = PipelineExtractor(llm=args.model)

    #     pipeline_extractor.extract_pipeline(args.parsed_paper, args.output)
    else:
        raise NotImplementedError


if __name__ == "__main__":
    cli()