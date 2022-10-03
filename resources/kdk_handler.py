# Kernel Debug Kit downloader

import datetime
from typing import cast
import urllib.parse
from pathlib import Path

import packaging.version
import requests

from resources import utilities
from resources.constants import Constants


class kernel_debug_kit_handler:
    def __init__(self, constants: Constants):
        self.constants = constants

    def get_available_kdks(self):
        KDK_API_LINK = "https://kdk-api.dhinak.net/v1"

        print("- Fetching available KDKs")

        results = utilities.SESSION.get(KDK_API_LINK, headers={"User-Agent": f"OCLP/{self.constants.patcher_version}"})

        if results.status_code != 200:
            print(" - Could not fetch KDK list")
            return None

        return results.json().sort(key=lambda x: (packaging.version.parse(x["version"]), datetime.datetime.fromisoformat(x["date"])), reversed=True)

    def get_closest_match_legacy(self, host_version: str, host_build: str):
        # Get the closest match to the provided version
        # KDKs are generally a few days late, so we'll rely on N-1 matching

        # Note: AppleDB is manually updated, so this is not a perfect solution

        OS_DATABASE_LINK = "https://api.appledb.dev/main.json"

        parsed_host_version = cast(packaging.version.Version, packaging.version.parse(host_version))

        print(f"- Checking closest match for: {host_version} build {host_build}")

        results = utilities.SESSION.get(OS_DATABASE_LINK)

        if results.status_code != 200:
            print(" - Could not fetch database")
            return None, ""

        macos_builds = [i for i in results.json()["ios"] if i["osType"] == "macOS"]
        macos_builds.sort(key=lambda x: (packaging.version.parse(x["version"]), datetime.datetime.fromisoformat(x["released"])), reverse=True)

        # Iterate through, find build that is closest to the host version
        # Use date to determine which is closest
        for build_info in macos_builds:
            if build_info["osType"] == "macOS":
                version = cast(packaging.version.Version, packaging.version.parse(build_info["version"]))
                if version == parsed_host_version:
                    # Skip, as we want the next closest match
                    continue
                elif version <= parsed_host_version and version.major == parsed_host_version.major and version.minor == parsed_host_version.minor:
                    # The KDK list is already sorted by date then version, so the first match is the closest
                    print(f"- Closest match: {build_info['version']} build {build_info['build']}")
                    return self.generate_kdk_link(build_info["version"], build_info["build"]), build_info["build"]

        print(" - Could not find a match")
        return None, ""

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
            print(" - Could not contact Apple download servers")
            return 2

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 400 and "The path specified is invalid" in response.text:
                print(" - File does not exist on Apple download servers")
                return 1
            else:
                print(" - Could not request download authorization from Apple download servers")
                return 2
        return 0

    def download_kdk(self, version: str, build: str):
        detected_build = build

        if self.is_kdk_installed(build) is True:
            print(" - KDK is already installed")
            return True, "", detected_build

        download_link = None
        closest_match_download_link = None
        closest_build = ""

        kdk_list = self.get_available_kdks()

        parsed_version = cast(packaging.version.Version, packaging.version.parse(version))

        if kdk_list:
            for kdk in kdk_list:
                kdk_version = cast(packaging.version.Version, packaging.version.parse(kdk["version"]))
                if kdk["build"] == build:
                    download_link = kdk["download_url"]
                elif not closest_match_download_link and kdk_version <= parsed_version and kdk_version.major == parsed_version.major and kdk_version.minor == parsed_version.minor:
                    # The KDK list is already sorted by date then version, so the first match is the closest
                    closest_match_download_link = kdk["download_url"]
                    closest_build = kdk["build"]
        else:
            print(" - Could not fetch KDK list, falling back to brute force")
            download_link = self.generate_kdk_link(version, build)
            closest_match_download_link, closest_build = self.get_closest_match_legacy(version, build)

        print(f"- Downloading Apple KDK for macOS {version} build {build}")
        # download_link is None if no matching KDK is found, so we'll fall back to the closest match
        result = self.verify_apple_developer_portal(download_link) if download_link else 1
        if result == 0:
            print(" - Downloading KDK")
        elif result == 1:
            print(" - Could not find KDK, finding closest match")

            if self.is_kdk_installed(closest_build) is True:
                return True, "", closest_build

            if closest_match_download_link is None:
                return False, "Could not find KDK for host, nor closest match", ""

            result = self.verify_apple_developer_portal(closest_match_download_link)

            if result == 0:
                print(" - Downloading KDK")
                download_link = closest_match_download_link
            elif result == 1:
                print(" - Could not find KDK")
                return False, "Could not find KDK for host on Apple's servers, nor closest match", ""
            elif result == 2:
                return False, "Could not contact Apple download servers", ""
        elif result == 2:
            return False, "Could not contact Apple download servers", ""

        if utilities.download_apple_developer_portal(download_link, self.constants.kdk_download_path):
            return True, "", detected_build
        return False, "Failed to download KDK", ""

    def is_kdk_installed(self, build):
        if Path("/Library/Developer/KDKs").exists():
            for file in Path("/Library/Developer/KDKs").iterdir():
                if file.is_dir():
                    if file.name.endswith(f"{build}.kdk"):
                        return True
        return False
