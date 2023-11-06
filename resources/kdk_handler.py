# Module for parsing and determining best Kernel Debug Kit for host OS
# Copyright (C) 2022-2023, Dhinak G, Mykola Grymalyuk

import datetime
from pathlib import Path
from typing import cast
import tempfile
import plistlib

import packaging.version
import requests

import subprocess
import os

import logging

from resources import utilities, network_handler, constants
from data import os_data

KDK_INSTALL_PATH: str  = "/Library/Developer/KDKs"
KDK_INFO_PLIST:   str  = "KDKInfo.plist"
KDK_API_LINK:     str  = "https://dortania.github.io/KdkSupportPkg/manifest.json"

KDK_ASSET_LIST:   list = None


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

    def __init__(self, global_constants: constants.Constants,
                 host_build: str, host_version: str,
                 ignore_installed: bool = False, passive: bool = False,
                 check_backups_only: bool = False
        ) -> None:

        self.constants: constants.Constants = global_constants

        self.host_build:   str = host_build    # ex. 20A5384c
        self.host_version: str = host_version  # ex. 11.0.1

        self.passive: bool = passive  # Don't perform actions requiring elevated privileges

        self.ignore_installed:      bool = ignore_installed   # If True, will ignore any installed KDKs and download the latest
        self.check_backups_only:    bool = check_backups_only # If True, will only check for KDK backups, not KDKs already installed
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


    def _get_remote_kdks(self) -> list or None:
        """
        Fetches a list of available KDKs from the KdkSupportPkg API
        Additionally caches the list for future use, avoiding extra API calls

        Returns:
            list: A list of KDKs, sorted by version and date if available. Returns None if the API is unreachable
        """

        global KDK_ASSET_LIST

        logging.info("Pulling KDK list from KdkSupportPkg API")
        if KDK_ASSET_LIST:
            return KDK_ASSET_LIST

        try:
            results = network_handler.NetworkUtilities().get(
                KDK_API_LINK,
                headers={
                    "User-Agent": f"OCLP/{self.constants.patcher_version}"
                },
                timeout=5
            )
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            logging.info("Could not contact KDK API")
            return None

        if results.status_code != 200:
            logging.info("Could not fetch KDK list")
            return None

        KDK_ASSET_LIST = sorted(results.json(), key=lambda x: (packaging.version.parse(x["version"]), datetime.datetime.fromisoformat(x["date"])), reverse=True)

        return KDK_ASSET_LIST


    def _get_latest_kdk(self, host_build: str = None, host_version: str = None) -> None:
        """
        Fetches the latest KDK for the current macOS version

        Parameters:
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
            logging.warning(f"{self.error_msg}")
            return

        self.kdk_installed_path = self._local_kdk_installed()
        if self.kdk_installed_path:
            logging.info(f"KDK already installed ({Path(self.kdk_installed_path).name}), skipping")
            self.kdk_already_installed = True
            self.success = True
            return

        remote_kdk_version = self._get_remote_kdks()

        if remote_kdk_version is None:
            logging.warning("Failed to fetch KDK list, falling back to local KDK matching")

            # First check if a KDK matching the current macOS version is installed
            # ex. 13.0.1 vs 13.0
            loose_version = f"{parsed_version.major}.{parsed_version.minor}"
            logging.info(f"Checking for KDKs loosely matching {loose_version}")
            self.kdk_installed_path = self._local_kdk_installed(match=loose_version, check_version=True)
            if self.kdk_installed_path:
                logging.info(f"Found matching KDK: {Path(self.kdk_installed_path).name}")
                self.kdk_already_installed = True
                self.success = True
                return

            older_version = f"{parsed_version.major}.{parsed_version.minor - 1 if parsed_version.minor > 0 else 0}"
            logging.info(f"Checking for KDKs matching {older_version}")
            self.kdk_installed_path = self._local_kdk_installed(match=older_version, check_version=True)
            if self.kdk_installed_path:
                logging.info(f"Found matching KDK: {Path(self.kdk_installed_path).name}")
                self.kdk_already_installed = True
                self.success = True
                return

            logging.warning(f"Couldn't find KDK matching {host_version} or {older_version}, please install one manually")

            self.error_msg = f"Could not contact KdkSupportPkg API, and no KDK matching {host_version} ({host_build}) or {older_version} was installed.\nPlease ensure you have a network connection or manually install a KDK."

            return

        # First check exact match
        for kdk in remote_kdk_version:
            if (kdk["build"] != host_build):
                continue
            self.kdk_url = kdk["url"]
            self.kdk_url_build = kdk["build"]
            self.kdk_url_version = kdk["version"]
            self.kdk_url_expected_size = kdk["fileSize"]
            self.kdk_url_is_exactly_match = True
            break

        # If no exact match, check for closest match
        if self.kdk_url == "":
            for kdk in remote_kdk_version:
                kdk_version = cast(packaging.version.Version, packaging.version.parse(kdk["version"]))
                if kdk_version > parsed_version:
                    continue
                if kdk_version.major != parsed_version.major:
                    continue
                if kdk_version.minor not in range(parsed_version.minor - 1, parsed_version.minor + 1):
                    continue

                # The KDK list is already sorted by version then date, so the first match is the closest
                self.kdk_closest_match_url = kdk["url"]
                self.kdk_closest_match_url_build = kdk["build"]
                self.kdk_closest_match_url_version = kdk["version"]
                self.kdk_closest_match_url_expected_size = kdk["fileSize"]
                self.kdk_url_is_exactly_match = False
                break

        if self.kdk_url == "":
            if self.kdk_closest_match_url == "":
                logging.warning(f"No KDKs found for {host_build} ({host_version})")
                self.error_msg = f"No KDKs found for {host_build} ({host_version})"
                return
            logging.info(f"No direct match found for {host_build}, falling back to closest match")
            logging.info(f"Closest Match: {self.kdk_closest_match_url_build} ({self.kdk_closest_match_url_version})")

            self.kdk_url = self.kdk_closest_match_url
            self.kdk_url_build = self.kdk_closest_match_url_build
            self.kdk_url_version = self.kdk_closest_match_url_version
            self.kdk_url_expected_size = self.kdk_closest_match_url_expected_size
        else:
            logging.info(f"Direct match found for {host_build} ({host_version})")


        # Check if this KDK is already installed
        self.kdk_installed_path = self._local_kdk_installed(match=self.kdk_url_build)
        if self.kdk_installed_path:
            logging.info(f"KDK already installed ({Path(self.kdk_installed_path).name}), skipping")
            self.kdk_already_installed = True
            self.success = True
            return

        logging.info("Following KDK is recommended:")
        logging.info(f"- KDK Build: {self.kdk_url_build}")
        logging.info(f"- KDK Version: {self.kdk_url_version}")
        logging.info(f"- KDK URL: {self.kdk_url}")

        self.success = True


    def retrieve_download(self, override_path: str = "") -> network_handler.DownloadObject or None:
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
            logging.info("No download required, KDK already installed")
            self.success = True
            return None

        if self.kdk_url == "":
            self.error_msg = "Could not retrieve KDK catalog, no KDK to download"
            logging.error(self.error_msg)
            return None

        logging.info(f"Returning DownloadObject for KDK: {Path(self.kdk_url).name}")
        self.success = True

        kdk_download_path = self.constants.kdk_download_path if override_path == "" else Path(override_path)
        kdk_plist_path = Path(f"{kdk_download_path.parent}/{KDK_INFO_PLIST}") if override_path == "" else Path(f"{Path(override_path).parent}/{KDK_INFO_PLIST}")

        self._generate_kdk_info_plist(kdk_plist_path)
        return network_handler.DownloadObject(self.kdk_url, kdk_download_path)


    def _generate_kdk_info_plist(self, plist_path: str) -> None:
        """
        Generates a KDK Info.plist

        """

        plist_path = Path(plist_path)
        if plist_path.exists():
            plist_path.unlink()

        kdk_dict = {
            "build": self.kdk_url_build,
            "version": self.kdk_url_version,
        }

        try:
            plist_path.touch()
            plistlib.dump(kdk_dict, plist_path.open("wb"), sort_keys=False)
        except Exception as e:
            logging.error(f"Failed to generate KDK Info.plist: {e}")


    def _local_kdk_valid(self, kdk_path: Path) -> bool:
        """
        Validates provided KDK, ensure no corruption

        The reason for this is due to macOS deleting files from the KDK during OS updates,
        similar to how Install macOS.app is deleted during OS updates

        Uses Apple's pkg receipt system to verify the original contents of the KDK

        Parameters:
            kdk_path (Path): Path to KDK

        Returns:
            bool: True if valid, False if invalid
        """

        if not Path(f"{kdk_path}/System/Library/CoreServices/SystemVersion.plist").exists():
            logging.info(f"Corrupted KDK found ({kdk_path.name}), removing due to missing SystemVersion.plist")
            self._remove_kdk(kdk_path)
            return False

        # Get build from KDK
        kdk_plist_data = plistlib.load(Path(f"{kdk_path}/System/Library/CoreServices/SystemVersion.plist").open("rb"))
        if "ProductBuildVersion" not in kdk_plist_data:
            logging.info(f"Corrupted KDK found ({kdk_path.name}), removing due to missing ProductBuildVersion")
            self._remove_kdk(kdk_path)
            return False

        kdk_build = kdk_plist_data["ProductBuildVersion"]

        # Check pkg receipts for this build, will give a canonical list if all files that should be present
        result = subprocess.run(["pkgutil", "--files", f"com.apple.pkg.KDK.{kdk_build}"], capture_output=True)
        if result.returncode != 0:
            # If pkg receipt is missing, we'll fallback to legacy validation
            logging.info(f"pkg receipt missing for {kdk_path.name}, falling back to legacy validation")
            return self._local_kdk_valid_legacy(kdk_path)

        # Go through each line of the pkg receipt and ensure it exists
        for line in result.stdout.decode("utf-8").splitlines():
            if not line.startswith("System/Library/Extensions"):
                continue
            if not Path(f"{kdk_path}/{line}").exists():
                logging.info(f"Corrupted KDK found ({kdk_path.name}), removing due to missing file: {line}")
                self._remove_kdk(kdk_path)
                return False

        return True


    def _local_kdk_valid_legacy(self, kdk_path: Path) -> bool:
        """
        Legacy variant of validating provided KDK
        Uses best guess of files that should be present
        This should ideally never be invoked, but used as a fallback

        Parameters:
            kdk_path (Path): Path to KDK

        Returns:
            bool: True if valid, False if invalid
        """

        KEXT_CATALOG = [
            "System.kext/PlugIns/Libkern.kext/Libkern",
            "apfs.kext/Contents/MacOS/apfs",
            "IOUSBHostFamily.kext/Contents/MacOS/IOUSBHostFamily",
            "AMDRadeonX6000.kext/Contents/MacOS/AMDRadeonX6000",
        ]

        for kext in KEXT_CATALOG:
            if not Path(f"{kdk_path}/System/Library/Extensions/{kext}").exists():
                logging.info(f"Corrupted KDK found, removing due to missing: {kdk_path}/System/Library/Extensions/{kext}")
                self._remove_kdk(kdk_path)
                return False

        return True


    def _local_kdk_installed(self, match: str = None, check_version: bool = False) -> str or None:
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

        # Installed KDKs only
        if self.check_backups_only is False:
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

        # If we can't find a KDK, next check if there's a backup present
        # Check for KDK packages in the same directory as the KDK
        for kdk_pkg in Path(KDK_INSTALL_PATH).iterdir():
            if kdk_pkg.is_dir():
                continue
            if not kdk_pkg.name.endswith(".pkg"):
                continue
            if check_version:
                if match not in kdk_pkg.name:
                    continue
            else:
                if not kdk_pkg.name.endswith(f"{match}.pkg"):
                    continue

            logging.info(f"Found KDK backup: {kdk_pkg.name}")
            if self.passive is False:
                logging.info("Attempting KDK restoration")
                if KernelDebugKitUtilities().install_kdk_pkg(kdk_pkg):
                    logging.info("Successfully restored KDK")
                    return self._local_kdk_installed(match=match, check_version=check_version)
            else:
                # When in passive mode, we're just checking if a KDK could be restored
                logging.info("KDK restoration skipped, running in passive mode")
                return kdk_pkg

        return None


    def _remove_kdk(self, kdk_path: str) -> None:
        """
        Removes provided KDK

        Parameters:
            kdk_path (str): Path to KDK
        """

        if self.passive is True:
            return

        if os.getuid() != 0:
            logging.warning("Cannot remove KDK, not running as root")
            return

        if not Path(kdk_path).exists():
            logging.warning(f"KDK does not exist: {kdk_path}")
            return

        rm_args = ["rm", "-rf" if Path(kdk_path).is_dir() else "-f", kdk_path]

        result = utilities.elevated(rm_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logging.warning(f"Failed to remove KDK: {kdk_path}")
            logging.warning(f"{result.stdout.decode('utf-8')}")
            return

        logging.info(f"Successfully removed KDK: {kdk_path}")


    def _remove_unused_kdks(self, exclude_builds: list = None) -> None:
        """
        Removes KDKs that are not in use

        Parameters:
            exclude_builds (list, optional): Builds to exclude from removal.
                                             If None, defaults to host and closest match builds.
        """

        if self.passive is True:
            return

        if exclude_builds is None:
            exclude_builds = [
                self.kdk_url_build,
                self.kdk_closest_match_url_build,
            ]

        if self.constants.should_nuke_kdks is False:
            return

        if not Path(KDK_INSTALL_PATH).exists():
            return

        logging.info("Cleaning unused KDKs")
        for kdk_folder in Path(KDK_INSTALL_PATH).iterdir():
            if kdk_folder.name.endswith(".kdk") or kdk_folder.name.endswith(".pkg"):
                should_remove = True
                for build in exclude_builds:
                    if kdk_folder.name.endswith(f"_{build}.kdk") or kdk_folder.name.endswith(f"_{build}.pkg"):
                        should_remove = False
                        break
                if should_remove is False:
                    continue
                self._remove_kdk(kdk_folder)


    def validate_kdk_checksum(self, kdk_dmg_path: str = None) -> bool:
        """
        Validates KDK DMG checksum

        Parameters:
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
            logging.info("Error: Kernel Debug Kit checksum verification failed!")
            logging.info(f"Output: {result.stderr.decode('utf-8')}")
            msg = "Kernel Debug Kit checksum verification failed, please try again.\n\nIf this continues to fail, ensure you're downloading on a stable network connection (ie. Ethernet)"
            logging.info(f"{msg}")

            self.error_msg = msg
            return False

        self._remove_unused_kdks()
        self.success = True
        logging.info("Kernel Debug Kit checksum verified")
        return True


