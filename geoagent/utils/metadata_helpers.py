import pandas as pd

from dataclasses import dataclass


@dataclass
class GSMSuppFile:
    geo_id: str
    files: list[str]

@dataclass
class GSESuppFile:
    geo_id: str
    files: list[str]
    samples: list[GSMSuppFile]


class SuppFileAnalysis:
    def __init__(self, metadata_path: str):
        self.gsm_files: list[GSMSuppFile] = []
        self.gse_files: list[GSESuppFile] = []
        self.meta_df = pd.read_csv(metadata_path, index_col=0)
        self._build_from_dataframe()

    def extract_supp_files_from_gsm_meta(self, meta: dict) -> GSMSuppFile:
        supp_files = [v for k, v in meta.items() if k.startswith("supplementary_file_")]
        supp_files_flatten = [item for sublist in supp_files for item in sublist if item != "NONE"]
        return GSMSuppFile(meta["geo_accession"], supp_files_flatten)
    
    def extract_supp_files_from_gse_meta(self, meta: dict, sub_metas: dict) -> GSESuppFile:
        gsm_supp_files = [self.extract_supp_files_from_gsm_meta(gsm_meta) for gsm_meta in sub_metas.values()]
        return GSESuppFile(meta["geo_accession"], meta["supplementary_file"], gsm_supp_files)

    def _build_from_dataframe(self) -> None:
        for idx, row in self.meta_df.iterrows():
            if idx.startswith("GSE"):
                self.gse_files.append(self.extract_supp_files_from_gse_meta(eval(row["metadata"]), eval(row["sub_metadata"])))
            elif idx.startswith("GSM"):
                self.gsm_files.append(self.extract_supp_files_from_gsm_meta(eval(row["metadata"])))
            else:
                raise ValueError(f"Invalid ID: {idx}")
    
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

    
    def _analyze_gse_file_types(self) -> dict:
        res = {}
        return res
    

    
    def analyze_gses(self):
        n = len(self.gse_files)
        res = {
            "gses": n,
            "avg_gsms_per_gse": sum([len(gse.samples) for gse in self.gse_files]) / n,
            "file_types_in_gse": self._analyze_gse_file_types(),

        }
        return res
            
    



if __name__ == "__main__":
    sfa = SuppFileAnalysis("/Users/panrong/Downloads/immunity10/metadata.csv")
    print(sfa._analyze_gse_file_locations())

git