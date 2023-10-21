# Utility class for build functions
# Copyright (C) 2020-2023, Dhinak G, Mykola Grymalyuk

import shutil
import typing
import logging
import plistlib
import zipfile
import subprocess

from pathlib import Path

from resources import constants, utilities


class BuildSupport:
    """
    Support Library for build.py and related libraries
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants


    @staticmethod
    def get_item_by_kv(iterable: dict, key: str, value: typing.Any) -> dict:
        """
        Gets an item from a list of dicts by key and value

        Parameters:
            iterable (list): List of dicts
            key       (str): Key to search for
            value     (any): Value to search for

        """

        item = None
        for i in iterable:
            if i[key] == value:
                item = i
                break
        return item


    def get_kext_by_bundle_path(self, bundle_path: str) -> dict:
        """
        Gets a kext by bundle path

        Parameters:
            bundle_path (str): Relative bundle path of the kext in the EFI folder
        """

        kext: dict = self.get_item_by_kv(self.config["Kernel"]["Add"], "BundlePath", bundle_path)
        if not kext:
            logging.info(f"- Could not find kext {bundle_path}!")
            raise IndexError
        return kext


    def get_efi_binary_by_path(self, bundle_name: str, entry_type: str, efi_type: str) -> dict:
        """
        Gets an EFI binary by name

        Parameters:
            bundle_name (str): Name of the EFI binary
            entry_type  (str): Type of EFI binary (UEFI, Misc)
            efi_type    (str): Type of EFI binary (Drivers, Tools)
        """

        efi_binary: dict = self.get_item_by_kv(self.config[entry_type][efi_type], "Path", bundle_name)
        if not efi_binary:
            logging.info(f"- Could not find {efi_type}: {bundle_name}!")
            raise IndexError
        return efi_binary


    def enable_kext(self, kext_name: str, kext_version: str, kext_path: Path, check: bool = False) -> None:
        """
        Enables a kext in the config.plist

        Parameters:
            kext_name     (str): Name of the kext
            kext_version  (str): Version of the kext
            kext_path    (Path): Path to the kext
        """

        kext: dict = self.get_kext_by_bundle_path(kext_name)

        if callable(check) and not check():
            # Check failed
            return

        if kext["Enabled"] is True:
            return

        logging.info(f"- Adding {kext_name} {kext_version}")
        shutil.copy(kext_path, self.constants.kexts_path)
        kext["Enabled"] = True


    def sign_files(self) -> None:
        """
        Signs files for on OpenCorePkg's Vault system
        """

        if self.constants.vault is False:
            return

        logging.info("- Vaulting EFI\n=========================================")
        popen = subprocess.Popen([str(self.constants.vault_path), f"{self.constants.oc_folder}/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            logging.info(stdout_line.strip())
        logging.info("=========================================")

    def validate_pathing(self) -> None:
        """
        Validate whether all files are accounted for on-disk

        This ensures that OpenCore won't hit a critical error and fail to boot
        """

        logging.info("- Validating generated config")
        if not Path(self.constants.opencore_release_folder / Path("EFI/OC/config.plist")):
            logging.info("- OpenCore config file missing!!!")
            raise Exception("OpenCore config file missing")

        config_plist = plistlib.load(Path(self.constants.opencore_release_folder / Path("EFI/OC/config.plist")).open("rb"))

        for acpi in config_plist["ACPI"]["Add"]:
            if not Path(self.constants.opencore_release_folder / Path("EFI/OC/ACPI") / Path(acpi["Path"])).exists():
                logging.info(f"- Missing ACPI Table: {acpi['Path']}")
                raise Exception(f"Missing ACPI Table: {acpi['Path']}")

        for kext in config_plist["Kernel"]["Add"]:
            kext_path = Path(self.constants.opencore_release_folder / Path("EFI/OC/Kexts") / Path(kext["BundlePath"]))
            kext_binary_path = Path(kext_path / Path(kext["ExecutablePath"]))
            kext_plist_path = Path(kext_path / Path(kext["PlistPath"]))
            if not kext_path.exists():
                logging.info(f"- Missing kext: {kext_path}")
                raise Exception(f"Missing {kext_path}")
            if not kext_binary_path.exists():
                logging.info(f"- Missing {kext['BundlePath']}'s binary: {kext_binary_path}")
                raise Exception(f"Missing {kext_binary_path}")
            if not kext_plist_path.exists():
                logging.info(f"- Missing {kext['BundlePath']}'s plist: {kext_plist_path}")
                raise Exception(f"Missing {kext_plist_path}")

        for tool in config_plist["Misc"]["Tools"]:
            if not Path(self.constants.opencore_release_folder / Path("EFI/OC/Tools") / Path(tool["Path"])).exists():
                logging.info(f"- Missing tool: {tool['Path']}")
                raise Exception(f"Missing tool: {tool['Path']}")

        for driver in config_plist["UEFI"]["Drivers"]:
            if not Path(self.constants.opencore_release_folder / Path("EFI/OC/Drivers") / Path(driver["Path"])).exists():
                logging.info(f"- Missing driver: {driver['Path']}")
                raise Exception(f"Missing driver: {driver['Path']}")

        # Validating local files
        # Report if they have no associated config.plist entry (i.e. they're not being used)
        for tool_files in Path(self.constants.opencore_release_folder / Path("EFI/OC/Tools")).glob("*"):
            if tool_files.name not in [x["Path"] for x in config_plist["Misc"]["Tools"]]:
                logging.info(f"- Missing tool from config: {tool_files.name}")
                raise Exception(f"Missing tool from config: {tool_files.name}")

        for driver_file in Path(self.constants.opencore_release_folder / Path("EFI/OC/Drivers")).glob("*"):
            if driver_file.name not in [x["Path"] for x in config_plist["UEFI"]["Drivers"]]:
                logging.info(f"- Found extra driver: {driver_file.name}")
                raise Exception(f"Found extra driver: {driver_file.name}")


    def cleanup(self) -> None:
        """
        Clean up files and entries
        """

        logging.info("- Cleaning up files")
        # Remove unused entries
        entries_to_clean = {
            "ACPI":   ["Add", "Delete", "Patch"],
            "Booter": ["Patch"],
            "Kernel": ["Add", "Block", "Force", "Patch"],
            "Misc":   ["Tools"],
            "UEFI":   ["Drivers"],
        }

        for entry in entries_to_clean:
            for sub_entry in entries_to_clean[entry]:
                for item in list(self.config[entry][sub_entry]):
                    if item["Enabled"] is False:
                        self.config[entry][sub_entry].remove(item)

        for kext in self.constants.kexts_path.rglob("*.zip"):
            with zipfile.ZipFile(kext) as zip_file:
                zip_file.extractall(self.constants.kexts_path)
            kext.unlink()

        for item in self.constants.oc_folder.rglob("*.zip"):
            with zipfile.ZipFile(item) as zip_file:
                zip_file.extractall(self.constants.oc_folder)
            item.unlink()

        if not self.constants.recovery_status:
            # Crashes in RecoveryOS for unknown reason
            for i in self.constants.build_path.rglob("__MACOSX"):
                shutil.rmtree(i)

        # Remove unused plugins inside of kexts
        # Following plugins are sometimes unused as there's different variants machines need
        known_unused_plugins = [
            "AirPortBrcm4331.kext",
            "AirPortAtheros40.kext",
            "AppleAirPortBrcm43224.kext",
            "AirPortBrcm4360_Injector.kext",
            "AirPortBrcmNIC_Injector.kext"
        ]
        for kext in Path(self.constants.opencore_release_folder / Path("EFI/OC/Kexts")).glob("*.kext"):
            for plugin in Path(kext / "Contents/PlugIns/").glob("*.kext"):
                should_remove = True
                for enabled_kexts in self.config["Kernel"]["Add"]:
                    if enabled_kexts["BundlePath"].endswith(plugin.name):
                        should_remove = False
                        break
                if should_remove:
                    if plugin.name not in known_unused_plugins:
                        raise Exception(f" - Unknown plugin found: {plugin.name}")
                    shutil.rmtree(plugin)

        Path(self.constants.opencore_zip_copied).unlink()