from enum import Enum


class FileType(Enum):
    RDATA = 1
    MTX = 2
    TABLE = 3
    H5 = 4
    H5AD = 5
    UNKNOWN = 6