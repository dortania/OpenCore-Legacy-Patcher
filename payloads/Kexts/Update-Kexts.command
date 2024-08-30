#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
import requests
import packaging.version
import tempfile


# For kexts with basic handling requirements
KEXT_DICTIONARY = {

    "Acidanthera": {
        "AirportBrcmFixup": {
            "Repository": "https://github.com/acidanthera/AirportBrcmFixup",
            "Constants Variable": "self.airportbcrmfixup_version",
        },
        # Due to issues with legacy Macs, don't update
        # "AppleALC": {
        #     "Repository": "https://github.com/acidanthera/AppleALC",
        #     "Constants Variable": "self.applealc_version",
        # },
        "BlueToolFixup": {
            "Repository": "https://github.com/acidanthera/BrcmPatchRAM",
            "Constants Variable": "self.bluetool_version",
            "Override": "BrcmPatchRAM",
        },
        "CPUFriend": {
            "Repository": "https://github.com/acidanthera/CPUFriend",
            "Constants Variable": "self.cpufriend_version",
        },
        "CryptexFixup": {
            "Repository": "https://github.com/acidanthera/CryptexFixup",
            "Constants Variable": "self.cryptexfixup_version",
        },
        "DebugEnhancer": {
            "Repository": "https://github.com/acidanthera/DebugEnhancer",
            "Constants Variable": "self.debugenhancer_version",
        },
        "FeatureUnlock": {
            "Repository": "https://github.com/acidanthera/FeatureUnlock",
            "Constants Variable": "self.featureunlock_version",
        },
        "Lilu": {
            "Repository": "https://github.com/acidanthera/Lilu",
            "Constants Variable": "self.lilu_version",
        },
        "NVMeFix": {
            "Repository": "https://github.com/acidanthera/NVMeFix",
            "Constants Variable": "self.nvmefix_version",
        },
        "RestrictEvents": {
            "Repository": "https://github.com/acidanthera/RestrictEvents",
            "Constants Variable": "self.restrictevents_version",
        },
        "RSRHelper": {
            "Repository": "https://github.com/khronokernel/RSRHelper",
            "Constants Variable": "self.rsrhelper_version",
        },
        "WhateverGreen": {
            "Repository": "https://github.com/acidanthera/WhateverGreen",
            "Constants Variable": "self.whatevergreen_version",
        },
    },

    "Misc": {
        "Innie": {
            "Repository": "https://github.com/cdf/Innie",
            "Constants Variable": "self.innie_version",
        },
    },
}



