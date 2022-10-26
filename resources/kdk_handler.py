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
        KDK_API_LINK = "https://kdk-api.dhinak.net/v1"

        print("- Fetching available KDKs")

        try:
            results = utilities.SESSION.get(KDK_API_LINK, headers={"User-Agent": f"OCLP/{self.constants.patcher_version}"})
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            print("- Could not contact KDK API")
            return None

        if results.status_code != 200:
            print("- Could not fetch KDK list")
            return None

        return sorted(results.json(), key=lambda x: (packaging.version.parse(x["version"]), datetime.datetime.fromisoformat(x["date"])), reverse=True)

    def get_closest_match_legacy(self, host_version: str, host_build: str):
        # Get the closest match to the provided version
        # KDKs are generally a few days late, so we'll rely on N-1 matching

        # Note: AppleDB is manually updated, so this is not a perfect solution

        OS_DATABASE_LINK = "https://api.appledb.dev/main.json"
        VERSION_PATTERN = re.compile(r"\d+\.\d+(\.\d+)?")

        parsed_host_version = cast(packaging.version.Version, packaging.version.parse(host_version))

        print(f"- Checking closest match for: {host_version} build {host_build}")

        try:
            results = utilities.SESSION.get(OS_DATABASE_LINK)
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            print("- Could not contact AppleDB")
            return None, "", ""

        if results.status_code != 200:
            print("- Could not fetch database")
            return None, "", ""

        macos_builds = [i for i in results.json()["ios"] if i["osType"] == "macOS"]
        # If the version is borked, put it at the bottom of the list
        # Would omit it, but can't do that in this lambda
        macos_builds.sort(key=lambda x: (packaging.version.parse(VERSION_PATTERN.match(x["version"]).group() if VERSION_PATTERN.match(x["version"]) else "0.0.0"), datetime.datetime.fromisoformat(x["released"])), reverse=True)  # type: ignore

        # Iterate through, find build that is closest to the host version
        # Use date to determine which is closest
        for build_info in macos_builds:
            if build_info["osType"] == "macOS":
                raw_version = VERSION_PATTERN.match(build_info["version"])
                if not raw_version:
                    # Skip if version is borked
                    continue
                version = cast(packaging.version.Version, packaging.version.parse(raw_version.group()))
                build = build_info["build"]
                if build == host_build:
                    # Skip, as we want the next closest match
                    continue
                elif version <= parsed_host_version and version.major == parsed_host_version.major and version.minor == parsed_host_version.minor:
                    # The KDK list is already sorted by date then version, so the first match is the closest
                    print(f"- Closest match: {version} build {build}")
                    return self.generate_kdk_link(str(version), build), str(version), build

        print("- Could not find a match")
        return None, "", ""

    def generate_kdk_link(self, version: str, build: str):
        return f"https://download.developer.apple.com/macOS/Kernel_Debug_Kit_{version}_build_{build}/Kernel_Debug_Kit_{version}_build_{build}.dmg"

    def verify_apple_developer_portal(self, link):
        # Determine whether Apple Developer Portal is up
        # and if the requested file is available

        # Returns following:
        # 0: Portal is up and file is available
        # 1: Portal is up but file is not available
        # 2: Portal is down

        TOKEN_URL_BASE = "https://developerservices2.apple.com/services/download"
        remote_path = urllib.parse.urlparse(link).path
        token_url = urllib.parse.urlunparse(urllib.parse.urlparse(TOKEN_URL_BASE)._replace(query=urllib.parse.urlencode({"path": remote_path})))

        try:
            response = utilities.SESSION.get(token_url, timeout=5)
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
            print("- Could not contact Apple download servers")
            return 2

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 400 and "The path specified is invalid" in response.text:
                print("- File does not exist on Apple download servers")
                return 1
            else:
                print("- Could not request download authorization from Apple download servers")
                return 2
        return 0

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
                elif not closest_match_download_link and kdk_version <= parsed_version and kdk_version.major == parsed_version.major and (kdk_version.minor == parsed_version.minor or kdk_version.minor == parsed_version.minor - 1):
                    # The KDK list is already sorted by date then version, so the first match is the closest
                    closest_match_download_link = kdk["url"]
                    closest_version = kdk["version"]
                    closest_build = kdk["build"]
        else:
            print("- Could not fetch KDK list, falling back to brute force")
            download_link = self.generate_kdk_link(version, build)
            closest_match_download_link, closest_version, closest_build = self.get_closest_match_legacy(version, build)

        print(f"- Checking for KDK matching macOS {version} build {build}")
        # download_link is None if no matching KDK is found, so we'll fall back to the closest match
        result = self.verify_apple_developer_portal(download_link) if download_link else 1
        if result == 0:
            print("- Downloading KDK")
        elif result == 1:
            print("- Could not find KDK, finding closest match")

            if self.is_kdk_installed(closest_build) is True:
                print(f"- Closet Build ({closest_build}) already installed")
                self.remove_unused_kdks(exclude_builds=[detected_build, closest_build])
                return True, "", closest_build

            if closest_match_download_link is None:
                msg = "Could not find KDK for host, nor closest match"
                print(f"- {msg}")
                return False, msg, ""

            print(f"- Closest match: {closest_version} build {closest_build}")
            result = self.verify_apple_developer_portal(closest_match_download_link)

            if result == 0:
                print("- Downloading KDK")
                download_link = closest_match_download_link
            elif result == 1:
                msg = "Could not find KDK for host on Apple's servers, nor closest match"
                print(f"- {msg}")
                return False, msg, ""
            elif result == 2:
                msg = "Could not contact Apple download servers"
                print(f"- {msg}")
                return False, msg, ""
            else:
                msg = "Unknown error"
                print(f"- {msg}")
                return False, msg, ""
        elif result == 2:
            msg = "Could not contact Apple download servers"
            print(f"- {msg}")
            return False, msg, ""

        if utilities.download_apple_developer_portal(download_link, self.constants.kdk_download_path):
            result = subprocess.run(["hdiutil", "verify", self.constants.kdk_download_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(f"Error: Kernel Debug Kit checksum verification failed!")
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