"""
macos_installer_handler.py: Handler for local macOS installers
"""

import logging
import plistlib
import tempfile
import subprocess
import re

from pathlib import Path

from ..datasets import os_data

from . import (
    utilities,
    subprocess_wrapper
)

from ..volume import (
    can_copy_on_write,
    generate_copy_arguments
)


APPLICATION_SEARCH_PATH:  str = "/Applications"

tmp_dir = tempfile.TemporaryDirectory()


class InstallerCreation():

    def __init__(self) -> None:
        pass


    def install_macOS_installer(self, download_path: str) -> bool:
        """
        Installs InstallAssistant.pkg

        Parameters:
            download_path (str): Path to InstallAssistant.pkg

        Returns:
            bool: True if successful, False otherwise
        """

        logging.info("Extracting macOS installer from InstallAssistant.pkg")
        result = subprocess_wrapper.run_as_root(["/usr/sbin/installer", "-pkg", f"{Path(download_path)}/InstallAssistant.pkg", "-target", "/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logging.info("Failed to install InstallAssistant")
            subprocess_wrapper.log(result)
            return False

        logging.info("InstallAssistant installed")
        return True


    def generate_installer_creation_script(self, tmp_location: str, installer_path: str, disk: str) -> bool:
        """
        Creates installer.sh to be piped to OCLP-Helper and run as admin

        Script includes:
        - Format provided disk as HFS+ GPT
        - Run createinstallmedia on provided disk

        Implementing this into a single installer.sh script allows us to only call
        OCLP-Helper once to avoid nagging the user about permissions

        Parameters:
            tmp_location (str): Path to temporary directory
            installer_path (str): Path to InstallAssistant.pkg
            disk (str): Disk to install to

        Returns:
            bool: True if successful, False otherwise
        """

        additional_args = ""
        script_location = Path(tmp_location) / Path("Installer.sh")

        # Due to a bug in createinstallmedia, running from '/Applications' may sometimes error:
        #   'Failed to extract AssetData/boot/Firmware/Manifests/InstallerBoot/*'
        # This affects native Macs as well even when manually invoking createinstallmedia

        # To resolve, we'll copy into our temp directory and run from there

        # Create a new tmp directory
        # Our current one is a disk image, thus CoW will not work
        global tmp_dir
        ia_tmp = tmp_dir.name

        logging.info(f"Creating temporary directory at {ia_tmp}")
        # Delete all files in tmp_dir
        for file in Path(ia_tmp).glob("*"):
            subprocess.run(["/bin/rm", "-rf", str(file)])

        # Copy installer to tmp
        if can_copy_on_write(installer_path, ia_tmp) is False:
            # Ensure we have enough space for the duplication when CoW is not supported
            space_available = utilities.get_free_space()
            space_needed = Path(ia_tmp).stat().st_size
            if space_available < space_needed:
                logging.info("Not enough free space to create installer.sh")
                logging.info(f"{utilities.human_fmt(space_available)} available, {utilities.human_fmt(space_needed)} required")
                return False

        subprocess.run(generate_copy_arguments(installer_path, ia_tmp))

        # Adjust installer_path to point to the copied installer
        installer_path = Path(ia_tmp) / Path(Path(installer_path).name)
        if not Path(installer_path).exists():
            logging.info(f"Failed to copy installer to {ia_tmp}")
            return False

        # Verify code signature before executing
        createinstallmedia_path = str(Path(installer_path) / Path("Contents/Resources/createinstallmedia"))
        if subprocess.run(["/usr/bin/codesign", "-v", "-R=anchor apple", createinstallmedia_path]).returncode != 0:
            logging.info(f"Installer has broken code signature")
            return False

        plist_path = str(Path(installer_path) / Path("Contents/Info.plist"))
        if Path(plist_path).exists():
            plist = plistlib.load(Path(plist_path).open("rb"))
            if "DTPlatformVersion" in plist:
                platform_version = plist["DTPlatformVersion"]
                platform_version = platform_version.split(".")[0]
                if platform_version[0] == "10":
                    if int(platform_version[1]) < 13:
                        additional_args = f" --applicationpath '{installer_path}'"

        if script_location.exists():
            script_location.unlink()
        script_location.touch()

        with script_location.open("w") as script:
            script.write(f'''#!/bin/bash
erase_disk='/usr/sbin/diskutil eraseDisk HFS+ OCLP-Installer {disk}'
if $erase_disk; then
    "{createinstallmedia_path}" --volume /Volumes/OCLP-Installer --nointeraction{additional_args}
fi
            ''')
        if Path(script_location).exists():
            return True
        return False


    def list_disk_to_format(self) -> dict:
        """
        List applicable disks for macOS installer creation
        Only lists disks that are:
        - 14GB or larger
        - External

        Current limitations:
        - Does not support PCIe based SD cards readers

        Returns:
            dict: Dictionary of disks
        """

        all_disks:  dict = {}
        list_disks: dict = {}

        # TODO: AllDisksAndPartitions is not supported in Snow Leopard and older
        try:
            # High Sierra and newer
            disks = plistlib.loads(subprocess.run(["/usr/sbin/diskutil", "list", "-plist", "physical"], stdout=subprocess.PIPE).stdout.decode().strip().encode())
        except ValueError:
            # Sierra and older
            disks = plistlib.loads(subprocess.run(["/usr/sbin/diskutil", "list", "-plist"], stdout=subprocess.PIPE).stdout.decode().strip().encode())

        for disk in disks["AllDisksAndPartitions"]:
            try:
                disk_info = plistlib.loads(subprocess.run(["/usr/sbin/diskutil", "info", "-plist", disk["DeviceIdentifier"]], stdout=subprocess.PIPE).stdout.decode().strip().encode())
            except:
                # Chinesium USB can have garbage data in MediaName
                diskutil_output = subprocess.run(["/usr/sbin/diskutil", "info", "-plist", disk["DeviceIdentifier"]], stdout=subprocess.PIPE).stdout.decode().strip()
                ungarbafied_output = re.sub(r'(<key>MediaName</key>\s*<string>).*?(</string>)', r'\1\2', diskutil_output).encode()
                disk_info = plistlib.loads(ungarbafied_output)
            try:
                all_disks[disk["DeviceIdentifier"]] = {"identifier": disk_info["DeviceNode"], "name": disk_info.get("MediaName", "Disk"), "size": disk_info["TotalSize"], "removable": disk_info["Internal"], "partitions": {}}
            except KeyError:
                # Avoid crashing with CDs installed
                continue

        for disk in all_disks:
            # Strip disks that are under 14GB (15,032,385,536 bytes)
            # createinstallmedia isn't great at detecting if a disk has enough space
            if not any(all_disks[disk]['size'] > 15032385536 for partition in all_disks[disk]):
                continue
            # Strip internal disks as well (avoid user formatting their SSD/HDD)
            # Ensure user doesn't format their boot drive
            if not any(all_disks[disk]['removable'] is False for partition in all_disks[disk]):
                continue

            list_disks.update({
                disk: {
                    "identifier": all_disks[disk]["identifier"],
                    "name": all_disks[disk]["name"],
                    "size": all_disks[disk]["size"],
                }
            })

        return list_disks


class LocalInstallerCatalog:
    """
    Finds all macOS installers on the local machine.
    """

    def __init__(self) -> None:
        self.available_apps: dict = self._list_local_macOS_installers()


    def _list_local_macOS_installers(self) -> dict:
        """
        Searches for macOS installers in /Applications

        Returns:
            dict: A dictionary of macOS installers found on the local machine.

            Example:
                "Install macOS Big Sur Beta.app": {
                    "Short Name": "Big Sur Beta",
                    "Version": "11.0",
                    "Build": "20A5343i",
                    "Path": "/Applications/Install macOS Big Sur Beta.app",
                },
                etc...
        """

        application_list: dict = {}

        for application in Path(APPLICATION_SEARCH_PATH).iterdir():
            # Certain Microsoft Applications have strange permissions disabling us from reading them
            try:
                if not (Path(APPLICATION_SEARCH_PATH) / Path(application) / Path("Contents/Resources/createinstallmedia")).exists():
                    continue

                if not (Path(APPLICATION_SEARCH_PATH) / Path(application) / Path("Contents/Info.plist")).exists():
                    continue
            except PermissionError:
                continue

            try:
                application_info_plist = plistlib.load((Path(APPLICATION_SEARCH_PATH) / Path(application) / Path("Contents/Info.plist")).open("rb"))
            except (PermissionError, TypeError, plistlib.InvalidFileException):
                continue

            if "DTPlatformVersion" not in application_info_plist:
                continue
            if "CFBundleDisplayName" not in application_info_plist:
                continue

            app_version:  str = application_info_plist["DTPlatformVersion"]
            clean_name:   str = application_info_plist["CFBundleDisplayName"]
            app_sdk:      str = application_info_plist["DTSDKBuild"] if "DTSDKBuild" in application_info_plist else "Unknown"
            min_required: str = application_info_plist["LSMinimumSystemVersion"] if "LSMinimumSystemVersion" in application_info_plist else "Unknown"

            kernel:       int = 0
            try:
                kernel = int(app_sdk[:2])
            except ValueError:
                pass

            min_required = os_data.os_conversion.os_to_kernel(min_required) if min_required != "Unknown" else 0

            if min_required == os_data.os_data.sierra and kernel == os_data.os_data.ventura:
                # Ventura's installer requires El Capitan minimum
                # Ref: https://github.com/dortania/OpenCore-Legacy-Patcher/discussions/1038
                min_required = os_data.os_data.el_capitan

            # app_version can sometimes report GM instead of the actual version
            # This is a workaround to get the actual version
            if app_version.startswith("GM"):
                if kernel == 0:
                    app_version = "Unknown"
                else:
                    app_version = os_data.os_conversion.kernel_to_os(kernel)

            # Check if App Version is High Sierra or newer
            if kernel < os_data.os_data.high_sierra:
                continue

            results = self._parse_sharedsupport_version(Path(APPLICATION_SEARCH_PATH) / Path(application)/ Path("Contents/SharedSupport/SharedSupport.dmg"))
            if results[0] is not None:
                app_sdk = results[0]
            if results[1] is not None:
                app_version = results[1]

            application_list.update({
                application: {
                    "Short Name": clean_name,
                    "Version": app_version,
                    "Build": app_sdk,
                    "Path": application,
                    "Minimum Host OS": min_required,
                    "OS": kernel
                }
            })

        # Sort Applications by version
        application_list = {k: v for k, v in sorted(application_list.items(), key=lambda item: item[1]["Version"])}
        return application_list


    def _parse_sharedsupport_version(self, sharedsupport_path: Path) -> tuple:
        """
        Determine true version of macOS installer by parsing SharedSupport.dmg
        This is required due to Info.plist reporting the application version, not the OS version

        Parameters:
            sharedsupport_path (Path): Path to SharedSupport.dmg

        Returns:
            tuple: Tuple containing the build and OS version
        """

        detected_build: str = None
        detected_os:    str = None

        if not sharedsupport_path.exists():
            return (detected_build, detected_os)

        if not sharedsupport_path.name.endswith(".dmg"):
            return (detected_build, detected_os)


        # Create temporary directory to extract SharedSupport.dmg to
        with tempfile.TemporaryDirectory() as tmpdir:

            output = subprocess.run(
                [
                    "/usr/bin/hdiutil", "attach", "-noverify", sharedsupport_path,
                    "-mountpoint", tmpdir,
                    "-nobrowse",
                ],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            if output.returncode != 0:
                return (detected_build, detected_os)


            ss_info_files = [
                Path("SFR/com_apple_MobileAsset_SFRSoftwareUpdate/com_apple_MobileAsset_SFRSoftwareUpdate.xml"),
                Path("com_apple_MobileAsset_MacSoftwareUpdate/com_apple_MobileAsset_MacSoftwareUpdate.xml")
            ]

            for ss_info in ss_info_files:
                if not Path(tmpdir / ss_info).exists():
                    continue
                plist = plistlib.load((tmpdir / ss_info).open("rb"))
                if "Assets" in plist:
                    if "Build" in plist["Assets"][0]:
                        detected_build = plist["Assets"][0]["Build"]
                    if "OSVersion" in plist["Assets"][0]:
                        detected_os = plist["Assets"][0]["OSVersion"]

            # Unmount SharedSupport.dmg
            subprocess.run(["/usr/bin/hdiutil", "detach", tmpdir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return (detected_build, detected_os)