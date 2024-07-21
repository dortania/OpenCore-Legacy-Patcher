"""
constants.py: Enumerations for sucatalog-py
"""

from enum import StrEnum


class SeedType(StrEnum):
    """
    Enum for catalog types

    Variants:
        DeveloperSeed:  Developer Beta (Part of the Apple Developer Program)
        PublicSeed:     Public Beta
        CustomerSeed:   AppleSeed Program (Generally mirrors DeveloperSeed)
        PublicRelease:  Public Release
    """
    DeveloperSeed: str = "seed"
    PublicSeed:    str = "beta"
    CustomerSeed:  str = "customerseed"
    PublicRelease: str = ""


class CatalogVersion(StrEnum):
    """
    Enum for macOS versions

    Used for generating sucatalog URLs
    """
    SEQUOIA:        str = "15"
    SONOMA:         str = "14"
    VENTURA:        str = "13"
    MONTEREY:       str = "12"
    BIG_SUR:        str = "11"
    BIG_SUR_LEGACY: str = "10.16"
    CATALINA:       str = "10.15"
    MOJAVE:         str = "10.14"
    HIGH_SIERRA:    str = "10.13"
    SIERRA:         str = "10.12"
    EL_CAPITAN:     str = "10.11"
    YOSEMITE:       str = "10.10"
    MAVERICKS:      str = "10.9"
    MOUNTAIN_LION:  str = "mountainlion"
    LION:           str = "lion"
    SNOW_LEOPARD:   str = "snowleopard"
    LEOPARD:        str = "leopard"
    TIGER:          str = ""


class CatalogExtension(StrEnum):
    """
    Enum for catalog extensions

    Used for generating sucatalog URLs
    """
    PLIST: str = ".sucatalog"
    GZIP:  str = ".sucatalog.gz"