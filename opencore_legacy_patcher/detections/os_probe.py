"""
os_probe.py: OS Host information
"""

import platform
import plistlib
import subprocess


class OSProbe:
    """
    Library for querying OS information specific to macOS
    """

    def __init__(self) -> None:
        self.uname_data = platform.uname()


    def detect_kernel_major(self) -> int:
        """
        Detect the booted major kernel version

        Returns:
            int: Major kernel version (ex. 21, from 21.1.0)
        """

        return int(self.uname_data.release.partition(".")[0])


    def detect_kernel_minor(self) -> int:
        """
        Detect the booted minor kernel version

        Returns:
            int: Minor kernel version (ex. 1, from 21.1.0)
        """

        return int(self.uname_data.release.partition(".")[2].partition(".")[0])


    def detect_os_version(self) -> str:
        """
        Detect the booted OS version

        Returns:
            str: OS version (ex. 12.0)
        """

        result = subprocess.run(["/usr/bin/sw_vers", "-productVersion"], stdout=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError("Failed to detect OS version")

        return result.stdout.decode().strip()


    def detect_os_build(self, rsr: bool = False) -> str:
        """
        Detect the booted OS build

        Implementation note:
            With macOS 13.2, Apple implemented the Rapid Security Response system which
            will change the reported build to the RSR version and not the original host

            To get the proper versions:
            - Host: /System/Library/CoreServices/SystemVersion.plist
            - RSR:  /System/Volumes/Preboot/Cryptexes/OS/System/Library/CoreServices/SystemVersion.plist


        Parameters:
            rsr (bool): Whether to use the RSR version of the build

        Returns:
            str: OS build (ex. 21A5522h)
        """

        file_path = "/System/Library/CoreServices/SystemVersion.plist"
        if rsr is True:
            file_path = f"/System/Volumes/Preboot/Cryptexes/OS{file_path}"

        try:
            return plistlib.load(open(file_path, "rb"))["ProductBuildVersion"]
        except Exception as e:
            raise RuntimeError(f"Failed to detect OS build: {e}")