class GenerateKexts:

    def __init__(self):
        self.weg_version =  None
        self.weg_old =      None
        self.lilu_version = None

        self._set_cwd()
        self._iterate_over_kexts()
        self._special_kext_handling()


    def _set_cwd(self):
        # Set working directory to script location
        script_path = Path(__file__).parent.absolute()
        os.chdir(script_path)

    def _special_kext_handling(self):
        # Generate custom WhateverGreen
        if self.weg_version is None or self.lilu_version is None or self.weg_old is None:
            raise Exception("Unable to find latest WEG version!")

        if packaging.version.parse(self.weg_version) <= packaging.version.parse(self.weg_old):
            print("   WEG is up to date!")
            return

        # WhateverGreen
        print("Building modified WhateverGreen...")
        # We have to compile WEG ourselves
        weg_source_url = f"https://github.com/acidanthera/WhateverGreen/archive/refs/tags/{self.weg_version}.zip"
        lilu_url = f"https://github.com/acidanthera/Lilu/releases/download/{self.lilu_version}/Lilu-{self.lilu_version}-DEBUG.zip"
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download source
            weg_source_zip = f"{temp_dir}/WhateverGreen-{self.weg_version}.zip"
            subprocess.run(["/usr/bin/curl", "--location", weg_source_url, "--output", weg_source_zip], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Unzip source
            subprocess.run(["/usr/bin/unzip", weg_source_zip, "-d", temp_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Git clone MacKernelSDK into source
            subprocess.run(["/usr/bin/git", "clone", "https://github.com/acidanthera/MacKernelSDK", f"{temp_dir}/WhateverGreen-{self.weg_version}/MacKernelSDK"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Grab latest Lilu release, debug version
            lilu_zip = f"{temp_dir}/Lilu-{self.lilu_version}-DEBUG.zip"
            subprocess.run(["/usr/bin/curl", "--location", lilu_url, "--output", lilu_zip], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Unzip Lilu into WEG source
            subprocess.run(["/usr/bin/unzip", lilu_zip, "-d", f"{temp_dir}/WhateverGreen-{self.weg_version}"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Apply patch
            patch_path = Path("./Acidanthera/WhateverGreen-Navi-Backlight.patch").absolute()
            subprocess.run(["/usr/bin/git", "apply", patch_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=f"{temp_dir}/WhateverGreen-{self.weg_version}")

            # Build WEG
            for variant in ["Release", "Debug"]:
                subprocess.run(["/usr/bin/xcodebuild", "-configuration", variant], cwd=f"{temp_dir}/WhateverGreen-{self.weg_version}", check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


            # Zip Release
            for variant in ["RELEASE", "DEBUG"]:
                dst_path = Path(f"./Acidanthera/WhateverGreen-v{self.weg_version}-Navi-{variant}.zip").absolute()
                subprocess.run(["/usr/bin/zip", "-r", dst_path, "WhateverGreen.kext"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=f"{temp_dir}/WhateverGreen-{self.weg_version}/build/{'Release' if variant == 'RELEASE' else 'Debug'}")
                if Path(f"./Acidanthera/WhateverGreen-v{self.weg_old}-Navi-{variant}.zip").exists():
                    subprocess.run(["/bin/rm", f"./Acidanthera/WhateverGreen-v{self.weg_old}-Navi-{variant}.zip"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self._update_constants_file("self.whatevergreen_navi_version", f"{self.weg_old}-Navi", f"{self.weg_version}-Navi")


    def _iterate_over_kexts(self):
        for kext_folder in KEXT_DICTIONARY:
            for kext_name in KEXT_DICTIONARY[kext_folder]:
                print(f"Checking {kext_name}...")
                if "Override" in KEXT_DICTIONARY[kext_folder][kext_name]:
                    self._get_latest_release(kext_folder, kext_name, override_kext_zip_name=KEXT_DICTIONARY[kext_folder][kext_name]["Override"])
                else:
                    self._get_latest_release(kext_folder, kext_name)


    def _is_build_nightly(self, kext: str, version: str) -> bool:
        # Load CHANGELOG.md
        changelog_path = Path(f"../../CHANGELOG.md").absolute()
        with open(changelog_path, "r") as changelog_file:
            changelog = changelog_file.read()

        # Check if kext is in changelog
        if kext not in changelog:
            return False

        # Check if kext is 'rolling' or 'nightly'
        for line in changelog.split("\n"):
            if kext in line and version in line:
                if ("rolling" in line or "nightly" in line):
                    return True
                break

        return False


    def _get_latest_release(self, kext_folder, kext_name, override_kext_zip_name=None):
        # Get latest release from GitHub API
        repo_url = KEXT_DICTIONARY[kext_folder][kext_name]["Repository"].replace("https://github.com", "https://api.github.com/repos")
        latest_release = requests.get(f"{repo_url}/releases/latest").json()

        for variant in ["RELEASE", "DEBUG"]:

            if "tag_name" not in latest_release:
                print(f"  Error: {latest_release['message']}")
                continue

            remote_version = latest_release["tag_name"]
            if remote_version.startswith("v"):
                remote_version = remote_version[1:]

            if kext_name == "WhateverGreen":
                self.weg_version = remote_version
            elif kext_name == "Lilu":
                self.lilu_version = remote_version

            local_version = self._get_local_version(kext_folder, kext_name, variant)
            if kext_name == "WhateverGreen":
                self.weg_old = local_version

            if packaging.version.parse(remote_version) <= packaging.version.parse(local_version):
                print(f"  {kext_name} {variant} is up to date: v{local_version}")
                if remote_version == local_version:
                    if self._is_build_nightly(kext_name, local_version) is False:
                        continue
                    print(f"  {kext_name} {variant} is a nightly build, updating...")
                else:
                    continue

            for asset in latest_release["assets"]:
                if not asset["name"].endswith(f"{variant}.zip"):
                    continue
                print(f"  Downloading {kext_name} {variant}: v{remote_version}...")
                zip_name = f"{override_kext_zip_name}-v{remote_version}-{variant}.zip" if override_kext_zip_name else f"{kext_name}-v{remote_version}-{variant}.zip"

                if Path(f"./{kext_folder}/{zip_name.replace(f'v{remote_version}', f'v{local_version}')}").exists():
                    subprocess.run(["/bin/rm", "-rf", f"./{kext_folder}/{zip_name.replace(f'v{remote_version}', f'v{local_version}')}"])
                self._download_file(asset["browser_download_url"], f"./{kext_folder}/{zip_name}", f"{kext_name}.kext")
                self._update_constants_file(KEXT_DICTIONARY[kext_folder][kext_name]["Constants Variable"], local_version, remote_version)

                if override_kext_zip_name:
                    # rename zip file
                    os.rename(f"./{kext_folder}/{zip_name}", f"./{kext_folder}/{kext_name}-v{remote_version}-{variant}.zip")
                    subprocess.run(["/bin/rm", "-rf", f"./{kext_folder}/{kext_name}-v{local_version}-{variant}.zip"])


    def _get_local_version(self, kext_folder, kext_name, variant):
        loose_name_start = f"{kext_name}-v"
        loose_name_end = f"-{variant}.zip"

        for file in Path(f"./{kext_folder}").iterdir():
            if file.name.startswith(loose_name_start) and file.name.endswith(loose_name_end):
                local_version = file.name.replace(loose_name_start, "").replace(loose_name_end, "")
                if local_version.startswith("v"):
                    local_version = local_version[1:]
                return local_version[:5]

        raise Exception(f"Could not find local version for {kext_name} {variant}")


    def _download_file(self, url, file_path, file):
        # Download file
        if Path(file_path).exists():
            os.remove(file_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            download = requests.get(url)
            with open(f"{temp_dir}/temp.zip", "wb") as f:
                f.write(download.content)

            # Unzip file
            subprocess.run(["/usr/bin/unzip", "-q", f"{temp_dir}/temp.zip", "-d", f"{temp_dir}"], check=True)

            print(f"  Moving {file} to {file_path}...")
            # Zip file
            subprocess.run(["/usr/bin/zip", "-q", "-r", Path(file_path).name, file], cwd=f"{temp_dir}", check=True)

            # Move file
            subprocess.run(["/bin/mv", f"{temp_dir}/{Path(file_path).name}", file_path], check=True)


    def _update_constants_file(self, variable_name, old_version, new_version):
        print(f"  Updating {variable_name} to {new_version}...")
        constants_file = Path("../../opencore_legacy_patcher/constants.py")
        if not constants_file.exists():
            raise Exception("Constants file does not exist")
        constants_file_contents = constants_file.read_text()

        # Replace version
        for line in constants_file_contents.splitlines():
            if variable_name in line:
                constants_file_contents = constants_file_contents.replace(line, line.replace(old_version, new_version))
                break

        # Write file
        constants_file.write_text(constants_file_contents)


if __name__ == '__main__':
    GenerateKexts()