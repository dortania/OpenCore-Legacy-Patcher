"""
updates.py: Check for OpenCore Legacy Patcher binary updates

Call check_binary_updates() to determine if any updates are available
Returns dict with Link and Version of the latest binary update if available
"""

import logging

from typing import Optional, Union
from packaging import version

from . import network_handler

from .. import constants


REPO_LATEST_RELEASE_URL: str = "https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest"


class CheckBinaryUpdates:
    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants
        try:
            self.binary_version = version.parse(self.constants.patcher_version)
        except version.InvalidVersion:
            assert self.constants.special_build is True, "Invalid version number for binary"
            # Special builds will not have a proper version number
            self.binary_version = version.parse("0.0.0")

        self.latest_details = None

    def check_if_newer(self, version: Union[str, version.Version]) -> bool:
        """
        Check if the provided version is newer than the local version

        Parameters:
            version (str): Version to compare against

        Returns:
            bool: True if the provided version is newer, False if not
        """
        if self.constants.special_build is True:
            return False

        return self._check_if_build_newer(version, self.binary_version)

    def _check_if_build_newer(self, first_version: Union[str, version.Version], second_version: Union[str, version.Version]) -> bool:
        """
        Check if the first version is newer than the second version

        Parameters:
            first_version_str (str): First version to compare against (generally local)
            second_version_str (str): Second version to compare against (generally remote)

        Returns:
            bool: True if first version is newer, False if not
        """

        if not isinstance(first_version, version.Version):
            try:
                first_version = version.parse(first_version)
            except version.InvalidVersion:
                # Special build > release build: assume special build is newer
                return True

        if not isinstance(second_version, version.Version):
            try:
                second_version = version.parse(second_version)
            except version.InvalidVersion:
                # Release build > special build: assume special build is newer
                return False

        if first_version == second_version:
            if not self.constants.commit_info[0].startswith("refs/tags"):
                # Check for nightly builds
                return True

        return first_version > second_version


    def check_binary_updates(self) -> Optional[dict]:
        """
        Check if any updates are available for the OpenCore Legacy Patcher binary

        Returns:
            dict: Dictionary with Link and Version of the latest binary update if available
        """

        if self.constants.special_build is True:
            # Special builds do not get updates through the updater
            return None

        if self.latest_details:
            # We already checked
            return self.latest_details

        if not network_handler.NetworkUtilities(REPO_LATEST_RELEASE_URL).verify_network_connection():
            return None

        response = network_handler.NetworkUtilities().get(REPO_LATEST_RELEASE_URL)
        data_set = response.json()

        if "tag_name" not in data_set:
            return None

        # The release marked as latest will always be stable, and thus, have a proper version number
        # But if not, let's not crash the program
        try:
            latest_remote_version = version.parse(data_set["tag_name"])
        except version.InvalidVersion:
            return None

        if not self._check_if_build_newer(latest_remote_version, self.binary_version):
            return None

        for asset in data_set["assets"]:
            logging.info(f"Found asset: {asset['name']}")
            if asset["name"] == "OpenCore-Patcher.pkg":
                self.latest_details = {
                    "Name": asset["name"],
                    "Version": latest_remote_version,
                    "Link": asset["browser_download_url"],
                    "Github Link": f"https://github.com/dortania/OpenCore-Legacy-Patcher/releases/{latest_remote_version}",
                }
                return self.latest_details

        return None
