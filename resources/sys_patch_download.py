# Download PatcherSupportPkg for usage with Root Patching
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

from data import os_data
from resources import utilities
from pathlib import Path
import shutil

class grab_patcher_support_pkg:

    def __init__(self, constants):
        self.constants = constants
    
    def generate_pkg_link(self):
        if self.constants.detected_os == os_data.os_data.monterey:
            os_ver = "12-Monterey"
        elif self.constants.detected_os == os_data.os_data.big_sur:
            os_ver = "11-Big-Sur"
        elif self.constants.detected_os == os_data.os_data.catalina:
            os_ver = "10.15-Catalina"
        elif self.constants.detected_os == os_data.os_data.mojave:
            os_ver = "10.14-Mojave"
        else:
            raise Exception(f"Unsupported OS: {self.constants.detected_os}")
        framework_link = f"{self.constants.url_patcher_support_pkg}{self.constants.patcher_support_pkg_version}/{os_ver}.zip"
        extensions_link = f"{self.constants.url_patcher_support_pkg}{self.constants.patcher_support_pkg_version}/Universal-Extensions.zip"
        return os_ver, extensions_link, framework_link

    def download_files(self):
        os_ver, extensions_link, framework_link = self.generate_pkg_link()
        if Path(self.constants.payload_apple_root_path).exists():
            print("- Removing old Apple Binaries folder")
            # Delete folder
            shutil.rmtree(self.constants.payload_apple_root_path)
        if Path(self.constants.payload_apple_root_path_zip).exists():
            print("- Removing old Apple Binaries zip")
            Path(self.constants.payload_apple_root_path_zip).unlink()

        download_result = None
        local_framework_zip = Path(self.constants.payload_path) / f"{os_ver}.zip"
        local_extensions_zip = Path(self.constants.payload_path) / f"Universal-Extensions.zip"
        if Path(local_framework_zip).exists() and Path(local_extensions_zip).exists():
            print(f"- Found local {os_ver} zip, skipping download")
            print(f"- Duplicating into Apple.zip")
            shutil.copy(local_framework_zip, self.constants.payload_apple_root_path_zip)
            download_result = True
        else:
            print(f"- No local version found, donwloading...")
            if utilities.download_file(extensions_link, self.constants.payload_universal_extensions_zip_path):
                download_result = utilities.download_file(framework_link, self.constants.payload_apple_root_path_zip)

        return download_result, os_ver, extensions_link, framework_link