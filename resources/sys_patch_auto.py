# Auto Patching's main purpose is to try and tell the user they're missing root patches
# New users may not realize OS updates remove our patches, so we try and run when nessasary
# Conditions for running:
#   - Verify running GUI (TUI users can write their own scripts)
#   - Verify the Snapshot Seal is intact (if not, assume user is running patches)
#   - Verify this model needs patching (if not, assume user upgraded hardware and OCLP was not removed)
#   - Verify there are no updates for OCLP (ensure we have the latest patch sets)
# If all these tests pass, start Root Patcher
# Copyright (C) 2022, Mykola Grymalyuk

from pathlib import Path
import plistlib
import subprocess
import webbrowser
from resources import sys_patch_detect, utilities, sys_patch_detect, updates, global_settings
from gui import gui_main

class AutomaticSysPatch:
    def start_auto_patch(settings):
        print("- Starting Automatic Patching")
        if settings.wxpython_variant is True:
            if utilities.check_seal() is True:
                print("- Detected Snapshot seal intact, detecting patches")
                patches = sys_patch_detect.detect_root_patch(settings.computer.real_model, settings).detect_patch_set()
                if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
                    patches = []
                if patches:
                    print("- Detected applicable patches, determining whether possible to patch")
                    if patches["Validation: Patching Possible"] is True:
                        print("- Determined patching is possible, checking for OCLP updates")
                        patch_string = ""
                        for patch in patches:
                            if patches[patch] is True and not patch.startswith("Settings") and not patch.startswith("Validation"):
                                patch_string += f"- {patch}\n"
                        # Check for updates
                        dict = updates.check_binary_updates(settings).check_binary_updates()
                        if not dict:
                            print("- No new binaries found on Github, proceeding with patching")
                            if settings.launcher_script is None:
                                args_string = f"'{settings.launcher_binary}' --gui_patch"
                            else:
                                args_string = f"{settings.launcher_binary} {settings.launcher_script} --gui_patch"

                            warning_str = ""
                            if utilities.verify_network_connection("https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest") is False:
                                warning_str = f"""\n\nWARNING: We're unable to verify whether there are any new releases of OpenCore Legacy Patcher on Github. Be aware that you may be using an outdated version for this OS. If you're unsure, verify on Github that OpenCore Legacy Patcher {settings.patcher_version} is the latest official release"""

                            args = [
                                "osascript",
                                "-e",
                                f"""display dialog "OpenCore Legacy Patcher has detected you're running without Root Patches, and would like to install them.\n\nmacOS wipes all root patches during OS installs and updates, so they need to be reinstalled.\n\nFollowing Patches have been detected for your system: \n{patch_string}\nWould you like to apply these patches?{warning_str}" """
                                f'with icon POSIX file "{settings.app_icon_path}"',
                            ]
                            output = subprocess.run(
                                args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                            )
                            if output.returncode == 0:
                                args = [
                                    "osascript",
                                    "-e",
                                    f'''do shell script "{args_string}"'''
                                    f' with prompt "OpenCore Legacy Patcher would like to patch your root volume"'
                                    " with administrator privileges"
                                    " without altering line endings"
                                ]
                                subprocess.run(
                                    args,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT
                                )
                        else:
                            version = dict[0]["Version"]
                            github_link = dict[0]["Github Link"]
                            print(f"- Found new version: {version}")

                            # launch oascript to ask user if they want to apply the update
                            # if yes, open the link in the default browser
                            # we never want to run the root patcher if there are updates available
                            args = [
                                "osascript",
                                "-e",
                                f"""display dialog "OpenCore Legacy Patcher has detected you're running without Root Patches, and would like to install them.\n\nHowever we've detected a new version of OCLP on Github. Would you like to view this?\n\nCurrent Version: {settings.patcher_version}\nLatest Version: {version}\n\nNote: After downloading the latest OCLP version, open the app and run the 'Post Install Root Patcher' from the main menu." """
                                f'with icon POSIX file "{settings.app_icon_path}"',
                            ]
                            output = subprocess.run(
                                args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                            )
                            if output.returncode == 0:
                                webbrowser.open(github_link)
                    else:
                        print("- Cannot run patching")
                else:
                    print("- No patches detected")
                    AutomaticSysPatch.determine_if_boot_matches(settings)
            else:
                print("- Detected Snapshot seal not intact, skipping")
                AutomaticSysPatch.determine_if_boot_matches(settings)
        else:
            print("- Auto Patch option is not supported on TUI, please use GUI")

    def determine_if_boot_matches(settings):
        # Goal of this function is to determine whether the user
        # is using a USB drive to Boot OpenCore but macOS does not
        # reside on the same drive as the USB.

        # If we determine them to be mismatched, notify the user
        # and ask if they want to install to install to disk

        print("- Determining if macOS drive matches boot drive")

        should_notify = global_settings.global_settings().read_property("AutoPatch_Notify_Mismatched_Disks")
        if should_notify is False:
            print("- Skipping due to user preference")
        elif settings.host_is_hackintosh is True:
            print("- Skipping due to hackintosh")
        else:
            if settings.booted_oc_disk:
                root_disk = settings.booted_oc_disk.strip("disk")
                root_disk = "disk" + root_disk.split("s")[0]

                print(f"  - Boot Drive: {settings.booted_oc_disk} ({root_disk})")
                macOS_disk = utilities.get_disk_path()
                print(f"  - macOS Drive: {macOS_disk}")
                physical_stores = utilities.find_apfs_physical_volume(macOS_disk)
                print(f"  - APFS Physical Stores: {physical_stores}")

                disk_match = False
                for disk in physical_stores:
                    if root_disk in disk:
                        print(f"- Boot drive matches macOS drive ({disk})")
                        disk_match = True
                        break

                if disk_match is False:
                    # Check if OpenCore is on a USB drive
                    print("- Boot Drive does not match macOS drive, checking if OpenCore is on a USB drive")

                    disk_info = plistlib.loads(subprocess.run(["diskutil", "info", "-plist", root_disk], stdout=subprocess.PIPE).stdout)
                    try:
                        if disk_info["Ejectable"] is True:
                            print("- Boot Disk is ejectable, prompting user to install to internal")

                            args = [
                                "osascript",
                                "-e",
                                f"""display dialog "OpenCore Legacy Patcher has detected that you are booting OpenCore from an USB or External drive.\n\nIf you would like to boot your Mac normally without a USB drive plugged in, you can install OpenCore to the internal hard drive.\n\nWould you like to launch OpenCore Legacy Patcher and install to disk?" """
                                f'with icon POSIX file "{settings.app_icon_path}"',
                            ]
                            output = subprocess.run(
                                args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                            )
                            if output.returncode == 0:
                                print("- Launching GUI's Build/Install menu")
                                settings.start_build_install = True
                                gui_main.wx_python_gui(settings).main_menu(None)
                        else:
                            print("- Boot Disk is not removable, skipping prompt")
                    except KeyError:
                        print("- Unable to determine if boot disk is removable, skipping prompt")

            else:
                print("- Failed to find disk OpenCore launched from")


    def install_auto_patcher_launch_agent(settings):
        # Installs the following:
        #   - OpenCore-Patcher.app in /Library/Application Support/Dortania/
        #   - com.dortania.opencore-legacy-patcher.auto-patch.plist in /Library/LaunchAgents/
        if settings.launcher_script is None:
            # Verify our binary isn't located in '/Library/Application Support/Dortania/'
            # As we'd simply be duplicating ourselves
            if not settings.launcher_binary.startswith("/Library/Application Support/Dortania/"):
                print("- Installing Auto Patcher Launch Agent")

                if not Path("Library/Application Support/Dortania").exists():
                    print("- Creating /Library/Application Support/Dortania/")
                    utilities.process_status(utilities.elevated(["mkdir", "-p", "/Library/Application Support/Dortania"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                print("- Copying OpenCore Patcher to /Library/Application Support/Dortania/")
                if Path("/Library/Application Support/Dortania/OpenCore-Patcher.app").exists():
                    print("- Deleting existing OpenCore-Patcher")
                    utilities.process_status(utilities.elevated(["rm", "-R", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                # Strip everything after OpenCore-Patcher.app
                path = str(settings.launcher_binary).split("/Contents/MacOS/OpenCore-Patcher")[0]
                print(f"- Copying {path} to /Library/Application Support/Dortania/")
                utilities.process_status(utilities.elevated(["cp", "-R", path, "/Library/Application Support/Dortania/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                if not Path("/Library/Application Support/Dortania/OpenCore-Patcher.app").exists():
                    # Sometimes the binary the user launches maye have a suffix (ie. OpenCore-Patcher 3.app)
                    # We'll want to rename it to OpenCore-Patcher.app
                    path = path.split("/")[-1]
                    print(f"- Renaming {path} to OpenCore-Patcher.app")
                    utilities.process_status(utilities.elevated(["mv", f"/Library/Application Support/Dortania/{path}", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Copy over our launch agent
            print("- Copying auto-patch.plist Launch Agent to /Library/LaunchAgents/")
            if Path("/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist").exists():
                print("- Deleting existing auto-patch.plist")
                utilities.process_status(utilities.elevated(["rm", "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["cp", settings.auto_patch_launch_agent_path, "/Library/LaunchAgents/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Set the permissions on the com.dortania.opencore-legacy-patcher.auto-patch.plist
            print("- Setting permissions on auto-patch.plist")
            utilities.process_status(utilities.elevated(["chmod", "644", "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "root:wheel", "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Making app alias
            # Simply an easy way for users to notice the app
            # If there's already an alias or exiting app, skip
            if not Path("/Applications/OpenCore-Patcher.app").exists():
                print("- Making app alias")
                utilities.process_status(utilities.elevated(["ln", "-s", "/Library/Application Support/Dortania/OpenCore-Patcher.app", "/Applications/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            print("- Skipping Auto Patcher Launch Agent, not supported when running from source")