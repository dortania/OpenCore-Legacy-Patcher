# Copyright (C) 2022, Mykola Grymalyuk
# Check whether new updates are available for OpenCore Legacy Patcher binary
# Call check_binary_updates() to determine if any updates are available
# Returns dict with Link and Version of the latest binary update if available
import requests
import logging

from resources import network_handler, constants

REPO_LATEST_RELEASE_URL: str = "https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest"


class check_binary_updates:
    def __init__(self, global_constants: constants.Constants()):
        self.constants: constants.Constants() = global_constants

        self.binary_version       = self.constants.patcher_version
        self.binary_version_array = [int(x) for x in self.binary_version.split(".")]

        self.available_binaries = {}


    def check_if_build_newer(self, remote_version=None, local_version=None):
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

    def determine_local_build_type(self):
        if self.constants.wxpython_variant is True:
            return "GUI"
        else:
            return "TUI"

    def determine_remote_type(self, remote_name):
        if "TUI" in remote_name:
            return "TUI"
        elif "GUI" in remote_name:
            return "GUI"
        else:
            return "Unknown"

    def check_binary_updates(self):
        # logging.info("- Checking for updates...")
        if network_handler.NetworkUtilities(REPO_LATEST_RELEASE_URL).verify_network_connection():
            # logging.info("- Network connection functional")
            response = requests.get(REPO_LATEST_RELEASE_URL)
            data_set = response.json()
            # logging.info("- Retrieved latest version data")
            self.remote_version = data_set["tag_name"]
            # logging.info(f"- Latest version: {self.remote_version}")
            self.remote_version_array = self.remote_version.split(".")
            self.remote_version_array = [
                int(x) for x in self.remote_version_array
            ]
            if self.check_if_build_newer() is True:
                # logging.info("- Remote version is newer")
                for asset in data_set["assets"]:
                    logging.info(f"- Found asset: {asset['name']}")
                    if self.determine_remote_type(asset["name"]) == self.determine_local_build_type():
                        # logging.info(f"- Found matching asset: {asset['name']}")
                        self.available_binaries.update({
                            asset['name']: {
                                "Name":
                                asset["name"],
                                "Version":
                                self.remote_version,
                                "Link":
                                asset["browser_download_url"],
                                "Type":
                                self.determine_remote_type(asset["name"]),
                                "Github Link":
                                f"https://github.com/dortania/OpenCore-Legacy-Patcher/releases/{self.remote_version}"
                            }
                        })
                        break
                if self.available_binaries:
                    return self.available_binaries
                else:
                    # logging.info("- No matching binaries available")
                    return None
        # else:
            # logging.info("- Failed to connect to GitHub API")
        return None