# Creates a macOS Installer
from pathlib import Path
import plistlib
import subprocess
import requests
import tempfile
from resources import utilities, tui_helpers

def list_local_macOS_installers():
    # Finds all applicable macOS installers
    # within a user's /Applications folder
    # Returns a list of installers
    application_list = {}

    for application in Path("/Applications").iterdir():
        # Verify whether application has createinstallmedia
        try:
            if (Path("/Applications") / Path(application) / Path("Contents/Resources/createinstallmedia")).exists():
                plist = plistlib.load((Path("/Applications") / Path(application) / Path("Contents/Info.plist")).open("rb"))
                try:
                    # Doesn't reflect true OS build, but best to report SDK in the event multiple installers are found with same version
                    app_version = plist["DTPlatformVersion"]
                    clean_name = plist["CFBundleDisplayName"]
                    try:
                        app_sdk = plist["DTSDKBuild"]
                    except KeyError:
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
                    can_add = False
                    if app_version.startswith("10."):
                        app_sub_version = app_version.split(".")[1]
                        if int(app_sub_version) >= 13:
                            can_add = True
                        else:
                            can_add = False
                    else:
                        can_add = True

                    # Check SharedSupport.dmg's data
                    results = parse_sharedsupport_version(Path("/Applications") / Path(application)/ Path("Contents/SharedSupport/SharedSupport.dmg"))
                    if results[0] is not None:
                        app_sdk = results[0]
                    if results[1] is not None:
                        app_version = results[1]

                    if can_add is True:
                        application_list.update({
                            application: {
                            "Short Name": clean_name,
                            "Version": app_version,
                            "Build": app_sdk,
                            "Path": application,
                            }
                        })
                except KeyError:
                    pass
        except PermissionError:
            pass
    # Sort Applications by version
    application_list = {k: v for k, v in sorted(application_list.items(), key=lambda item: item[1]["Version"])}
    return application_list

