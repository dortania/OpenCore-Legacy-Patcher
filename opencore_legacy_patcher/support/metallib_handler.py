"""
metallib_handler.py: Library for handling Metal libraries
"""

import logging
import requests
import subprocess
import packaging.version

from typing  import cast
from pathlib import Path

from .  import network_handler, subprocess_wrapper
from .. import constants

from ..datasets import os_data


METALLIB_INSTALL_PATH: str  = "/Library/Application Support/Dortania/MetallibSupportPkg"
METALLIB_API_LINK:     str  = "https://dortania.github.io/MetallibSupportPkg/manifest.json"

METALLIB_ASSET_LIST:   list = None


class MetalLibraryObject:

    def __init__(self, global_constants: constants.Constants,
                 host_build: str, host_version: str,
                 ignore_installed: bool = False, passive: bool = False
        ) -> None:

        self.constants: constants.Constants = global_constants

        self.host_build:   str = host_build    # ex. 20A5384c
        self.host_version: str = host_version  # ex. 11.0.1

        self.passive: bool = passive  # Don't perform actions requiring elevated privileges

        self.ignore_installed:      bool = ignore_installed   # If True, will ignore any installed MetallibSupportPkg PKGs and download the latest
        self.metallib_already_installed: bool = False

        self.metallib_installed_path: str = ""

        self.metallib_url:         str = ""
        self.metallib_url_build:   str = ""
        self.metallib_url_version: str = ""

        self.metallib_url_is_exactly_match: bool = False

        self.metallib_closest_match_url:         str = ""
        self.metallib_closest_match_url_build:   str = ""
        self.metallib_closest_match_url_version: str = ""

        self.success: bool = False

        self.error_msg: str = ""

        self._get_latest_metallib()


    def _get_remote_metallibs(self) -> dict:
        """
        Get the MetallibSupportPkg list from the API
        """

        global METALLIB_ASSET_LIST

        logging.info("Pulling metallib list from MetallibSupportPkg API")
        if METALLIB_ASSET_LIST:
            return METALLIB_ASSET_LIST

        try:
            results = network_handler.NetworkUtilities().get(
                METALLIB_API_LINK,
                headers={
                    "User-Agent": f"OCLP/{self.constants.patcher_version}"
                },
                timeout=5
            )
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            logging.info("Could not contact MetallibSupportPkg API")
            return None

        if results.status_code != 200:
            logging.info("Could not fetch Metallib list")
            return None

        METALLIB_ASSET_LIST = results.json()

        return METALLIB_ASSET_LIST


    def _get_latest_metallib(self) -> None:
        """
        Get the latest MetallibSupportPkg PKG
        """

        parsed_version = cast(packaging.version.Version, packaging.version.parse(self.host_version))

        if os_data.os_conversion.os_to_kernel(str(parsed_version.major)) < os_data.os_data.sequoia:
            self.error_msg = "MetallibSupportPkg is not required for macOS Sonoma or older"
            logging.warning(f"{self.error_msg}")
            return

        self.metallib_installed_path = self._local_metallib_installed()
        if self.metallib_installed_path:
            logging.info(f"metallib already installed ({Path(self.metallib_installed_path).name}), skipping")
            self.metallib_already_installed = True
            self.success = True
            return

        remote_metallib_version = self._get_remote_metallibs()

        if remote_metallib_version is None:
            logging.warning("Failed to fetch metallib list, falling back to local metallib matching")

            # First check if a metallib matching the current macOS version is installed
            # ex. 13.0.1 vs 13.0
            loose_version = f"{parsed_version.major}.{parsed_version.minor}"
            logging.info(f"Checking for metallibs loosely matching {loose_version}")
            self.metallib_installed_path = self._local_metallib_installed(match=loose_version, check_version=True)
            if self.metallib_installed_path:
                logging.info(f"Found matching metallib: {Path(self.metallib_installed_path).name}")
                self.metallib_already_installed = True
                self.success = True
                return

            older_version = f"{parsed_version.major}.{parsed_version.minor - 1 if parsed_version.minor > 0 else 0}"
            logging.info(f"Checking for metallibs matching {older_version}")
            self.metallib_installed_path = self._local_metallib_installed(match=older_version, check_version=True)
            if self.metallib_installed_path:
                logging.info(f"Found matching metallib: {Path(self.metallib_installed_path).name}")
                self.metallib_already_installed = True
                self.success = True
                return

            logging.warning(f"Couldn't find metallib matching {self.host_version} or {older_version}, please install one manually")

            self.error_msg = f"Could not contact MetallibSupportPkg API, and no metallib matching {self.host_version} ({self.host_build}) or {older_version} was installed.\nPlease ensure you have a network connection or manually install a metallib."

            return


        # First check exact match
        for metallib in remote_metallib_version:
            if (metallib["build"] != self.host_build):
                continue
            self.metallib_url = metallib["url"]
            self.metallib_url_build = metallib["build"]
            self.metallib_url_version = metallib["version"]
            self.metallib_url_is_exactly_match = True
            break

        # If no exact match, check for closest match
        if self.metallib_url == "":
            for metallib in remote_metallib_version:
                metallib_version = cast(packaging.version.Version, packaging.version.parse(metallib["version"]))
                if metallib_version > parsed_version:
                    continue
                if metallib_version.major != parsed_version.major:
                    continue
                if metallib_version.minor not in range(parsed_version.minor - 1, parsed_version.minor + 1):
                    continue

                # The metallib list is already sorted by version then date, so the first match is the closest
                self.metallib_closest_match_url = metallib["url"]
                self.metallib_closest_match_url_build = metallib["build"]
                self.metallib_closest_match_url_version = metallib["version"]
                self.metallib_url_is_exactly_match = False
                break

        if self.metallib_url == "":
            if self.metallib_closest_match_url == "":
                logging.warning(f"No metallibs found for {self.host_build} ({self.host_version})")
                self.error_msg = f"No metallibs found for {self.host_build} ({self.host_version})"
                return
            logging.info(f"No direct match found for {self.host_build}, falling back to closest match")
            logging.info(f"Closest Match: {self.metallib_closest_match_url_build} ({self.metallib_closest_match_url_version})")

            self.metallib_url = self.metallib_closest_match_url
            self.metallib_url_build = self.metallib_closest_match_url_build
            self.metallib_url_version = self.metallib_closest_match_url_version
        else:
            logging.info(f"Direct match found for {self.host_build} ({self.host_version})")


        # Check if this metallib is already installed
        self.metallib_installed_path = self._local_metallib_installed(match=self.metallib_url_build)
        if self.metallib_installed_path:
            logging.info(f"metallib already installed ({Path(self.metallib_installed_path).name}), skipping")
            self.metallib_already_installed = True
            self.success = True
            return

        logging.info("Following metallib is recommended:")
        logging.info(f"- metallib Build: {self.metallib_url_build}")
        logging.info(f"- metallib Version: {self.metallib_url_version}")
        logging.info(f"- metallib URL: {self.metallib_url}")

        self.success = True


    def _local_metallib_installed(self, match: str = None, check_version: bool = False) -> str:
        """
        Check if a metallib is already installed
        """

        if self.ignore_installed:
            return None

        if not Path(METALLIB_INSTALL_PATH).exists():
            return None

        for metallib_folder in Path(METALLIB_INSTALL_PATH).iterdir():
            if not metallib_folder.is_dir():
                continue
            if check_version:
                if match not in metallib_folder.name:
                    continue
            else:
                if not metallib_folder.name.endswith(f"-{match}"):
                    continue

            return metallib_folder

        return None


    def retrieve_download(self, override_path: str = "") -> network_handler.DownloadObject:
        """
        Retrieve MetallibSupportPkg PKG download object
        """

        self.success = False
        self.error_msg = ""

        if self.metallib_already_installed:
            logging.info("No download required, metallib already installed")
            self.success = True
            return None

        if self.metallib_url == "":
            self.error_msg = "Could not retrieve metallib catalog, no metallib to download"
            logging.error(self.error_msg)
            return None

        logging.info(f"Returning DownloadObject for metallib: {Path(self.metallib_url).name}")
        self.success = True

        metallib_download_path = self.constants.metallib_download_path if override_path == "" else Path(override_path)
        return network_handler.DownloadObject(self.metallib_url, metallib_download_path)


    def install_metallib(self, metallib: str = None) -> None:
        """
        Install MetallibSupportPkg PKG
        """

        if not self.success:
            logging.error("Cannot install metallib, no metallib was successfully retrieved")
            return False

        if self.metallib_already_installed:
            logging.info("No installation required, metallib already installed")
            return True

        result = subprocess_wrapper.run_as_root([
            "/usr/sbin/installer", "-pkg", metallib if metallib else self.constants.metallib_download_path, "-target", "/"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            subprocess_wrapper.log(result)
            return False

        return True