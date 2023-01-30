# Kernel Debug Kit downloader

import datetime
import re
import urllib.parse
from pathlib import Path
from typing import cast

import packaging.version
import requests

import subprocess

from resources import utilities
from resources.constants import Constants


class kernel_debug_kit_handler:
    def __init__(self, constants: Constants):
        self.constants = constants

    def get_available_kdks(self):
        KDK_API_LINK = "https://raw.githubusercontent.com/dortania/KdkSupportPkg/gh-pages/manifest.json"

        print("- Fetching available KDKs")

        try:
            results = utilities.SESSION.get(KDK_API_LINK, headers={"User-Agent": f"OCLP/{self.constants.patcher_version}"}, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            print("- Could not contact KDK API")
            return None

        if results.status_code != 200:
            print("- Could not fetch KDK list")
            return None

        return sorted(results.json(), key=lambda x: (packaging.version.parse(x["version"]), datetime.datetime.fromisoformat(x["date"])), reverse=True)

    def download_kdk(self, version: str, build: str):
        detected_build = build

        if self.is_kdk_installed(detected_build) is True:
            print("- KDK is already installed")
            self.remove_unused_kdks(exclude_builds=[detected_build])
            return True, "", detected_build

        download_link = None
        closest_match_download_link = None
        closest_version = ""
        closest_build = ""

        kdk_list = self.get_available_kdks()

        parsed_version = cast(packaging.version.Version, packaging.version.parse(version))

        if kdk_list:
            for kdk in kdk_list:
                kdk_version = cast(packaging.version.Version, packaging.version.parse(kdk["version"]))
                if kdk["build"] == build:
                    download_link = kdk["url"]
                elif not closest_match_download_link and kdk_version <= parsed_version and kdk_version.major == parsed_version.major and (kdk_version.minor in range(parsed_version.minor - 1, parsed_version.minor + 1)):
                    # The KDK list is already sorted by version then date, so the first match is the closest
                    closest_match_download_link = kdk["url"]
                    closest_version = kdk["version"]
                    closest_build = kdk["build"]
        else:
            msg = "Could not fetch KDK list"
            print(f"- {msg}")
            return False, msg, ""

        print(f"- Checking for KDK matching macOS {version} build {build}")
        # download_link is None if no matching KDK is found, so we'll fall back to the closest match
        if not download_link:
            print("- Could not find KDK, finding closest match")

            if self.is_kdk_installed(closest_build) is True:
                print(f"- Closest build ({closest_build}) already installed")
                self.remove_unused_kdks(exclude_builds=[detected_build, closest_build])
                return True, "", closest_build

            if closest_match_download_link is None:
                msg = "Could not find KDK for host, nor closest match"
                print(f"- {msg}")
                return False, msg, ""

            print(f"- Closest match: {closest_version} build {closest_build}")
            download_link = closest_match_download_link

        if utilities.verify_network_connection(download_link):
            print("- Downloading KDK")
        else:
            msg = "Could not contact download site"
            print(f"- {msg}")
            return False, msg, ""

        result = utilities.download_file(download_link, self.constants.kdk_download_path)

        if result:
            # TODO: should we use the checksum from the API?
            result = subprocess.run(["hdiutil", "verify", self.constants.kdk_download_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print("Error: Kernel Debug Kit checksum verification failed!")
                print(f"Output: {result.stderr}")
                msg = "Kernel Debug Kit checksum verification failed, please try again.\n\nIf this continues to fail, ensure you're downloading on a stable network connection (ie. Ethernet)"
                print(f"- {msg}")
                return False, msg, ""
            self.remove_unused_kdks(exclude_builds=[detected_build, closest_build])
            return True, "", detected_build
        msg = "Failed to download KDK"
        print(f"- {msg}")
        return False, msg, ""

    def is_kdk_installed(self, build):
        kexts_to_check = [
            "System.kext/PlugIns/Libkern.kext/Libkern",
            "apfs.kext/Contents/MacOS/apfs",
            "IOUSBHostFamily.kext/Contents/MacOS/IOUSBHostFamily",
            "AMDRadeonX6000.kext/Contents/MacOS/AMDRadeonX6000",
        ]

        if Path("/Library/Developer/KDKs").exists():
            for file in Path("/Library/Developer/KDKs").iterdir():
                if file.is_dir():
                    if file.name.endswith(f"{build}.kdk"):
                        for kext in kexts_to_check:
                            if not Path(f"{file}/System/Library/Extensions/{kext}").exists():
                                print(f"- Corrupted KDK found, removing due to missing: {file}/System/Library/Extensions/{kext}")
                                utilities.elevated(["rm", "-rf", file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                                return False
                        return True
        return False

    def remove_unused_kdks(self, exclude_builds=[]):
        if self.constants.should_nuke_kdks is False:
            return

        if not Path("/Library/Developer/KDKs").exists():
            return

        if exclude_builds == []:
            return

        print("- Cleaning unused KDKs")
        for kdk_folder in Path("/Library/Developer/KDKs").iterdir():
            if kdk_folder.is_dir():
                if kdk_folder.name.endswith(".kdk"):
                    should_remove = True
                    for build in exclude_builds:
                        if build != "" and kdk_folder.name.endswith(f"{build}.kdk"):
                            should_remove = False
                            break
                    if should_remove is False:
                        continue
                    print(f"  - Removing {kdk_folder.name}")
                    utilities.elevated(["rm", "-rf", kdk_folder], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def kdk_backup_site(self, build):
        KDK_MIRROR_REPOSITORY = "https://api.github.com/repos/dortania/KdkSupportPkg/releases"

        # Check if tag exists
        catalog = requests.get(KDK_MIRROR_REPOSITORY)
        if catalog.status_code != 200:
            print(f"- Could not contact KDK mirror repository")
            return None

        catalog = catalog.json()

        for release in catalog:
            if release["tag_name"] == build:
                print(f"- Found KDK mirror for build: {build}")
                for asset in release["assets"]:
                    if asset["name"].endswith(".dmg"):
                        return asset["browser_download_url"]

        print(f"- Could not find KDK mirror for build {build}")
        return None