class KernelDebugKitUtilities:
    """
    Utilities for KDK handling

    """

    def __init__(self) -> None:
        pass


    def install_kdk_pkg(self, kdk_path: Path) -> bool:
        """
        Installs provided KDK packages

        Parameters:
            kdk_path (Path): Path to KDK package

        Returns:
            bool: True if successful, False if not
        """

        if os.getuid() != 0:
            logging.warning("Cannot install KDK, not running as root")
            return False

        logging.info(f"Installing KDK package: {kdk_path.name}")
        logging.info(f"- This may take a while...")

        # TODO: Check whether enough disk space is available

        result = utilities.elevated(["installer", "-pkg", kdk_path, "-target", "/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logging.info("Failed to install KDK:")
            logging.info(result.stdout.decode('utf-8'))
            if result.stderr:
                logging.info(result.stderr.decode('utf-8'))
            return False

        return True


    def install_kdk_dmg(self, kdk_path: Path, only_install_backup: bool = False) -> bool:
        """
        Installs provided KDK disk image

        Parameters:
            kdk_path (Path): Path to KDK disk image

        Returns:
            bool: True if successful, False if not
        """

        if os.getuid() != 0:
            logging.warning("Cannot install KDK, not running as root")
            return False

        logging.info(f"Extracting downloaded KDK disk image")
        with tempfile.TemporaryDirectory() as mount_point:
            result = subprocess.run(["hdiutil", "attach", kdk_path, "-mountpoint", mount_point, "-nobrowse"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.info("Failed to mount KDK:")
                logging.info(result.stdout.decode('utf-8'))
                return False

            kdk_pkg_path = Path(f"{mount_point}/KernelDebugKit.pkg")

            if not kdk_pkg_path.exists():
                logging.warning("Failed to find KDK package in DMG, likely corrupted!!!")
                self._unmount_disk_image(mount_point)
                return False


            if only_install_backup is False:
                if self.install_kdk_pkg(kdk_pkg_path) is False:
                    self._unmount_disk_image(mount_point)
                    return False

            self._create_backup(kdk_pkg_path, Path(f"{kdk_path.parent}/{KDK_INFO_PLIST}"))
            self._unmount_disk_image(mount_point)

        logging.info("Successfully installed KDK")
        return True

    def _unmount_disk_image(self, mount_point) -> None:
        """
        Unmounts provided disk image silently

        Parameters:
            mount_point (Path): Path to mount point
        """
        subprocess.run(["hdiutil", "detach", mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def _create_backup(self, kdk_path: Path, kdk_info_plist: Path) -> None:
        """
        Creates a backup of the KDK

        Parameters:
            kdk_path (Path): Path to KDK
            kdk_info_plist (Path): Path to KDK Info.plist
        """

        if not kdk_path.exists():
            logging.warning("KDK does not exist, cannot create backup")
            return
        if not kdk_info_plist.exists():
            logging.warning("KDK Info.plist does not exist, cannot create backup")
            return

        kdk_info_dict = plistlib.load(kdk_info_plist.open("rb"))

        if 'version' not in kdk_info_dict or 'build' not in kdk_info_dict:
            logging.warning("Malformed KDK Info.plist provided, cannot create backup")
            return

        if os.getuid() != 0:
            logging.warning("Cannot create KDK backup, not running as root")
            return

        if not Path(KDK_INSTALL_PATH).exists():
            subprocess.run(["mkdir", "-p", KDK_INSTALL_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        kdk_dst_name = f"KDK_{kdk_info_dict['version']}_{kdk_info_dict['build']}.pkg"
        kdk_dst_path = Path(f"{KDK_INSTALL_PATH}/{kdk_dst_name}")

        logging.info(f"Creating backup: {kdk_dst_name}")
        if kdk_dst_path.exists():
            logging.info("Backup already exists, skipping")
            return

        result = utilities.elevated(["cp", "-R", kdk_path, kdk_dst_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logging.info("Failed to create KDK backup:")
            logging.info(result.stdout.decode('utf-8'))