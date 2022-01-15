# Copyright (C) 2022, Mykola Grymalyuk
# Check whether new updates are available for OpenCore Legacy Patcher binary
# Call check_binary_updates() to determine if any updates are available
# Returns dict with Link and Version of the latest binary update if available
import requests
from pathlib import Path


class check_binary_updates:
    def __init__(self, constants):
        self.constants = constants
        self.binary_version = self.constants.patcher_version
        self.binary_version_array = self.binary_version.split(".")
        self.binary_version_array = [int(x) for x in self.binary_version_array]
        self.binary_url = "https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest"

        self.available_binaries = {}

    def verify_network_connection(self, url):
        try:
            response = requests.head(url, timeout=5)
            if response:
                return True
        except (requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError):
            return False
        return False

    def check_if_build_newer(self):
        for i in range(0, 3):
            if self.remote_version_array[i] > self.binary_version_array[i]:
                return True
        return False

    def determine_local_build_type(self):
        if self.constants.gui_mode is True:
            return "GUI"
        else:
            return "TUI"

    def determine_local_build_type_offline(self):
        if (Path(self.constants.payload_path) / f"12-Monterey.zip").exists():
            return True
        else:
            return False

    def determine_remote_type(self, remote_name):
        if "TUI" in remote_name:
            return "TUI"
        elif "GUI" in remote_name:
            return "GUI"
        else:
            return "Unknown"

    def determine_remote_offline_type(self, remote_name):
        if "Offline" in remote_name:
            return True
        else:
            return False

    def check_binary_updates(self):
        print("- Checking for updates...")
        if self.verify_network_connection(self.binary_url):
            print("- Network connection functional")
            response = requests.get(self.binary_url)
            data_set = response.json()
            print("- Retrived latest version data")
            self.remote_version = data_set["tag_name"]
            print(f"- Latest version: {self.remote_version}")
            self.remote_version_array = self.remote_version.split(".")
            self.remote_version_array = [
                int(x) for x in self.remote_version_array
            ]
            if self.check_if_build_newer() is True:
                print("- Remote version is newer")
                for asset in data_set["assets"]:
                    print(f"- Found asset: {asset['name']}")
                    if self.determine_remote_type(
                            asset["name"]) == self.determine_local_build_type(
                            ) and self.determine_remote_offline_type(
                                asset["name"]
                            ) == self.determine_local_build_type_offline():
                        print(f"- Found matching asset: {asset['name']}")
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
                                "Offline":
                                self.determine_remote_offline_type(
                                    asset["name"]),
                                "Github Link":
                                f"https://github.com/dortania/OpenCore-Legacy-Patcher/releases/{self.remote_version}"
                            }
                        })
                        break
                if self.available_binaries:
                    return self.available_binaries
                else:
                    print("- No matching binaries available")
                    return None
        else:
            print("- Failed to connect to GitHub API")
        return None