# Copyright (C) 2022, Mykola Grymalyuk
# Check whether new updates are available for OpenCore Legacy Patcher binary
# Call check_binary_updates() to determine if any updates are available
# Returns dict with Link and Version of the latest binary update if available
import requests
import logging

from resources import network_handler, constants

REPO_LATEST_RELEASE_URL: str = "https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest"


class CheckBinaryUpdates:
    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants

        self.binary_version       = self.constants.patcher_version
        self.binary_version_array = [int(x) for x in self.binary_version.split(".")]


    def _check_if_build_newer(self, remote_version: list = None, local_version: list = None) -> bool:
        """
        Check if the remote version is newer than the local version

        Parameters:
            remote_version (list): Remote version to compare against
            local_version (list): Local version to compare against

        Returns:
            bool: True if remote version is newer, False if not
        """

        if remote_version is None:
            remote_version = self.remote_version_array
        if local_version is None:
            local_version = self.binary_version_array

        # Pad version numbers to match length (ie. 0.1.0 vs 0.1.0.1)
        while len(remote_version) > len(local_version):
            local_version.append(0)
        while len(remote_version) < len(local_version):
            remote_version.append(0)

        for i in range(0, len(remote_version)):
            if int(remote_version[i]) < int(local_version[i]):
                break
            elif int(remote_version[i]) > int(local_version[i]):
                return True

        return False


    def _determine_local_build_type(self) -> str:
        """
        Check if the local build is a GUI or TUI build

        Returns:
            str: "GUI" or "TUI"
        """

        if self.constants.wxpython_variant is True:
            return "GUI"
        else:
            return "TUI"


    def _determine_remote_type(self, remote_name: str) -> str:
        """
        Check if the remote build is a GUI or TUI build

        Parameters:
            remote_name (str): Name of the remote build

        Returns:
            str: "GUI" or "TUI"
        """

        if "TUI" in remote_name:
            return "TUI"
        elif "GUI" in remote_name:
            return "GUI"
        else:
            return "Unknown"


    def check_binary_updates(self) -> dict:
        """
        Check if any updates are available for the OpenCore Legacy Patcher binary

        Returns:
            dict: Dictionary with Link and Version of the latest binary update if available
        """

        available_binaries: list = {}

        if not network_handler.NetworkUtilities(REPO_LATEST_RELEASE_URL).verify_network_connection():
            return None

        response = network_handler.NetworkUtilities().get(REPO_LATEST_RELEASE_URL)
        data_set = response.json()

        self.remote_version = data_set["tag_name"]

        self.remote_version_array = self.remote_version.split(".")
        self.remote_version_array = [int(x) for x in self.remote_version_array]

        if self._check_if_build_newer() is False:
            return None

        for asset in data_set["assets"]:
            logging.info(f"- Found asset: {asset['name']}")
            if self._determine_remote_type(asset["name"]) == self._determine_local_build_type():
                available_binaries.update({
                    asset['name']: {
                        "Name":        asset["name"],
                        "Version":     self.remote_version,
                        "Link":        asset["browser_download_url"],
                        "Type":        self._determine_remote_type(asset["name"]),
                        "Github Link": f"https://github.com/dortania/OpenCore-Legacy-Patcher/releases/{self.remote_version}"
                    }
                })
                return available_binaries

        return None