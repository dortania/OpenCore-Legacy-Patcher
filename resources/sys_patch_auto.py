# Auto Patching's main purpose is to try and tell the user they're missing root patches
# New users may not realize OS updates remove our patches, so we try and run when nessasary
# Conditions for running:
#   - Verify running GUI (TUI users can write their own scripts)
#   - Verify the Snapshot Seal is in tact (if not, assume user is running patches)
#   - Verify this model needs patching (if not, assume user upgraded hardware and OCLP was not removed)
#   - Verify there are no updates for OCLP (ensure we have the latest patch sets)
# If all these tests pass, start Root Patcher
# Copyright (C) 2022, Mykola Grymalyuk

import subprocess
import webbrowser
from resources import sys_patch_detect, utilities, sys_patch_detect, updates

class AutomaticSysPatch:
    def start_auto_patch(settings):
        print("- Starting Automatic Patching")
        if settings.wxpython_variant is True:
            if utilities.check_seal() is True:
                print("- Detected Snapshot seal in tact, detecting patches")
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
                            for entry in dict:
                                version = dict[entry]["Version"]
                                github_link = dict[entry]["Github Link"]
                                print(f"- Found new version: {version}")

                                # launch oascript to ask user if they want to apply the update
                                # if yes, open the link in the default browser
                                # we never want to run the root patcher if there are updates available
                                args = [
                                    "osascript",
                                    "-e",
                                    f"""display dialog "OpenCore Legacy Patcher has detected you're running without Root Patches, and would like to install them.\n\nHowever we've detected a new version of OCLP on Github. Would you like to view this?\n\nCurrent Version: {settings.patcher_version}\nRemote Version: {version}" """
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
            else:
                print("- Detected Snapshot seal not in tact, skipping")
        else:
            print("- Auto Patch option is not supported on TUI, please use GUI")