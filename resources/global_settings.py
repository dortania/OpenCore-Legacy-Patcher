# Alternative to Apple's 'defaults' tool
# Store data in '/Users/Shared'
# This is to ensure compatibility when running without a user
# ie. during automated patching

from pathlib import Path
import plistlib
import logging
import os
import subprocess


class GlobalEnviromentSettings:
    """
    Library for querying and writing global enviroment settings
    """

    def __init__(self) -> None:
        self.file_name:              str = ".com.dortania.opencore-legacy-patcher.plist"
        self.global_settings_folder: str = "/Users/Shared"
        self.global_settings_plist:  str = f"{self.global_settings_folder}/{self.file_name}"

        self._generate_settings_file()
        self._convert_defaults_to_global_settings()
        self._fix_file_permission()


    def read_property(self, property_name: str) -> str or None:
        """
        Reads a property from the global settings file
        """

        if Path(self.global_settings_plist).exists():
            plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            if property_name in plist:
                return plist[property_name]
        return None


    def write_property(self, property_name: str, property_value) -> None:
        """
        Writes a property to the global settings file
        """

        if Path(self.global_settings_plist).exists():
            plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            plist[property_name] = property_value
            try:
                plistlib.dump(plist, Path(self.global_settings_plist).open("wb"))
            except PermissionError:
                logging.info("- Failed to write to global settings file")


    def _generate_settings_file(self) -> None:
        if Path(self.global_settings_plist).exists():
            return
        try:
            plistlib.dump({"Developed by Dortania": True,}, Path(self.global_settings_plist).open("wb"))
        except PermissionError:
            logging.info("- Permission error: Unable to write to global settings file")


    def _convert_defaults_to_global_settings(self) -> None:
        """
        Converts legacy defaults to global settings
        """

        defaults_path = "~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist"
        defaults_path = Path(defaults_path).expanduser()

        if Path(defaults_path).exists():
            defaults_plist = plistlib.load(Path(defaults_path).open("rb"))
            # merge defaults with global settings
            global_settings_plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            global_settings_plist.update(defaults_plist)
            try:
                plistlib.dump(global_settings_plist, Path(self.global_settings_plist).open("wb"))
            except PermissionError:
                logging.info("- Permission error: Unable to write to global settings file")
                return

            # delete defaults plist
            try:
                Path(defaults_path).unlink()
            except PermissionError:
                logging.info("- Permission error: Unable to delete defaults plist")


    def _fix_file_permission(self) -> None:
        """
        Fixes file permission for log file

        If OCLP was invoked as root, file permission will only allow root to write to settings file
        This in turn breaks normal OCLP execution to write to settings file
        """

        if os.geteuid() != 0:
            return

        # Set file permission to allow any user to write to log file
        result = subprocess.run(["chmod", "777", self.global_settings_plist], capture_output=True)
        if result.returncode != 0:
            logging.warning("- Failed to fix settings file permissions:")
            if result.stderr:
                logging.warning(result.stderr.decode("utf-8"))