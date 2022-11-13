# Commands for building the EFI and SMBIOS
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
        self.computer = self.constants.computer
        self.gfx0_path = None


    def build_efi(self):
        utilities.cls()
        if not self.constants.custom_model:
            print(f"Building Configuration on model: {self.model}")
        else:
            print(f"Building Configuration for external model: {self.model}")
        if not Path(self.constants.build_path).exists():
            Path(self.constants.build_path).mkdir()
            print("Created build folder")
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

        print("- Adding config.plist for OpenCore")
        # Setup config.plist for editing
        shutil.copy(self.constants.plist_template, self.constants.oc_folder)
        self.config = plistlib.load(Path(self.constants.plist_path).open("rb"))

        # Set revision in config
        self.config["#Revision"]["Build-Version"] = f"{self.constants.patcher_version} - {date.today()}"
        if not self.constants.custom_model:
            self.config["#Revision"]["Build-Type"] = "OpenCore Built on Target Machine"
            computer_copy = copy.copy(self.computer)
            computer_copy.ioregistry = None
            self.config["#Revision"]["Hardware-Probe"] = pickle.dumps(computer_copy)
        else:
            self.config["#Revision"]["Build-Type"] = "OpenCore Built for External Machine"
        self.config["#Revision"]["OpenCore-Version"] = f"{self.constants.opencore_version} - {self.constants.opencore_build} - {self.constants.opencore_commit}"
        self.config["#Revision"]["Original-Model"] = self.model
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Version"] = f"{self.constants.patcher_version}"
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Model"] = self.model

        # Set Lilu and co.
        support.build_support(self.model, self.constants, self.config).enable_kext("Lilu.kext", self.constants.lilu_version, self.constants.lilu_path)
        self.config["Kernel"]["Quirks"]["DisableLinkeditJettison"] = True

        # Call support functions
        firmware.build_firmware(self.model, self.constants, self.config).build()
        wired.build_wired(self.model, self.constants, self.config).build()
        wireless.build_wireless(self.model, self.constants, self.config).build()
        graphics_audio.build_graphics_audio(self.model, self.constants, self.config).build()
        bluetooth.build_bluetooth(self.model, self.constants, self.config).build()
        storage.build_storage(self.model, self.constants, self.config).build()
        misc.build_misc(self.model, self.constants, self.config).build()
        smbios.build_smbios(self.model, self.constants, self.config).build()
        security.build_security(self.model, self.constants, self.config).build()

        if self.constants.validate is False:
            print("- Adding bootmgfw.efi BlessOverride")
            self.config["Misc"]["BlessOverride"] += ["\\EFI\\Microsoft\\Boot\\bootmgfw.efi"]

        if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
            # Ensure this is done at the end so all previous RestrictEvents patches are applied
            # RestrictEvents and EFICheckDisabler will conflict if both are injected
            support.build_support(self.model, self.constants, self.config).enable_kext("EFICheckDisabler.kext", "", self.constants.efi_disabler_path)


    def build_opencore(self):
        self.build_efi()
        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True or (self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != ""):
            smbios.build_smbios(self.model, self.constants, self.config).set_smbios()
        support.build_support(self.model, self.constants, self.config).cleanup()
        support.build_support(self.model, self.constants, self.config).sign_files()
        support.build_support(self.model, self.constants, self.config).validate_pathing()
        print("")
        print(f"Your OpenCore EFI for {self.model} has been built at:")
        print(f"    {self.constants.opencore_release_folder}")
        print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to continue\n")
