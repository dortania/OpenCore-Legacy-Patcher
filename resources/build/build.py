# Class for generating OpenCore Configurations tailored for Macs
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

import copy
import pickle
import plistlib
import shutil
import zipfile
from pathlib import Path
from datetime import date

from resources import constants, utilities
from resources.build import bluetooth, firmware, graphics_audio, support, storage, smbios, security, misc
from resources.build.networking import wired, wireless


def rmtree_handler(func, path, exc_info):
    if exc_info[0] == FileNotFoundError:
        return
    raise  # pylint: disable=misplaced-bare-raise


class build_opencore:
    def __init__(self, model, versions):
        self.model = model
        self.config = None
        self.constants: constants.Constants = versions


    def build_efi(self):
        utilities.cls()
        if not self.constants.custom_model:
            print(f"Building Configuration on model: {self.model}")
        else:
            print(f"Building Configuration for external model: {self.model}")

        self.generate_base()
        self.set_revision()

        # Set Lilu and co.
        support.build_support(self.model, self.constants, self.config).enable_kext("Lilu.kext", self.constants.lilu_version, self.constants.lilu_path)
        self.config["Kernel"]["Quirks"]["DisableLinkeditJettison"] = True

        # Due to regression in AppleALC 1.6.4+, temporarily use 1.6.3 and set override
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += "-lilubetaall"

        # Call support functions
        firmware.build_firmware(self.model, self.constants, self.config).build()
        wired.build_wired(self.model, self.constants, self.config).build()
        wireless.build_wireless(self.model, self.constants, self.config).build()
        graphics_audio.build_graphics_audio(self.model, self.constants, self.config).build()
        bluetooth.build_bluetooth(self.model, self.constants, self.config).build()
        storage.build_storage(self.model, self.constants, self.config).build()
        smbios.build_smbios(self.model, self.constants, self.config).build()
        security.build_security(self.model, self.constants, self.config).build()
        misc.build_misc(self.model, self.constants, self.config).build()

        # Work-around ocvalidate
        if self.constants.validate is False:
            print("- Adding bootmgfw.efi BlessOverride")
            self.config["Misc"]["BlessOverride"] += ["\\EFI\\Microsoft\\Boot\\bootmgfw.efi"]


    def generate_base(self):
        # Generate OpenCore base folder and config
        if not Path(self.constants.build_path).exists():
            print("Creating build folder")
            Path(self.constants.build_path).mkdir()
        else:
            print("Build folder already present, skipping")

        if Path(self.constants.opencore_zip_copied).exists():
            print("Deleting old copy of OpenCore zip")
            Path(self.constants.opencore_zip_copied).unlink()
        if Path(self.constants.opencore_release_folder).exists():
            print("Deleting old copy of OpenCore folder")
            shutil.rmtree(self.constants.opencore_release_folder, onerror=rmtree_handler, ignore_errors=True)

        print(f"\n- Adding OpenCore v{self.constants.opencore_version} {self.constants.opencore_build}")
        shutil.copy(self.constants.opencore_zip_source, self.constants.build_path)
        zipfile.ZipFile(self.constants.opencore_zip_copied).extractall(self.constants.build_path)

        # Setup config.plist for editing
        print("- Adding config.plist for OpenCore")
        shutil.copy(self.constants.plist_template, self.constants.oc_folder)
        self.config = plistlib.load(Path(self.constants.plist_path).open("rb"))


    def set_revision(self):
        # Set revision in config
        self.config["#Revision"]["Build-Version"] = f"{self.constants.patcher_version} - {date.today()}"
        if not self.constants.custom_model:
            self.config["#Revision"]["Build-Type"] = "OpenCore Built on Target Machine"
            computer_copy = copy.copy(self.constants.computer)
            computer_copy.ioregistry = None
            self.config["#Revision"]["Hardware-Probe"] = pickle.dumps(computer_copy)
        else:
            self.config["#Revision"]["Build-Type"] = "OpenCore Built for External Machine"
        self.config["#Revision"]["OpenCore-Version"] = f"{self.constants.opencore_version} - {self.constants.opencore_build} - {self.constants.opencore_commit}"
        self.config["#Revision"]["Original-Model"] = self.model
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Version"] = f"{self.constants.patcher_version}"
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Model"] = self.model


    def save_config(self):
        plistlib.dump(self.config, Path(self.constants.plist_path).open("wb"), sort_keys=True)


    def build_opencore(self):
        # Generate OpenCore Configuration
        self.build_efi()
        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True or (self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != ""):
            smbios.build_smbios(self.model, self.constants, self.config).set_smbios()
        support.build_support(self.model, self.constants, self.config).cleanup()
        self.save_config()

        # Post-build handling
        support.build_support(self.model, self.constants, self.config).sign_files()
        support.build_support(self.model, self.constants, self.config).validate_pathing()

        print("")
        print(f"Your OpenCore EFI for {self.model} has been built at:")
        print(f"    {self.constants.opencore_release_folder}")
        print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to continue\n")
