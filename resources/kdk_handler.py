# Module for parsing and determining best Kernel Debug Kit for host OS
# Copyright (C) 2022-2023, Dhinak G, Mykola Grymalyuk

import datetime
from pathlib import Path
from typing import cast
import plistlib

import packaging.version
import requests

import subprocess
import os

import logging

from resources import utilities, network_handler
from resources.constants import Constants
from data import os_data

KDK_INSTALL_PATH = "/Library/Developer/KDKs"
KDK_INFO_PLIST = "KDKInfo.plist"


class KernelDebugKitObject:
    """
    Library for querying and downloading Kernel Debug Kits (KDK) for macOS

    Usage:
        >>> kdk_object = KernelDebugKitObject(constants, host_build, host_version)

        >>> if kdk_object.success:

        >>>     # Query whether a KDK is already installed
        >>>     if kdk_object.kdk_already_installed:
        >>>         # Use the installed KDK
        >>>         kdk_path = kdk_object.kdk_installed_path

        >>>     else:
        >>>         # Get DownloadObject for the KDK
        >>>         # See network_handler.py's DownloadObject documentation for usage
        >>>         kdk_download_object = kdk_object.retrieve_download()

        >>>         # Once downloaded, recommend verifying KDK's checksum
        >>>         valid = kdk_object.validate_kdk_checksum()

    """

    def __init__(self, constants: Constants, host_build: str, host_version: str, ignore_installed: bool = False):
        self.constants: Constants = constants

        self.host_build:   str = host_build    # ex. 20A5384c
        self.host_version: str = host_version  # ex. 11.0.1

        self.ignore_installed:      bool = ignore_installed  # If True, will ignore any installed KDKs and download the latest
        self.kdk_already_installed: bool = False

        self.kdk_installed_path: str = ""

        self.kdk_url:         str = ""
        self.kdk_url_build:   str = ""
        self.kdk_url_version: str = ""

        self.kdk_url_expected_size: int = 0

        self.kdk_url_is_exactly_match: bool = False

        self.kdk_closest_match_url:         str = ""
        self.kdk_closest_match_url_build:   str = ""
        self.kdk_closest_match_url_version: str = ""

        self.kdk_closest_match_url_expected_size: int = 0

        self.success: bool = False

        self.error_msg: str = ""

        self._get_latest_kdk()


    def _get_remote_kdks(self):
        """
        Fetches a list of available KDKs from the KdkSupportPkg API

        Returns:
            list: A list of KDKs, sorted by version and date if available. Returns None if the API is unreachable
        """

        KDK_API_LINK = "https://raw.githubusercontent.com/dortania/KdkSupportPkg/gh-pages/manifest.json"

        logging.info("- Pulling KDK list from KdkSupportPkg API")

        try:
            results = network_handler.SESSION.get(
                KDK_API_LINK,
                headers={
                    "User-Agent": f"OCLP/{self.constants.patcher_version}"
                },
                timeout=10
            )
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            logging.info("- Could not contact KDK API")
            return None

        if results.status_code != 200:
            logging.info("- Could not fetch KDK list")
            return None

        return sorted(results.json(), key=lambda x: (packaging.version.parse(x["version"]), datetime.datetime.fromisoformat(x["date"])), reverse=True)


    def _get_latest_kdk(self, host_build: str = None, host_version: str = None):
        """
        Fetches the latest KDK for the current macOS version

        Args:
            host_build (str, optional):   The build version of the current macOS version.
                                          If empty, will use the host_build from the class. Defaults to None.
            host_version (str, optional): The version of the current macOS version.
                                          If empty, will use the host_version from the class. Defaults to None.
        """

        if host_build is None and host_version is None:
            host_build   = self.host_build
            host_version = self.host_version

        parsed_version = cast(packaging.version.Version, packaging.version.parse(host_version))

        if os_data.os_conversion.os_to_kernel(str(parsed_version.major)) < os_data.os_data.ventura:
            self.error_msg = "KDKs are not required for macOS Monterey or older"
            logging.warning(f"- {self.error_msg}")
            return

        self.kdk_installed_path = self._local_kdk_installed()
        if self.kdk_installed_path:
            logging.info(f"- KDK already installed ({Path(self.kdk_installed_path).name}), skipping")
            self.kdk_already_installed = True
            self.success = True
            return

        remote_kdk_version = self._get_remote_kdks()

        if remote_kdk_version is None:
            logging.warning("- Failed to fetch KDK list, falling back to local KDK matching")

            # First check if a KDK matching the current macOS version is installed
            # ex. 13.0.1 vs 13.0
            loose_version = f"{parsed_version.major}.{parsed_version.minor}"
            logging.info(f"- Checking for KDKs loosely matching {loose_version}")
            self.kdk_installed_path = self._local_kdk_installed(match=loose_version, check_version=True)
            if self.kdk_installed_path:
                logging.info(f"- Found matching KDK: {Path(self.kdk_installed_path).name}")
                self.success = True
                return

            older_version = f"{parsed_version.major}.{parsed_version.minor - 1 if parsed_version.minor > 0 else 0}"
            logging.info(f"- Checking for KDKs matching {older_version}")
            self.kdk_installed_path = self._local_kdk_installed(match=older_version, check_version=True)
            if self.kdk_installed_path:
                logging.info(f"- Found matching KDK: {Path(self.kdk_installed_path).name}")
                self.success = True
                return

            logging.warning(f"- Couldn't find KDK matching {host_version} or {older_version}, please install one manually")

            self.error_msg = f"Could not contact KdkSupportPkg API, and no KDK matching {host_version} ({host_build}) or {older_version} was installed.\nPlease ensure you have a network connection or manually install a KDK."

            return

        for kdk in remote_kdk_version:
            kdk_version = cast(packaging.version.Version, packaging.version.parse(kdk["version"]))
            if (kdk["build"] == host_build):
                self.kdk_url = kdk["url"]
                self.kdk_url_build = kdk["build"]
                self.kdk_url_version = kdk["version"]
                self.kdk_url_expected_size = kdk["fileSize"]
                self.kdk_url_is_exactly_match = True
                break
            if kdk_version <= parsed_version and kdk_version.major == parsed_version.major and (kdk_version.minor in range(parsed_version.minor - 1, parsed_version.minor + 1)):
                # The KDK list is already sorted by version then date, so the first match is the closest
                self.kdk_closest_match_url = kdk["url"]
                self.kdk_closest_match_url_build = kdk["build"]
                self.kdk_closest_match_url_version = kdk["version"]
                self.kdk_closest_match_url_expected_size = kdk["fileSize"]
                self.kdk_url_is_exactly_match = False
                break

        if self.kdk_url == "":
            if self.kdk_closest_match_url == "":
                logging.warning(f"- No KDKs found for {host_build} ({host_version})")
                self.error_msg = f"No KDKs found for {host_build} ({host_version})"
                return
            logging.info(f"- No direct match found for {host_build}, falling back to closest match")
            logging.info(f"- Closest Match: {self.kdk_closest_match_url_build} ({self.kdk_closest_match_url_version})")

            self.kdk_url = self.kdk_closest_match_url
            self.kdk_url_build = self.kdk_closest_match_url_build
            self.kdk_url_version = self.kdk_closest_match_url_version
            self.kdk_url_expected_size = self.kdk_closest_match_url_expected_size
        else:
            logging.info(f"- Direct match found for {host_build} ({host_version})")


        # Check if this KDK is already installed
        self.kdk_installed_path = self._local_kdk_installed(match=self.kdk_url_build)
        if self.kdk_installed_path:
            logging.info(f"- KDK already installed ({Path(self.kdk_installed_path).name}), skipping")
            self.kdk_already_installed = True
            self.success = True
            return

        logging.info("- Following KDK is recommended:")
        logging.info(f"-   KDK Build: {self.kdk_url_build}")
        logging.info(f"-   KDK Version: {self.kdk_url_version}")
        logging.info(f"-   KDK URL: {self.kdk_url}")

        self.success = True


    def retrieve_download(self, override_path: str = ""):
        """
        Returns a DownloadObject for the KDK

        Parameters:
            override_path (str): Override the default download path

        Returns:
            DownloadObject: DownloadObject for the KDK, None if no download required
        """

        self.success = False
        self.error_msg = ""

        if self.kdk_already_installed:
            logging.info("- No download required, KDK already installed")
            self.success = True
            return None

        if self.kdk_url == "":
            self.error_msg = "Could not retrieve KDK catalog, no KDK to download"
            logging.error(self.error_msg)
            return None

        logging.info(f"- Returning DownloadObject for KDK: {Path(self.kdk_url).name}")
        self.success = True

        kdk_download_path = self.constants.kdk_download_path if override_path == "" else Path(override_path)
        kdk_plist_path = Path(f"{kdk_download_path}/{KDK_INFO_PLIST}") if override_path == "" else Path(f"{Path(override_path).parent}/{KDK_INFO_PLIST}")

        self._generate_kdk_info_plist(kdk_plist_path)
        return network_handler.DownloadObject(self.kdk_url, kdk_download_path)


    def _generate_kdk_info_plist(self, plist_path: str):
        """
        Generates a KDK Info.plist

        """

        plist_path = Path(plist_path)
        if plist_path.exists():
            plist_path.unlink()

        kdk_dict = {
            "Build": self.kdk_url_build,
            "Version": self.kdk_url_version,
        }

        try:
            plistlib.dump(kdk_dict, plist_path.open("wb"), sort_keys=False)
        except Exception as e:
            logging.error(f"- Failed to generate KDK Info.plist: {e}")


    def _local_kdk_valid(self, kdk_path: str):
        """
        Validates provided KDK, ensure no corruption

        The reason for this is due to macOS deleting files from the KDK during OS updates,
        similar to how Install macOS.app is deleted during OS updates

        Args:
            kdk_path (str): Path to KDK

        Returns:
            bool: True if valid, False if invalid
        """

        KEXT_CATALOG = [
            "System.kext/PlugIns/Libkern.kext/Libkern",
            "apfs.kext/Contents/MacOS/apfs",
            "IOUSBHostFamily.kext/Contents/MacOS/IOUSBHostFamily",
            "AMDRadeonX6000.kext/Contents/MacOS/AMDRadeonX6000",
        ]

        kdk_path = Path(kdk_path)

        for kext in KEXT_CATALOG:
            if not Path(f"{kdk_path}/System/Library/Extensions/{kext}").exists():
                logging.info(f"- Corrupted KDK found, removing due to missing: {kdk_path}/System/Library/Extensions/{kext}")
                self._remove_kdk(kdk_path)
                return False

        return True


    def _local_kdk_installed(self, match: str = None, check_version: bool = False):
        """
        Checks if KDK matching build is installed
        If so, validates it has not been corrupted

        Parameters:
            match (str): string to match against (ex. build or version)
            check_version (bool): If True, match against version, otherwise match against build

        Returns:
            str: Path to KDK if valid, None if not
        """

        if self.ignore_installed is True:
            return None

        if match is None:
            if check_version:
                match = self.host_version
            else:
                match = self.host_build

        if not Path(KDK_INSTALL_PATH).exists():
            return None

        for kdk_folder in Path(KDK_INSTALL_PATH).iterdir():
            if not kdk_folder.is_dir():
                continue
            if check_version:
                if match not in kdk_folder.name:
                    continue
            else:
                if not kdk_folder.name.endswith(f"{match}.kdk"):
                    continue

            if self._local_kdk_valid(kdk_folder):
                return kdk_folder

        return None


    def _remove_kdk(self, kdk_path: str):
        """
        Removes provided KDK

        Args:
            kdk_path (str): Path to KDK
        """

        if os.getuid() != 0:
            logging.warning("- Cannot remove KDK, not running as root")
            return

        result = utilities.elevated(["rm", "-rf", kdk_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logging.warning(f"- Failed to remove KDK: {kdk_path}")
            logging.warning(f"- {result.stdout.decode('utf-8')}")

        logging.info(f"- Successfully removed KDK: {kdk_path}")


    def _remove_unused_kdks(self, exclude_builds: list = None):
        """
        Removes KDKs that are not in use

        Args:
            exclude_builds (list, optional): Builds to exclude from removal.
                                             If None, defaults to host and closest match builds.
        """


        if exclude_builds is None:
            exclude_builds = [
                self.kdk_url_build,
                self.kdk_closest_match_url_build,
            ]

        if self.constants.should_nuke_kdks is False:
            return

        if not Path(KDK_INSTALL_PATH).exists():
            return

        logging.info("- Cleaning unused KDKs")
        for kdk_folder in Path(KDK_INSTALL_PATH).iterdir():
            if kdk_folder.is_dir():
                if kdk_folder.name.endswith(".kdk"):
                    should_remove = True
                    for build in exclude_builds:
                        if build != "" and kdk_folder.name.endswith(f"{build}.kdk"):
                            should_remove = False
                            break
                    if should_remove is False:
                        continue
                    self._remove_kdk(kdk_folder)


    def validate_kdk_checksum(self, kdk_dmg_path: str = None):
        """
        Validates KDK DMG checksum

        Args:
            kdk_dmg_path (str, optional): Path to KDK DMG. Defaults to None.

        Returns:
            bool: True if valid, False if invalid
        """

        self.success = False
        self.error_msg = ""

        if kdk_dmg_path is None:
            kdk_dmg_path = self.constants.kdk_download_path

        if not Path(kdk_dmg_path).exists():
            logging.error(f"KDK DMG does not exist: {kdk_dmg_path}")
            return False

        # TODO: should we use the checksum from the API?
        result = subprocess.run(["hdiutil", "verify", self.constants.kdk_download_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logging.info("- Error: Kernel Debug Kit checksum verification failed!")
            logging.info(f"- Output: {result.stderr.decode('utf-8')}")
            msg = "Kernel Debug Kit checksum verification failed, please try again.\n\nIf this continues to fail, ensure you're downloading on a stable network connection (ie. Ethernet)"
            logging.info(f"- {msg}")

            self.error_msg = msg

        self._remove_unused_kdks()

        self.success = True
