# Alternative to Apple's 'defaults' tool
# Store data in '/Users/Shared'
# This is to ensure compatibility when running without a user
# ie. during automated patching

from pathlib import Path
import plistlib

class global_settings:

    def __init__(self):
        self.file_name = ".com.dortania.opencore-legacy-patcher.plist"
        self.global_settings_folder = "/Users/Shared"
        self.global_settings_plist = f"{self.global_settings_folder}/{self.file_name}"
        self.generate_settings_file()
        self.convert_defaults_to_global_settings()

    def generate_settings_file(self):
        if Path(self.global_settings_plist).exists():
            return
        try:
            plistlib.dump({"Developed by Dortania": True,}, Path(self.global_settings_plist).open("wb"))
        except PermissionError:
            print("- Permission error: Unable to write to global settings file")

    def read_property(self, property_name):
        if Path(self.global_settings_plist).exists():
            plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            if property_name in plist:
                return plist[property_name]
        return None

    def write_property(self, property_name, property_value):
        if Path(self.global_settings_plist).exists():
            plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            plist[property_name] = property_value
            try:
                plistlib.dump(plist, Path(self.global_settings_plist).open("wb"))
            except PermissionError:
                print("- Failed to write to global settings file")


    def convert_defaults_to_global_settings(self):
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
                print("- Permission error: Unable to write to global settings file")
                return

            # delete defaults plist
            try:
                Path(defaults_path).unlink()
            except PermissionError:
                print("- Permission error: Unable to delete defaults plist")