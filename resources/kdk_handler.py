
from multiprocessing.spawn import is_forking
from pathlib import Path
import requests, urllib
from resources import utilities

SESSION = requests.Session()

class kernel_debug_kit_handler:


    def __init__(self, constants):
        self.constants = constants


    def get_closest_match(self, host_version: str, host_build: str):
        # Get the closest match to the provided version
        # KDKs are generally a few days late, so we'll rely on N-1 matching

        # Note: AppleDB is manually updated, so this is not a perfect solution

        OS_DATABASE_LINK = "https://api.appledb.dev/main.json"

        newest_build = {
            "name": "",
            "version": "",
            "build": "",
            "date": "",
        }

        print(f"- Checking closest match for: {host_version} build {host_build}")

        results = SESSION.get(OS_DATABASE_LINK)

        if results.status_code != 200:
            print(" - Could not fetch database")
            return None

        results = results.json()

        # Iterate through, find build that is closest to the host version
        # Use date to determine which is closest
        if "ios" in results:
            for variant in results["ios"]:
                if variant["osStr"] == "macOS":

                    name = variant["version"]
                    version = name.split(" ")[0]
                    build = variant["build"]
                    date = variant["released"]

                    if version != host_version:
                        # Check if this is a secuirty update (ie. 13.0.1)
                        version_split = version.split(".")
                        host_version_split = host_version.split(".")
                        if len(version_split) >= 2 and len(host_version_split) >= 2:
                            if not (version_split[0] == host_version_split[0] and version_split[1] == host_version_split[1]):
                                continue
                        else:
                            continue

                    if build == host_build:
                        # Skip, as we want the next closest match
                        continue

                    # Check if this is the newest build
                    if newest_build["date"] == "":
                        newest_build = {
                            "name": name,
                            "version": version,
                            "build": build,
                            "date": date,
                        }

                    else:
                        if date > newest_build["date"]:
                            newest_build = {
                                "name": name,
                                "version": version,
                                "build": build,
                                "date": date,
                            }

        if newest_build["date"] != "":
            print(f"- Closest match: {newest_build['version']} build {newest_build['build']}")
            return self.generate_kdk_link(newest_build["version"], newest_build["build"]), newest_build["build"]

        print(" - Could not find a match")
        return None, ""


    def generate_kdk_link(self, version: str, build: str):
        # Note: cannot do lazy matching as we don't store old version/build numbers nor can we enumerate KDKs from the portal
        URL_TEMPLATE = f"https://download.developer.apple.com/macOS/Kernel_Debug_Kit_{version}_build_{build}/Kernel_Debug_Kit_{version}_build_{build}.dmg"

        return URL_TEMPLATE


    def verify_apple_developer_portal(self, link):
        # Determine whether Apple Developer Portal is up
        # and if the requested file is available

        # Returns following:
        # 0: Portal is up and file is available
        # 1: Portal is up but file is not available
        # 2: Portal is down

        TOKEN_URL_BASE = "https://developerservices2.apple.com/services/download?path="
        remote_path = urllib.parse.urlparse(link).path
        token_url = urllib.parse.urlunparse(urllib.parse.urlparse(TOKEN_URL_BASE)._replace(query=urllib.parse.urlencode({"path": remote_path})))

        try:
            response = SESSION.get(token_url, timeout=5)
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
        error_msg = ""

        if self.is_kdk_installed(build) is True:
            print(" - KDK is already installed")
            return True, error_msg

        # Note: cannot do lazy matching as we don't store old version/build numbers nor can we enumerate KDKs from the portal
        URL_TEMPLATE = self.generate_kdk_link(version, build)

        print(f"- Downloading Apple KDK for macOS {version} build {build}")
        result = self.verify_apple_developer_portal(URL_TEMPLATE)
        if result == 2:
            error_msg = "Could not contact Apple download servers"
            return False, error_msg
        elif result == 0:
            print(" - Downloading KDK")
        elif result == 1:
            print(" - Could not find KDK, finding closest match")
            URL_TEMPLATE, closest_build = self.get_closest_match(version, build)

            if self.is_kdk_installed(closest_build) is True:
                return True, error_msg
            if URL_TEMPLATE is None:
                error_msg = "Could not find KDK for host, nor closest match"
                return False, error_msg
            result = self.verify_apple_developer_portal(URL_TEMPLATE)
            if result == 2:
                error_msg = "Could not contact Apple download servers"
                return False, error_msg
            elif result == 0:
                print(" - Downloading KDK")
            elif result == 1:
                print(" - Could not find KDK")
                error_msg = "Could not find KDK for host on Apple's servers, nor closest match"
                return False, error_msg

        if utilities.download_apple_developer_portal(URL_TEMPLATE, self.constants.kdk_download_path):
            return True, error_msg
        error_msg = "Failed to download KDK"
        return False, error_msg

    def is_kdk_installed(self, build):
        for file in Path("/Library/Developer/KDKs").iterdir():
            if file.is_dir():
                if build in file.name:
                    return True
        return False