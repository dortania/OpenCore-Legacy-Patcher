"""
products.py: Parse products from Software Update Catalog
"""

import datetime
import hashlib
import logging
import zoneinfo

import packaging.version

from functools import cached_property

from opencore_legacy_patcher import constants
from opencore_legacy_patcher.datasets.os_data import os_data

from ..support import network_handler


APPLEDB_API_URL = "https://api.appledb.dev/ios/macOS/main.json"


class AppleDBProducts:
    """
    Fetch InstallAssistants from AppleDB
    """

    def __init__(
        self,
        global_constants: constants.Constants,
        max_install_assistant_version: os_data = os_data.sequoia,
    ) -> None:
        self.constants: constants.Constants = global_constants

        try:
            self.data = (
                network_handler.NetworkUtilities()
                .get(APPLEDB_API_URL, headers={"User-Agent": f"OCLP/{self.constants.patcher_version}"})
                .json()
            )
        except Exception as e:
            self.data = []
            logging.error(f"Failed to fetch AppleDB API response: {e}")
            return

        self.max_ia: os_data = max_install_assistant_version

    def _build_installer_name(self, xnu_major: int, beta: bool) -> str:
        """
        Builds the installer name based on the version and catalog
        """
        try:
            return f"macOS {os_data(xnu_major).name.replace('_', ' ').title()}{' Beta' if beta else ''}"
        except ValueError:
            return f"macOS{' Beta' if beta else ''}"

    def _list_latest_installers_only(self, products: list) -> list:
        """
        List only the latest installers per macOS version

        macOS versions capped at n-3 (n being the latest macOS version)
        """

        supported_versions = {
            os_data(i): [v for v in products if v["InstallAssistant"]["XNUMajor"] == i] for i in range(self.max_ia - 3, self.max_ia + 1)
        }

        for versions in supported_versions.values():
            versions.sort(key=lambda v: (not v["Beta"], packaging.version.parse(v["RawVersion"])), reverse=True)

        return [next(iter(versions)) for versions in supported_versions.values() if versions]

    @cached_property
    def products(self) -> None:
        """
        Returns a list of products from the sucatalog
        """

        _products = []

        for firmware in self.data:
            if firmware.get("internal") or firmware.get("sdk") or firmware.get("rsr"):
                continue

            # AppleDB does not track whether an installer supports the VMM pseudo-identifier,
            # so we will use MacPro7,1, which supports all macOS versions that we care about.
            if "MacPro7,1" not in firmware["deviceMap"]:
                continue

            firmware["raw_version"] = firmware["version"].partition(" ")[0]

            xnu_major = int(firmware["build"][:2])
            beta = firmware.get("beta") or firmware.get("rc")

            details = {
                # Dates in AppleDB are in Cupertino time. There are no times, so pin to 10 AM
                "PostDate": datetime.datetime.fromisoformat(firmware["released"]).replace(
                    # hour=10,
                    # minute=0,
                    # second=0,
                    tzinfo=zoneinfo.ZoneInfo("America/Los_Angeles"),
                ),
                "Title": f"{self._build_installer_name(xnu_major, beta)}",
                "Build": firmware["build"],
                "RawVersion": firmware["raw_version"],
                "Version": firmware["version"],
                "Beta": beta,
                "InstallAssistant": {"XNUMajor": xnu_major},
            }

            if xnu_major > self.max_ia:
                continue

            for source in firmware.get("sources", []):
                if source["type"] != "installassistant":
                    continue

                if "MacPro7,1" not in source["deviceMap"]:
                    continue

                for link in source["links"]:
                    if not link["active"]:
                        continue

                    if not network_handler.NetworkUtilities(link["url"]).validate_link():
                        continue

                    details["InstallAssistant"] |= {
                        "URL": link["url"],
                        "Size": source.get("size", 0),
                        "Checksum": source.get("hashes"),
                    }
                    break
                else:
                    continue

                break

            else:
                # No applicable InstallAssistants, or no active sources
                continue

            _products.append(details)

        _products = sorted(_products, key=lambda x: x["Beta"])
        _deduplicated_products = []
        _seen_builds = set()

        # Prevent RCs that were the final release from showing up
        for product in _products:
            if product["Beta"] and product["Build"] in _seen_builds:
                continue
            _deduplicated_products.append(product)
            _seen_builds.add(product["Build"])

        _deduplicated_products = sorted(
            _deduplicated_products, key=lambda x: (packaging.version.parse(x["RawVersion"]), x["Build"], not x["Beta"])
        )

        return _deduplicated_products

    @cached_property
    def latest_products(self) -> list:
        """
        Returns a list of the latest products from the sucatalog
        """
        return self._list_latest_installers_only(self.products)

    def checksum_for_product(self, product: dict):
        """
        Returns the checksum and algorithm for a given product
        """
        HASH_TO_ALGO = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha2-256": hashlib.sha256, "sha2-512": hashlib.sha512}

        if not product.get("InstallAssistant", {}).get("Checksum"):
            return None, None

        for algo, hash_func in HASH_TO_ALGO.items():
            if algo in product["InstallAssistant"]["Checksum"]:
                return product["InstallAssistant"]["Checksum"][algo], hash_func()

        return None, None