def parse_sharedsupport_version(sharedsupport_path):
    detected_build =     None
    detected_os =        None
    sharedsupport_path = Path(sharedsupport_path)

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

        ss_info = Path("SFR/com_apple_MobileAsset_SFRSoftwareUpdate/com_apple_MobileAsset_SFRSoftwareUpdate.xml")

        if Path(tmpdir / ss_info).exists():
            plist = plistlib.load((tmpdir / ss_info).open("rb"))
            if "Build" in plist["Assets"][0]:
                detected_build = plist["Assets"][0]["Build"]
            if "OSVersion" in plist["Assets"][0]:
                detected_os = plist["Assets"][0]["OSVersion"]

        # Unmount SharedSupport.dmg
        output = subprocess.run(["hdiutil", "detach", tmpdir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return (detected_build, detected_os)


def create_installer(installer_path, volume_name):
    # Creates a macOS installer
    # Takes a path to the installer and the Volume
    # Returns boolean on success status

    createinstallmedia_path = Path("/Applications") / Path(installer_path) / Path("Contents/Resources/createinstallmedia")

    # Sanity check in the event the user somehow deleted it between the time we found it and now
    if (createinstallmedia_path).exists():
        utilities.cls()
        utilities.header(["Starting createinstallmedia"])
        print("This will take some time, recommend making some coffee while you wait\n")
        utilities.elevated([createinstallmedia_path, "--volume", f"/Volumes/{volume_name}", "--nointeraction"])
        return True
    else:
        print("- Failed to find createinstallmedia")
    return False

def download_install_assistant(download_path, ia_link):
    # Downloads InstallAssistant.pkg
    if utilities.download_file(ia_link, (Path(download_path) / Path("InstallAssistant.pkg"))):
        return True
    return False

def install_macOS_installer(download_path):
    print("- Extracting macOS installer from InstallAssistant.pkg\n  This may take some time")
    args = [
        "osascript",
        "-e",
        f'''do shell script "installer -pkg {Path(download_path)}/InstallAssistant.pkg -target /"'''
        ' with prompt "OpenCore Legacy Patcher needs administrator privileges to add InstallAssistant."'
        " with administrator privileges"
        " without altering line endings",
    ]

    result = subprocess.run(args,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("- InstallAssistant installed")
        return True
    else:
        print("- Failed to install InstallAssistant")
        print(f"  Error Code: {result.returncode}")
        return False

def list_downloadable_macOS_installers(download_path, catalog):
    available_apps = {}
    if catalog == "DeveloperSeed":
        link = "https://swscan.apple.com/content/catalogs/others/index-13seed-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
    elif catalog == "PublicSeed":
        link = "https://swscan.apple.com/content/catalogs/others/index-13beta-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
    else:
        link = "https://swscan.apple.com/content/catalogs/others/index-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"

    if utilities.verify_network_connection(link) is True:
        try:
            catalog_plist = plistlib.loads(utilities.SESSION.get(link).content)
        except plistlib.InvalidFileException:
            return available_apps

        for item in catalog_plist["Products"]:
            try:
                # Check if entry has SharedSupport and BuildManifest
                # Ensures only Big Sur and newer Installers are listed
                catalog_plist["Products"][item]["ExtendedMetaInfo"]["InstallAssistantPackageIdentifiers"]["SharedSupport"]
                catalog_plist["Products"][item]["ExtendedMetaInfo"]["InstallAssistantPackageIdentifiers"]["BuildManifest"]

                for bm_package in catalog_plist["Products"][item]["Packages"]:
                    if "Info.plist" in bm_package["URL"] and "InstallInfo.plist" not in bm_package["URL"]:
                        try:
                            build_plist = plistlib.loads(utilities.SESSION.get(bm_package["URL"]).content)
                        except plistlib.InvalidFileException:
                            continue
                        # Ensure Apple Silicon specific Installers are not listed
                        if "VMM-x86_64" not in build_plist["MobileAssetProperties"]["SupportedDeviceModels"]:
                            continue
                        version = build_plist["MobileAssetProperties"]["OSVersion"]
                        build = build_plist["MobileAssetProperties"]["Build"]
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
                        for ia_package in catalog_plist["Products"][item]["Packages"]:
                            if "InstallAssistant.pkg" in ia_package["URL"]:
                                download_link = ia_package["URL"]
                                size = ia_package["Size"]
                                integrity = ia_package["IntegrityDataURL"]

                        available_apps.update({
                            item: {
                                "Version": version,
                                "Build": build,
                                "Link": download_link,
                                "Size": size,
                                "integrity": integrity,
                                "Source": "Apple Inc.",
                                "Variant": catalog_url,
                            }
                        })
            except KeyError:
                pass
        available_apps = {k: v for k, v in sorted(available_apps.items(), key=lambda x: x[1]['Version'])}
    return available_apps

def only_list_newest_installers(available_apps):
    # Takes a dictionary of available installers
    # Returns a dictionary of only the newest installers
    # This is used to avoid overwhelming the user with installer options

    # Only strip OSes that we know are supported
    supported_versions = ["10.13", "10.14", "10.15", "11", "12", "13"]

    for version in supported_versions:
        remote_version_minor = 0
        remote_version_security = 0
        os_builds = []

        # First determine the largest version
        for ia in available_apps:
            if available_apps[ia]["Version"].startswith(version):
                if available_apps[ia]["Variant"] not in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                    remote_version = available_apps[ia]["Version"].split(".")
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
        for ia in list(available_apps):
            # Don't use Beta builds to determine latest version
            if available_apps[ia]["Variant"] in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                continue

            if available_apps[ia]["Version"].startswith(version):
                remote_version = available_apps[ia]["Version"].split(".")
                if remote_version[0] == "10":
                    remote_version.pop(0)
                    remote_version.pop(0)
                else:
                    remote_version.pop(0)
                if int(remote_version[0]) < remote_version_minor:
                    available_apps.pop(ia)
                    continue
                if int(remote_version[0]) == remote_version_minor:
                    if len(remote_version) > 1:
                        if int(remote_version[1]) < remote_version_security:
                            available_apps.pop(ia)
                            continue
                    else:
                        if remote_version_security > 0:
                            available_apps.pop(ia)
                            continue

                # Remove duplicate builds
                #   ex.  macOS 12.5.1 has 2 builds in the Software Update Catalog
                #   ref: https://twitter.com/classicii_mrmac/status/1560357471654379522
                if available_apps[ia]["Build"] in os_builds:
                    available_apps.pop(ia)
                    continue

                os_builds.append(available_apps[ia]["Build"])

    # Final passthrough
    # Remove Betas if there's a non-beta version available
    for ia in list(available_apps):
        if available_apps[ia]["Variant"] in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
            for ia2 in available_apps:
                if available_apps[ia2]["Version"].split(".")[0] == available_apps[ia]["Version"].split(".")[0] and available_apps[ia2]["Variant"] not in ["CustomerSeed", "DeveloperSeed", "PublicSeed"]:
                    available_apps.pop(ia)
                    break

    return available_apps

def format_drive(disk_id):
    # Formats a disk for macOS install
    # Takes a disk ID
    # Returns boolean on success status
    header = f"# Formatting disk{disk_id} for macOS installer #"
    box_length = len(header)
    utilities.cls()
    print("#" * box_length)
    print(header)
    print("#" * box_length)
    print("")
    #print(f"- Formatting disk{disk_id} for macOS installer")
    format_process = utilities.elevated(["diskutil", "eraseDisk", "HFS+", "OCLP-Installer", f"disk{disk_id}"])
    if format_process.returncode == 0:
        print("- Disk formatted")
        return True
    else:
        print("- Failed to format disk")
        print(f"  Error Code: {format_process.returncode}")
        input("\nPress Enter to exit")
        return False

def select_disk_to_format():
    utilities.cls()
    utilities.header(["Installing OpenCore to Drive"])

    print("\nDisk picker is loading...")

    all_disks = {}
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
    menu = tui_helpers.TUIMenu(
        ["Select Disk to write the macOS Installer onto"],
        "Please select the disk you would like to install OpenCore to: ",
        in_between=["Missing drives? Verify they are 14GB+ and external (ie. USB)", "", "Ensure all data is backed up on selected drive, entire drive will be erased!"],
        return_number_instead_of_direct_call=True,
        loop=True,
    )
    for disk in all_disks:
        # Strip disks that are under 14GB (15,032,385,536 bytes)
        # createinstallmedia isn't great at detecting if a disk has enough space
        if not any(all_disks[disk]['size'] > 15032385536 for partition in all_disks[disk]):
            continue
        # Strip internal disks as well (avoid user formatting their SSD/HDD)
        # Ensure user doesn't format their boot drive
        if not any(all_disks[disk]['removable'] is False for partition in all_disks[disk]):
            continue
        menu.add_menu_option(f"{disk}: {all_disks[disk]['name']} ({utilities.human_fmt(all_disks[disk]['size'])})", key=disk[4:])

    response = menu.start()

    if response == -1:
        return None

    return response



def list_disk_to_format():
    all_disks = {}
    list_disks = {}
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
        print(f"disk {disk}: {all_disks[disk]['name']} ({utilities.human_fmt(all_disks[disk]['size'])})")
        list_disks.update({
            disk: {
                "identifier": all_disks[disk]["identifier"],
                "name": all_disks[disk]["name"],
                "size": all_disks[disk]["size"],
            }
        })
    return list_disks

# Create global tmp directory
tmp_dir = tempfile.TemporaryDirectory()

def generate_installer_creation_script(tmp_location, installer_path, disk):
    # Creates installer.sh to be piped to OCLP-Helper and run as admin
    # Goals:
    # - Format provided disk as HFS+ GPT
    # - Run createinstallmedia on provided disk
    # Implementing this into a single installer.sh script allows us to only call
    # OCLP-Helper once to avoid nagging the user about permissions

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

    print(f"Creating temporary directory at {ia_tmp}")
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
            print("Not enough free space to create installer.sh")
            print(f"{utilities.human_fmt(space_available)} available, {utilities.human_fmt(space_needed)} required")
            return False
    subprocess.run(args)

    # Adjust installer_path to point to the copied installer
    installer_path = Path(ia_tmp) / Path(Path(installer_path).name)
    if not Path(installer_path).exists():
        print(f"Failed to copy installer to {ia_tmp}")
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