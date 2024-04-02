"""
commit_info.py: Parse Commit Info from binary's info.plist
"""

import plistlib

from pathlib import Path


class ParseCommitInfo:

    def __init__(self, binary_path: str) -> None:
        """
        Parameters:
            binary_path (str): Path to binary
        """

        self.binary_path = str(binary_path)
        self.plist_path = self._convert_binary_path_to_plist_path()


    def _convert_binary_path_to_plist_path(self) -> str:
        """
        Resolve Info.plist path from binary path
        """

        if Path(self.binary_path).exists():
            plist_path = self.binary_path.replace("MacOS/OpenCore-Patcher", "Info.plist")
            if Path(plist_path).exists() and plist_path.endswith(".plist"):
                return plist_path
        return None


    def generate_commit_info(self) -> tuple:
        """
        Generate commit info from Info.plist

        Returns:
            tuple: (Branch, Commit Date, Commit URL)
        """

        if self.plist_path:
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