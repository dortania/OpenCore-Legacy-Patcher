# Handler for macOS installers, both local and remote

from pathlib import Path
import plistlib
import subprocess
import tempfile
import enum
import logging

from data import os_data
from resources import network_handler, utilities


APPLICATION_SEARCH_PATH:  str = "/Applications"
SFR_SOFTWARE_UPDATE_PATH: str = "SFR/com_apple_MobileAsset_SFRSoftwareUpdate/com_apple_MobileAsset_SFRSoftwareUpdate.xml"

CATALOG_URL_BASE:      str = "https://swscan.apple.com/content/catalogs/others/index"
CATALOG_URL_EXTENSION: str = "13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
CATALOG_URL_VERSION:   str = "13"

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

        logging.info("- Extracting macOS installer from InstallAssistant.pkg\n  This may take some time")
        args = [
            "osascript",
            "-e",
            f'''do shell script "installer -pkg {Path(download_path)}/InstallAssistant.pkg -target /"'''
            ' with prompt "OpenCore Legacy Patcher needs administrator privileges to add InstallAssistant."'
            " with administrator privileges"
            " without altering line endings",
        ]

        result = subprocess.run(args,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logging.info("- Failed to install InstallAssistant")
            logging.info(f"  Error Code: {result.returncode}")
            return False

        logging.info("- InstallAssistant installed")
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
            subprocess.run(["rm", "-rf", str(file)])

        # Copy installer to tmp (use CoW to avoid extra disk writes)
        args = ["cp", "-cR", installer_path, ia_tmp]
        if utilities.check_filesystem_type() != "apfs":
            # HFS+ disks do not support CoW
            args[1] = "-R"

            # Ensure we have enough space for the duplication
            space_available = utilities.get_free_space()
            space_needed = Path(ia_tmp).stat().st_size
            if space_available < space_needed:
                logging.info("Not enough free space to create installer.sh")
                logging.info(f"{utilities.human_fmt(space_available)} available, {utilities.human_fmt(space_needed)} required")
                return False

        subprocess.run(args)

        # Adjust installer_path to point to the copied installer
        installer_path = Path(ia_tmp) / Path(Path(installer_path).name)
        if not Path(installer_path).exists():
            logging.info(f"Failed to copy installer to {ia_tmp}")
            return False

        createinstallmedia_path = str(Path(installer_path) / Path("Contents/Resources/createinstallmedia"))
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
erase_disk='diskutil eraseDisk HFS+ OCLP-Installer {disk}'
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
            disks = plistlib.loads(subprocess.run("diskutil list -plist physical".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        except ValueError:
            # Sierra and older
            disks = plistlib.loads(subprocess.run("diskutil list -plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())

        for disk in disks["AllDisksAndPartitions"]:
            disk_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            try:
                all_disks[disk["DeviceIdentifier"]] = {"identifier": disk_info["DeviceNode"], "name": disk_info["MediaName"], "size": disk_info["TotalSize"], "removable": disk_info["Internal"], "partitions": {}}
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

            logging.info(f"disk {disk}: {all_disks[disk]['name']} ({utilities.human_fmt(all_disks[disk]['size'])})")
            list_disks.update({
                disk: {
                    "identifier": all_disks[disk]["identifier"],
                    "name": all_disks[disk]["name"],
                    "size": all_disks[disk]["size"],
                }
            })

        return list_disks


class SeedType(enum.IntEnum):
    """
    Enum for catalog types

    Variants:
        DeveloperSeed:  Developer Beta (Part of the Apple Developer Program)
        PublicSeed:     Public Beta
        CustomerSeed:   AppleSeed Program (Generally mirrors DeveloperSeed)
        PublicRelease:  Public Release
    """
    DeveloperSeed: int = 0
    PublicSeed:    int = 1
    CustomerSeed:  int = 2
    PublicRelease: int = 3


class RemoteInstallerCatalog:
    """
    Parses Apple's Software Update catalog and finds all macOS installers.
    """

    def __init__(self, seed_override: SeedType = SeedType.PublicRelease) -> None:

        self.catalog_url: str = self._construct_catalog_url(seed_override)

        self.available_apps:        dict = self._parse_catalog()
        self.available_apps_latest: dict = self._list_newest_installers_only()


    def _construct_catalog_url(self, seed_type: SeedType) -> str:
        """
        Constructs the catalog URL based on the seed type

        Parameters:
            seed_type (SeedType): The seed type to use

        Returns:
            str: The catalog URL
        """


        url: str = ""

        if seed_type == SeedType.DeveloperSeed:
            url = f"{CATALOG_URL_BASE}-{CATALOG_URL_VERSION}seed-{CATALOG_URL_EXTENSION}"
        elif seed_type == SeedType.PublicSeed:
            url = f"{CATALOG_URL_BASE}-{CATALOG_URL_VERSION}beta-{CATALOG_URL_EXTENSION}"
        elif seed_type == SeedType.CustomerSeed:
            url = f"{CATALOG_URL_BASE}-{CATALOG_URL_VERSION}customerseed-{CATALOG_URL_EXTENSION}"
        else:
            url = f"{CATALOG_URL_BASE}-{CATALOG_URL_EXTENSION}"

        return url


    def _fetch_catalog(self) -> dict:
        """
        Fetches the catalog from Apple's servers

        Returns:
            dict: The catalog as a dictionary
        """

        catalog: dict = {}

        if network_handler.NetworkUtilities(self.catalog_url).verify_network_connection() is False:
            return catalog

        try:
            catalog = plistlib.loads(network_handler.NetworkUtilities().get(self.catalog_url).content)
        except plistlib.InvalidFileException:
            return {}

        return catalog

    def _parse_catalog(self) -> dict:
        """
        Parses the catalog and returns a dictionary of available installers

        Returns:
            dict: Dictionary of available installers
        """
        available_apps: dict = {}

        catalog: dict = self._fetch_catalog()
        if not catalog:
            return available_apps

        if "Products" not in catalog:
            return available_apps

        for product in catalog["Products"]:
            if "ExtendedMetaInfo" not in catalog["Products"][product]:
                continue
            if "Packages" not in catalog["Products"][product]:
                continue
            if "InstallAssistantPackageIdentifiers" not in catalog["Products"][product]["ExtendedMetaInfo"]:
                continue
            if "SharedSupport" not in catalog["Products"][product]["ExtendedMetaInfo"]["InstallAssistantPackageIdentifiers"]:
                continue
            if "BuildManifest" not in catalog["Products"][product]["ExtendedMetaInfo"]["InstallAssistantPackageIdentifiers"]:
                continue

            for bm_package in catalog["Products"][product]["Packages"]:
                if "Info.plist" not in bm_package["URL"]:
                    continue
                if "InstallInfo.plist" in bm_package["URL"]:
                    continue

                try:
                    build_plist = plistlib.loads(network_handler.NetworkUtilities().get(bm_package["URL"]).content)
                except plistlib.InvalidFileException:
                    continue

                if "MobileAssetProperties" not in build_plist:
                    continue
                if "SupportedDeviceModels" not in build_plist["MobileAssetProperties"]:
                    continue
                if "OSVersion" not in build_plist["MobileAssetProperties"]:
                    continue
                if "Build" not in build_plist["MobileAssetProperties"]:
                    continue

                # Ensure Apple Silicon specific Installers are not listed
                if "VMM-x86_64" not in build_plist["MobileAssetProperties"]["SupportedDeviceModels"]:
                    continue

                version = build_plist["MobileAssetProperties"]["OSVersion"]
                build   = build_plist["MobileAssetProperties"]["Build"]

                try:
                    catalog_url = build_plist["MobileAssetProperties"]["BridgeVersionInfo"]["CatalogURL"]
                    if "beta" in catalog_url:
                        catalog_url = "PublicSeed"
                    elif "customerseed" in catalog_url:
                        catalog_url = "CustomerSeed"
                    elif "seed" in catalog_url:
                        catalog_url = "DeveloperSeed"
                    else:
                        catalog_url = "Public"
                except KeyError:
                    # Assume Public if no catalog URL is found
                    catalog_url = "Public"

                download_link = None
                integrity     = None
                size          = None

                for ia_package in catalog["Products"][product]["Packages"]:
                    if "InstallAssistant.pkg" not in ia_package["URL"]:
                        continue
                    if "URL" not in ia_package:
                        continue
                    if "IntegrityDataURL" not in ia_package:
                        continue
                    if "Size" not in ia_package:
                        size = 0

                    download_link = ia_package["URL"]
                    integrity     = ia_package["IntegrityDataURL"]
                    size          = ia_package["Size"]


                if any([version, build, download_link, size, integrity]) is None:
                    continue

                available_apps.update({
                    product: {
                        "Version":   version,
                        "Build":     build,
                        "Link":      download_link,
                        "Size":      size,
                        "integrity": integrity,
                        "Source":   "Apple Inc.",
                        "Variant":   catalog_url,
                    }
                })

        available_apps = {k: v for k, v in sorted(available_apps.items(), key=lambda x: x[1]['Version'])}
        return available_apps


    def _list_newest_installers_only(self) -> dict:
        """
        Returns a dictionary of the newest macOS installers only.
        Primarily used to avoid overwhelming the user with a list of
        installers that are not the newest version.

        Returns:
            dict: A dictionary of the newest macOS installers only.
        """

        if self.available_apps is None:
            return {}

        newest_apps: dict = self.available_apps.copy()
        supported_versions = ["10.13", "10.14", "10.15", "11", "12", "13"]


        for version in supported_versions:
            remote_version_minor = 0
            remote_version_security = 0
            os_builds = []

            # First determine the largest version
            for ia in newest_apps:
                if newest_apps[ia]["Version"].startswith(version):
                    if newest_apps[ia]["Variant"] not in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                        remote_version = newest_apps[ia]["Version"].split(".")
                        if remote_version[0] == "10":
                            remote_version.pop(0)
                            remote_version.pop(0)
                        else:
                            remote_version.pop(0)
                        if int(remote_version[0]) > remote_version_minor:
                            remote_version_minor = int(remote_version[0])
                            remote_version_security = 0 # Reset as new minor version found
                        if len(remote_version) > 1:
                            if int(remote_version[1]) > remote_version_security:
                                remote_version_security = int(remote_version[1])

            # Now remove all versions that are not the largest
            for ia in list(newest_apps):
                # Don't use Beta builds to determine latest version
                if newest_apps[ia]["Variant"] in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                    continue

                if newest_apps[ia]["Version"].startswith(version):
                    remote_version = newest_apps[ia]["Version"].split(".")
                    if remote_version[0] == "10":
                        remote_version.pop(0)
                        remote_version.pop(0)
                    else:
                        remote_version.pop(0)
                    if int(remote_version[0]) < remote_version_minor:
                        newest_apps.pop(ia)
                        continue
                    if int(remote_version[0]) == remote_version_minor:
                        if len(remote_version) > 1:
                            if int(remote_version[1]) < remote_version_security:
                                newest_apps.pop(ia)
                                continue
                        else:
                            if remote_version_security > 0:
                                newest_apps.pop(ia)
                                continue

                    # Remove duplicate builds
                    #   ex.  macOS 12.5.1 has 2 builds in the Software Update Catalog
                    #   ref: https://twitter.com/classicii_mrmac/status/1560357471654379522
                    if newest_apps[ia]["Build"] in os_builds:
                        newest_apps.pop(ia)
                        continue

                    os_builds.append(newest_apps[ia]["Build"])

        # Final passthrough
        # Remove Betas if there's a non-beta version available
        for ia in list(newest_apps):
            if newest_apps[ia]["Variant"] in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                for ia2 in newest_apps:
                    if newest_apps[ia2]["Version"].split(".")[0] == newest_apps[ia]["Version"].split(".")[0] and newest_apps[ia2]["Variant"] not in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                        newest_apps.pop(ia)
                        break

        return newest_apps


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

            app_version = application_info_plist["DTPlatformVersion"]
            clean_name = application_info_plist["CFBundleDisplayName"]

            if "DTSDKBuild" in application_info_plist:
                app_sdk = application_info_plist["DTSDKBuild"]
            else:
                app_sdk = "Unknown"

            # app_version can sometimes report GM instead of the actual version
            # This is a workaround to get the actual version
            if app_version.startswith("GM"):
                try:
                    app_version = int(app_sdk[:2])
                    if app_version < 20:
                        app_version = f"10.{app_version - 4}"
                    else:
                        app_version = f"{app_version - 9}.0"
                except ValueError:
                    app_version = "Unknown"

            # Check if App Version is High Sierra or newer
            if os_data.os_conversion.os_to_kernel(app_version) < os_data.os_data.high_sierra:
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
                    "hdiutil", "attach", "-noverify", sharedsupport_path,
                    "-mountpoint", tmpdir,
                    "-nobrowse",
                ],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            if output.returncode != 0:
                return (detected_build, detected_os)

            ss_info = Path(SFR_SOFTWARE_UPDATE_PATH)

            if Path(tmpdir / ss_info).exists():
                plist = plistlib.load((tmpdir / ss_info).open("rb"))
                if "Assets" in plist:
                    if "Build" in plist["Assets"][0]:
                        detected_build = plist["Assets"][0]["Build"]
                    if "OSVersion" in plist["Assets"][0]:
                        detected_os = plist["Assets"][0]["OSVersion"]

            # Unmount SharedSupport.dmg
            subprocess.run(["hdiutil", "detach", tmpdir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return (detected_build, detected_os)