# Commands for building the EFI and SMBIOS

from __future__ import print_function

import binascii
import plistlib
import re
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path

from Resources import ModelArray, Versions, utilities


class BuildOpenCore():
    def __init__(self, model, versions):
        self.model = model
        self.config = None
        self.versions: Versions.Versions = versions

    def build_efi(self):
        utilities.cls()
        if not Path(self.versions.build_path).exists():
            Path(self.versions.build_path).mkdir()
            print("Created build folder")
        else:
            print("Build folder already present, skipping")

        if Path(self.versions.opencore_path_build).exists():
            print("Deleting old copy of OpenCore zip")
            Path(self.versions.opencore_path_build).unlink()
        if Path(self.versions.opencore_path_done).exists():
            print("Deleting old copy of OpenCore folder")
            shutil.rmtree(self.versions.opencore_path_done)

        print()
        print("- Adding OpenCore v" + self.versions.opencore_version)
        shutil.copy(self.versions.opencore_path, self.versions.build_path)
        zipfile.ZipFile(self.versions.opencore_path_build).extractall(self.versions.build_path)

        print("- Adding config.plist for OpenCore")
        # Setup config.plist for editing
        shutil.copy(self.versions.plist_path, self.versions.plist_path_build)
        self.config = plistlib.load(Path(self.versions.plist_path_build_full).open("rb"))

        for name, version, path, check in [
            # Essential kexts
            ("Lilu.kext", self.versions.lilu_version, self.versions.lilu_path, lambda: True),
            ("WhateverGreen.kext", self.versions.whatevergreen_version, self.versions.whatevergreen_path, lambda: True),
            ("RestrictEvents.kext", self.versions.restrictevents_version, self.versions.restrictevents_path, lambda: self.model in ModelArray.MacPro71),
            # CPU patches
            ("AppleMCEReporterDisabler.kext", self.versions.mce_version, self.versions.mce_path, lambda: self.model in ModelArray.DualSocket),
            ("AAAMouSSE.kext", self.versions.mousse_version, self.versions.mousse_path, lambda: self.model in ModelArray.SSEEmulator),
            ("telemetrap.kext", self.versions.telemetrap_version, self.versions.telemetrap_path, lambda: self.model in ModelArray.MissingSSE42),
            # Ethernet patches
            ("nForceEthernet.kext", self.versions.nforce_version, self.versions.nforce_path, lambda: self.model in ModelArray.EthernetNvidia),
            ("MarvelYukonEthernet.kext", self.versions.marvel_version, self.versions.marvel_path, lambda: self.model in ModelArray.EthernetMarvell),
            ("CatalinaBCM5701Ethernet.kext", self.versions.bcm570_version, self.versions.bcm570_path, lambda: self.model in ModelArray.EthernetBroadcom),
            # Legacy audio
            ("VoodooHDA.kext", self.versions.voodoohda_version, self.versions.voodoohda_path, lambda: self.model in ModelArray.LegacyAudio)
        ]:
            self.enable_kext(name, version, path, check)

        # WiFi patches

        if self.model in ModelArray.WifiAtheros:
            self.enable_kext("IO80211HighSierra.kext", self.versions.io80211high_sierra_version, self.versions.io80211high_sierra_path)
            self.get_kext_by_bundle_path("IO80211HighSierra.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True

        if self.model in ModelArray.WifiBCM94331:
            self.enable_kext("AirportBrcmFixup.kext", self.versions.airportbcrmfixup_version, self.versions.airportbcrmfixup_path)
            self.get_kext_by_bundle_path("AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext")["Enabled"] = True

            if self.model in ModelArray.EthernetNvidia:
                # Nvidia chipsets all have the same path to ARPT
                property_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            if self.model in ("MacBookAir2,1", "MacBookAir3,1", "MacBookAir3,2"):
                property_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            elif self.model in ("iMac7,1", "iMac8,1"):
                property_path = "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x0)"
            elif self.model in ("iMac13,1", "iMac13,2"):
                property_path = "PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)"
            elif self.model == "MacPro5,1":
                property_path = "PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)"
            else:
                # Assumes we have a laptop with Intel chipset
                property_path = "PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"
            print("- Applying fake ID for WiFi")
            self.config["DeviceProperties"]["Add"][property_path] = {
                "device-id": binascii.unhexlify("ba430000"),
                "compatible": "pci14e4,43ba"
            }

        # HID patches
        if self.model in ModelArray.LegacyHID:
            print("- Adding IOHIDFamily patch")
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.iokit.IOHIDFamily")["Enabled"] = True

        # SSDT patches
        if self.model in ModelArray.pciSSDT:
            print("- Adding SSDT-CPBG.aml")
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-CPBG.aml")["Enabled"] = True

        # USB map
        map_name = f"USB-Map-{self.model}.zip"
        map_entry = f"USB-Map-{self.model}.kext"
        usb_map_path = Path(self.versions.current_path) / Path(f"payloads/Kexts/Maps/Zip/{map_name}")
        if usb_map_path.exists():
            print(f"- Adding {map_entry}")
            shutil.copy(usb_map_path, self.versions.kext_path_build)
            self.get_kext_by_bundle_path("USB-Map-SMBIOS.kext")["Enabled"] = True
            self.get_kext_by_bundle_path("USB-Map-SMBIOS.kext")["BundlePath"] = map_entry

        if self.model in ModelArray.DualGPUPatch:
            print("- Adding dual GPU patch")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " agdpmod=pikera"

        if self.model in ModelArray.HiDPIpicker:
            print("- Setting HiDPI picker")
            self.config["NVRAM"]["Add"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"]["UIScale"] = binascii.unhexlify("02")

        # Add OpenCanopy
        print("- Adding OpenCanopy GUI")
        shutil.rmtree(self.versions.gui_path_build)
        shutil.copy(self.versions.gui_path, self.versions.plist_path_build)
        self.config["UEFI"]["Drivers"] = ["OpenCanopy.efi", "OpenRuntime.efi"]

        plistlib.dump(self.config, Path(self.versions.plist_path_build_full).open("wb"), sort_keys=True)

    def set_smbios(self):
        spoofed_model = self.model
        if self.model in ModelArray.MacBookAir61:
            print("- Spoofing to MacBookAir6,1")
            spoofed_model = "MacBookAir6,1"
        elif self.model in ModelArray.MacBookAir62:
            print("- Spoofing to MacBookAir6,2")
            spoofed_model = "MacBookAir6,2"
        elif self.model in ModelArray.MacBookPro111:
            print("- Spoofing to MacBookPro11,1")
            spoofed_model = "MacBookPro11,1"
        elif self.model in ModelArray.MacBookPro112:
            print("- Spoofing to MacBookPro11,2")
            spoofed_model = "MacBookPro11,2"
        elif self.model in ModelArray.Macmini71:
            print("- Spoofing to Macmini7,1")
            spoofed_model = "Macmini7,1"
        elif self.model in ModelArray.iMac151:
            print("- Spoofing to iMac15,1")
            spoofed_model = "iMac15,1"
        elif self.model in ModelArray.iMac144:
            print("- Spoofing to iMac14,4")
            spoofed_model = "iMac14,4"
        elif self.model in ModelArray.MacPro71:
            print("- Spoofing to MacPro7,1")
            spoofed_model = "MacPro7,1"
        macserial_output = subprocess.run((f"./payloads/tools/macserial -g -m {spoofed_model} -n 1").split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        macserial_output = macserial_output.stdout.decode().strip().split(" | ")
        self.config["PlatformInfo"]["Generic"]["SystemProductName"] = spoofed_model
        self.config["PlatformInfo"]["Generic"]["SystemSerialNumber"] = macserial_output[0]
        self.config["PlatformInfo"]["Generic"]["MLB"] = macserial_output[1]
        self.config["PlatformInfo"]["Generic"]["SystemUUID"] = str(uuid.uuid4()).upper()

    @staticmethod
    def get_item_by_kv(iterable, key, value):
        item = None
        for i in iterable:
            if i[key] == value:
                item = i
                break
        return item

    def get_kext_by_bundle_path(self, bundle_path):
        kext = self.get_item_by_kv(self.config["Kernel"]["Add"], "BundlePath", bundle_path)
        if not kext:
            print(f"- Could not find kext {bundle_path}!")
            raise IndexError
        return kext

    def enable_kext(self, kext_name, kext_version, kext_path, check=False):
        kext = self.get_kext_by_bundle_path(kext_name)

        if callable(check) and not check():
            # Check failed
            return

        print(f"- Adding {kext_name} {kext_version}")
        shutil.copy(kext_path, self.versions.kext_path_build)
        kext["Enabled"] = True

    def cleanup(self):
        print("- Cleaning up files")
        for kext in Path(self.versions.kext_path_build).glob("*.zip"):
            with zipfile.ZipFile(kext) as zip_file:
                zip_file.extractall(self.versions.kext_path_build)
            kext.unlink()
        shutil.rmtree((Path(self.versions.kext_path_build) / Path("__MACOSX")), ignore_errors=True)

        for item in Path(self.versions.plist_path_build).glob("*.zip"):
            with zipfile.ZipFile(item) as zip_file:
                zip_file.extractall(self.versions.plist_path_build)
            item.unlink()
        shutil.rmtree((Path(self.versions.build_path) / Path("__MACOSX")), ignore_errors=True)
        Path(self.versions.opencore_path_build).unlink()

    def build_opencore(self):
        self.build_efi()
        self.set_smbios()
        self.cleanup()
        print("")
        print("Your OpenCore EFI has been built at:")
        print(f"    {self.versions.opencore_path_done}")
        print("")
        input("Press enter to go back")

    def copy_efi(self):
        diskutil = [subprocess.run("diskutil list".split(), stdout=subprocess.PIPE).stdout.decode().strip()]
        menu = utilities.TUIMenu(["Select Disk"], "Please select the disk you want to install OpenCore to: ", in_between=diskutil, return_number_instead_of_direct_call=True, add_quit=False)
        for disk in [i for i in Path("/dev").iterdir() if re.fullmatch("disk[0-9]+", i.stem)]:
            menu.add_menu_option(disk.stem, key=disk.stem[4:])
        disk_num = menu.start()
        print(subprocess.run(("sudo diskutil mount disk" + disk_num).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout)

        utilities.cls()
        utilities.header(["Copying OpenCore"])
        efi_dir = Path("/Volumes/EFI")
        if efi_dir.exists():
            print("- Coping OpenCore onto EFI partition")
            if (efi_dir / Path("EFI")).exists():
                print("Removing preexisting EFI folder")
                shutil.rmtree(efi_dir / Path("EFI"))
            if Path(self.versions.opencore_path_done).exists():
                shutil.copytree(self.versions.opencore_path_done, efi_dir)
                shutil.copy(self.versions.icon_path, efi_dir)
                print("OpenCore transfer complete")
                print("")
        else:
            print("Couldn't find EFI partition")
            print("Please ensure your drive is formatted as GUID Partition Table")
            print("")


class OpenCoreMenus():
    def __init__(self, versions):
        self.versions: Versions.Versions = versions

    def change_opencore_version(self):
        utilities.cls()
        utilities.header(["Change OpenCore Version"])
        print(f"\nCurrent OpenCore version: {self.versions.opencore_version}\nSupported versions: 0.6.6 (recommended)")
        version = input("Please enter the desired OpenCore version (or press Enter to cancel): ").strip()
        if not version:
            return
        while version not in self.versions.available_opencore_versions:
            utilities.cls()
            utilities.header(["Change OpenCore Version"])
            print(f"\nCurrent OpenCore version: {self.versions.opencore_version}\nSupported versions: 0.6.6 (recommended)")
            version = input(f"Invalid OpenCore version {version}!\nPlease enter the desired OpenCore version (or press Enter to cancel): ").strip()
            if not version:
                return
        self.versions.opencore_version = version

    def build_opencore_menu(self, model):
        response = None
        while not (response and response == -1):
            title = [
                f"Build OpenCore v{self.versions.opencore_version} EFI",
                "Selected Model: " + model
            ]
            menu = utilities.TUIMenu(title, "Please select an option: ", auto_number=True)

            options = [
                ["Build OpenCore", lambda: BuildOpenCore(model, self.versions).build_opencore()],
                ["Change OpenCore Version", self.change_opencore_version],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()
            # response = utilities.menu(title, "zoomer, Please select an option: ", options, auto_number=True, top_level=True)
