# Parse Commit Info from binary's info.plist
# App Structure:
#   OpenCore-Patcher.app:
#      Contents:
#          MacOS:
#              OpenCore-Patcher
#          Info.plist

from pathlib import Path
import plistlib

class commit_info:

    def __init__(self, binary_path):
        self.binary_path = str(binary_path)
        self.plist_path = self.convert_binary_path_to_plist_path()


    def convert_binary_path_to_plist_path(self):
        if Path(self.binary_path).exists():
            plist_path = self.binary_path.replace("MacOS/OpenCore-Patcher", "Info.plist")
            if Path(plist_path).exists() and plist_path.endswith(".plist"):
                return plist_path
        return None

    def generate_commit_info(self):
        if self.plist_path:
            # print(self.plist_path)
            plist_info = plistlib.load(Path(self.plist_path).open("rb"))
            if "Github" in plist_info:
                return (
                    plist_info["Github"]["Branch"],
                    plist_info["Github"]["Commit Date"],
                    plist_info["Github"]["Commit URL"],
                )
        return (
            "Running from source",
            "Not applicable",
            "",
        )