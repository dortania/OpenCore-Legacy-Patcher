"""
url.py: Generate URL for Software Update Catalog

Usage:
>>> import sucatalog
>>> catalog_url = sucatalog.CatalogURL().url
https://swscan.apple.com/content/catalogs/others/index-15seed-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog
"""

import logging
import plistlib

from .constants import (
    SeedType,
    CatalogVersion,
    CatalogExtension
)

from ..support import network_handler


class CatalogURL:
    """
    Provides URL generation for Software Update Catalog

    Args:
        version   (CatalogVersion):    Version of macOS
        seed      (SeedType):          Seed type
        extension (CatalogExtension):  Extension for the catalog URL
    """
    def __init__(self,
                 version: CatalogVersion = CatalogVersion.TAHOE,
                 seed: SeedType = SeedType.PublicRelease,
                 extension: CatalogExtension = CatalogExtension.PLIST
                 ) -> None:
        self.version   = version
        self.seed      = seed
        self.extension = extension

        self.seed    = self._fix_seed_type()
        self.version = self._fix_version()


    def _fix_seed_type(self) -> SeedType:
        """
        Fixes seed type for URL generation
        """
        # Pre-Mountain Lion lacked seed types
        if self.version in [CatalogVersion.LION, CatalogVersion.SNOW_LEOPARD, CatalogVersion.LEOPARD, CatalogVersion.TIGER]:
            if self.seed != SeedType.PublicRelease:
                logging.warning(f"{self.seed.name} not supported for {self.version.name}, defaulting to PublicRelease")
                return SeedType.PublicRelease

        # Pre-Yosemite lacked PublicSeed/CustomerSeed, thus override to DeveloperSeed
        if self.version in [CatalogVersion.MAVERICKS, CatalogVersion.MOUNTAIN_LION]:
            if self.seed in [SeedType.PublicSeed, SeedType.CustomerSeed]:
                logging.warning(f"{self.seed.name} not supported for {self.version.name}, defaulting to DeveloperSeed")
                return SeedType.DeveloperSeed

        return self.seed


    def _fix_version(self) -> CatalogVersion:
        """
        Fixes version for URL generation
        """
        if self.version == CatalogVersion.BIG_SUR:
            return CatalogVersion.BIG_SUR_LEGACY

        return self.version


    def _fetch_versions_for_url(self) -> list:
        """
        Fetches versions for URL generation
        """
        versions: list = []

        _did_hit_variant: bool = False
        for variant in CatalogVersion:

            # Avoid appending versions newer than the current version
            if variant == self.version:
                _did_hit_variant = True
            if _did_hit_variant is False:
                continue

            # Skip invalid version
            if variant in [CatalogVersion.BIG_SUR, CatalogVersion.TIGER]:
                continue

            versions.append(variant.value)

        if self.version == CatalogVersion.SNOW_LEOPARD:
            # Reverse list pre-Lion (ie. just Snow Leopard, since Lion is a list of one)
            versions = versions[::-1]

        return versions


    def _construct_catalog_url(self) -> str:
        """
        Constructs the catalog URL based on the seed type
        """

        url: str = "https://swscan.apple.com/content/catalogs"

        if self.version == CatalogVersion.TIGER:
            url += "/index"
        else:
            url += "/others/index"

        if self.seed in [SeedType.DeveloperSeed, SeedType.PublicSeed, SeedType.CustomerSeed]:
            url += f"-{self.version.value}"
            if self.version == CatalogVersion.MAVERICKS and self.seed == SeedType.CustomerSeed:
                # Apple previously used 'publicseed' for CustomerSeed in Mavericks
                url += "publicseed"
            else:
                url += f"{self.seed.value}"

        # 10.10 and older don't append versions for CustomerSeed
        if self.seed == SeedType.CustomerSeed and self.version in [
            CatalogVersion.YOSEMITE,
            CatalogVersion.MAVERICKS,
            CatalogVersion.MOUNTAIN_LION,
            CatalogVersion.LION,
            CatalogVersion.SNOW_LEOPARD,
            CatalogVersion.LEOPARD
        ]:
            pass
        else:
            for version in self._fetch_versions_for_url():
                url += f"-{version}"

        if self.version != CatalogVersion.TIGER:
            url += ".merged-1"
        url += self.extension.value

        return url


    def catalog_url_to_seed(self, catalog_url: str) -> SeedType:
        """
        Converts the Catalog URL to a SeedType
        """
        if "beta" in catalog_url:
            return SeedType.PublicSeed
        elif "customerseed" in catalog_url:
            return SeedType.CustomerSeed
        elif "seed" in catalog_url:
            return SeedType.DeveloperSeed
        return SeedType.PublicRelease


    @property
    def url(self) -> str:
        """
        Generate URL for Software Update Catalog

        Returns:
            str: URL for Software Update Catalog
        """
        return self._construct_catalog_url()


    @property
    def url_contents(self) -> dict:
        """
        Return URL contents
        """
        try:
            return plistlib.loads(network_handler.NetworkUtilities().get(self.url).content)
        except Exception as e:
            logging.error(f"Failed to fetch URL contents: {e}")
            return None
