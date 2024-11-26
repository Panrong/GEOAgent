import os
import pandas as pd

from dataclasses import dataclass
from tqdm import tqdm

from geoagent.utils.file_helpers import wget_ftp_url


@dataclass
class GSMSuppFile:
    geo_id: str
    files: list[str]

@dataclass
class GSESuppFile:
    geo_id: str
    files: list[str]
    samples: list[GSMSuppFile]


class SuppFileHelper:
    def __init__(self, metadata_path: str):
        self.gsm_files: list[GSMSuppFile] = []
        self.gse_files: list[GSESuppFile] = []
        self.meta_df = pd.read_csv(metadata_path, index_col=0)
        self._build_from_dataframe()

    def extract_supp_files_from_gsm_meta(self, meta: dict) -> GSMSuppFile:
        supp_files = [v for k, v in meta.items() if k.startswith("supplementary_file_")]
        supp_files_flatten = [item for sublist in supp_files for item in sublist if item != "NONE"]
        return GSMSuppFile(meta["geo_accession"][0], supp_files_flatten)
    
    def extract_supp_files_from_gse_meta(self, meta: dict, sub_metas: dict) -> GSESuppFile:
        gsm_supp_files = [self.extract_supp_files_from_gsm_meta(gsm_meta) for gsm_meta in sub_metas.values()]
        return GSESuppFile(meta["geo_accession"][0], meta["supplementary_file"], gsm_supp_files)

    def _build_from_dataframe(self) -> None:
        for idx, row in self.meta_df.iterrows():
            if idx.startswith("GSE"):
                self.gse_files.append(self.extract_supp_files_from_gse_meta(eval(row["metadata"]), eval(row["sub_metadata"])))
            elif idx.startswith("GSM"):
                self.gsm_files.append(self.extract_supp_files_from_gsm_meta(eval(row["metadata"])))
            else:
                raise ValueError(f"Invalid ID: {idx}")
            
    def _count_gse_files(self) -> int:
        gse_level_count = 0
        gsm_level_count = 0

        for gse in self.gse_files:
            gse_level_count += len(gse.files)
            for gsm in gse.samples:
                gsm_level_count += len(gsm.files)
        return gse_level_count, gsm_level_count

    def _analyze_gse_file_locations(self) -> dict:
        n = len(self.gse_files)
        gse_only, gsm_only, both, neither = 0, 0, 0, 0
        for gse in self.gse_files:
            has_file_in_gse = True if gse.files else False
            has_file_in_gsm = any([True if gsm.files else False for gsm in gse.samples])
            if has_file_in_gse and has_file_in_gsm:
                both += 1
            elif has_file_in_gse:
                gse_only += 1
            elif has_file_in_gsm:
                gsm_only += 1
            else:
                neither += 1

        return {
            "gse_only": round(gse_only/n, 2),
            "gsm_only": round(gsm_only/n, 2),
            "both": round(both/n, 2),
            "neither": round(neither/n, 2),
        }

    @staticmethod
    def _get_file_types(file: str) -> str:
        base_name = os.path.basename(file)
        parts = base_name.split('.')
        if len(parts) > 2:
            ext = '.'.join(parts[-2:])
        else:
            ext = parts[-1]
        return ext
    
    def _analyze_gse_file_types(self) -> dict:
        gse_level = {}
        gsm_level = {}
        
        for gse in self.gse_files:
            # Check files in GSE level
            for file in gse.files:
                ext = self._get_file_types(file)
                gse_level[ext] = gse_level.get(ext, 0) + 1
            
            # Check files in GSM level
            for gsm in gse.samples:
                for file in gsm.files:
                    ext = self._get_file_types(file)
                    gsm_level[ext] = gsm_level.get(ext, 0) + 1
        
        return {
            "gse_level": gse_level,
            "gsm_level": gsm_level
        }

    def analyze_gses(self):
        n = len(self.gse_files)
        gsm_counts = [len(gse.samples) for gse in self.gse_files]
        gse_level_file_count, gsm_level_file_count = self._count_gse_files()
        res = {
            "gses": n,
            "avg_gsms_per_gse": round(sum(gsm_counts) / n, 2),
            "min_gsms_per_gse": min(gsm_counts),
            "max_gsms_per_gse": max(gsm_counts),
            "file_counts": {
                "gse_level": gse_level_file_count,
                "gsm_level": gsm_level_file_count
            },
            "file_locations": self._analyze_gse_file_locations(),
            "file_types": self._analyze_gse_file_types(),

        }
        return res
    
    def list_all_gse_files(self) -> dict[str, dict]:
        return {gse.geo_id: {
            "gse_level": os.path.basename(gse.files), 
            "gsm_level": {gsm.geo_id: os.path.basename(gsm.files) for gsm in gse.samples}
            } 
            for gse in self.gse_files
        }
    
    def download_all_gse_files(self, cache_dir: str) -> None:
        for gse in tqdm(self.gse_files, desc="Downloading GSE files"):
            gse_dir = os.path.join(cache_dir, gse.geo_id)
            os.makedirs(gse_dir, exist_ok=True)
            
            if gse.files:
                gse_supp_dir = os.path.join(gse_dir, "Supp")
                for file in gse.files:
                    wget_ftp_url(ftp_url=file, data_dir=gse_supp_dir, log_dir=cache_dir)
            
            if gse.samples:
                for gsm in gse.samples:
                    if gsm.files:
                        gsm_level_dir = os.path.join(gse_dir, gsm.geo_id)
                        for file in gsm.files:
                            wget_ftp_url(ftp_url=file, data_dir=gsm_level_dir, log_dir=cache_dir) 
            
if __name__ == "__main__":
    sfa = SuppFileHelper("/Users/panrong/Downloads/immunity10/metadata.csv")
    print(sfa.download_all_gse_files("/Users/panrong/Downloads/immunity10/"))
