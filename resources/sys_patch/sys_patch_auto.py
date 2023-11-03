# Copyright (C) 2022, Mykola Grymalyuk
# Copyright (c) 2023 Jazzzny

import wx
import wx.html2
import requests
import markdown2
import logging
import plistlib
import subprocess
import webbrowser
import hashlib

from pathlib import Path


from resources import utilities, updates, global_settings, network_handler, constants
from resources.sys_patch import sys_patch_detect
from resources.wx_gui import gui_entry, gui_support


class AutomaticSysPatch:
    """
    Library of functions for launch agent, including automatic patching
    """

    def __init__(self, global_constants: constants.Constants):
        self.constants: constants.Constants = global_constants


    def start_auto_patch(self):
        """
        Initiates automatic patching

        Auto Patching's main purpose is to try and tell the user they're missing root patches
        New users may not realize OS updates remove our patches, so we try and run when nessasary

        Conditions for running:
            - Verify running GUI (TUI users can write their own scripts)
            - Verify the Snapshot Seal is intact (if not, assume user is running patches)
            - Verify this model needs patching (if not, assume user upgraded hardware and OCLP was not removed)
            - Verify there are no updates for OCLP (ensure we have the latest patch sets)

        If all these tests pass, start Root Patcher

        """

        logging.info("- Starting Automatic Patching")
        if self.constants.wxpython_variant is False:
            logging.info("- Auto Patch option is not supported on TUI, please use GUI")
            return

        dict = updates.CheckBinaryUpdates(self.constants).check_binary_updates()
        if dict:
            version = dict["Version"]
            logging.info(f"- Found new version: {version}")

            app = wx.App()
            mainframe = wx.Frame(None, -1, "OpenCore Legacy Patcher")

            ID_GITHUB = wx.NewId()
            ID_UPDATE = wx.NewId()

            url = "https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest"
            response = requests.get(url).json()
            try:
                changelog = response["body"].split("## Asset Information")[0]
            except: #if user constantly checks for updates, github will rate limit them
                changelog = """## Unable to fetch changelog

Please check the Github page for more information about this release."""

            html_markdown = markdown2.markdown(changelog)
            html_css = """
    <style>
        body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.5;
        font-size: 13px;
        margin-top: 20px;
        background-color: rgb(238,238,238);
        }
        h2 {
        line-height: 0.5;
        padding-left: 10px;
        }
        a {
            color: -apple-system-control-accent;
        }
        @media (prefers-color-scheme: dark) {
            body {
                color: #fff;
                background-color: rgb(47,47,47);
            }

        }
    </style>
    """
            frame = wx.Dialog(None, -1, title="", size=(650, 500))
            frame.SetMinSize((650, 500))
            frame.SetWindowStyle(wx.STAY_ON_TOP)
            panel = wx.Panel(frame)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddSpacer(10)
            self.title_text = wx.StaticText(panel, label="A new version of OpenCore Legacy Patcher is available!")
            self.description = wx.StaticText(panel, label=f"OpenCore Legacy Patcher {version} is now available - You have {self.constants.patcher_version}{' (Nightly)' if not self.constants.commit_info[0].startswith('refs/tags') else ''}. Would you like to update?")
            self.title_text.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
            self.description.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            self.web_view = wx.html2.WebView.New(panel, style=wx.BORDER_SUNKEN)
            html_code = html_css+html_markdown.replace("<a href=", "<a target='_blank' href=")
            self.web_view.SetPage(html_code, "")
            self.web_view.Bind(wx.html2.EVT_WEBVIEW_NEWWINDOW, self._onWebviewNav)
            self.web_view.EnableContextMenu(False)
            self.close_button = wx.Button(panel, label="Ignore")
            self.close_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(wx.ID_CANCEL))
            self.view_button = wx.Button(panel, ID_GITHUB, label="View on GitHub")
            self.view_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_GITHUB))
            self.install_button = wx.Button(panel, label="Download and Install")
            self.install_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_UPDATE))
            self.install_button.SetDefault()

            buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
            buttonsizer.Add(self.close_button, 0, wx.ALIGN_CENTRE | wx.RIGHT, 5)
            buttonsizer.Add(self.view_button, 0, wx.ALIGN_CENTRE | wx.LEFT|wx.RIGHT, 5)
            buttonsizer.Add(self.install_button, 0, wx.ALIGN_CENTRE | wx.LEFT, 5)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.title_text, 0, wx.ALIGN_CENTRE | wx.TOP, 20)
            sizer.Add(self.description, 0, wx.ALIGN_CENTRE | wx.BOTTOM, 20)
            sizer.Add(self.web_view, 1, wx.EXPAND | wx.LEFT|wx.RIGHT, 10)
            sizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 20)
            panel.SetSizer(sizer)
            frame.Centre()

            result = frame.ShowModal()


            if result == ID_GITHUB:
                webbrowser.open(dict["Github Link"])
            elif result == ID_UPDATE:
                gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.UPDATE_APP)


            return

        if utilities.check_seal() is True:
            logging.info("- Detected Snapshot seal intact, detecting patches")
            patches = sys_patch_detect.DetectRootPatch(self.constants.computer.real_model, self.constants).detect_patch_set()
            if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
                patches = []
            if patches:
                logging.info("- Detected applicable patches, determining whether possible to patch")
                if patches["Validation: Patching Possible"] is False:
                    logging.info("- Cannot run patching")
                    return

                logging.info("- Determined patching is possible, checking for OCLP updates")
                patch_string = ""
                for patch in patches:
                    if patches[patch] is True and not patch.startswith("Settings") and not patch.startswith("Validation"):
                        patch_string += f"- {patch}\n"

                logging.info("- No new binaries found on Github, proceeding with patching")
                if self.constants.launcher_script is None:
                    args_string = f"'{self.constants.launcher_binary}' --gui_patch"
                else:
                    args_string = f"{self.constants.launcher_binary} {self.constants.launcher_script} --gui_patch"

                warning_str = ""
                if network_handler.NetworkUtilities("https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest").verify_network_connection() is False:
                    warning_str = f"""\n\nWARNING: We're unable to verify whether there are any new releases of OpenCore Legacy Patcher on Github. Be aware that you may be using an outdated version for this OS. If you're unsure, verify on Github that OpenCore Legacy Patcher {self.constants.patcher_version} is the latest official release"""

                args = [
                    "osascript",
                    "-e",
                    f"""display dialog "OpenCore Legacy Patcher has detected you're running without Root Patches, and would like to install them.\n\nmacOS wipes all root patches during OS installs and updates, so they need to be reinstalled.\n\nFollowing Patches have been detected for your system: \n{patch_string}\nWould you like to apply these patches?{warning_str}" """
                    f'with icon POSIX file "{self.constants.app_icon_path}"',
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
                return
            else:
                logging.info("- No patches detected")
        else:
            logging.info("- Detected Snapshot seal not intact, skipping")

        if self._determine_if_versions_match():
            self._determine_if_boot_matches()

    def _onWebviewNav(self, event):
        url = event.GetURL()
        webbrowser.open(url)

    def _determine_if_versions_match(self):
        """
        Determine if the booted version of OCLP matches the installed version

        ie. Installed app is 0.2.0, but EFI version is 0.1.0

        Returns:
            bool: True if versions match, False if not
        """

        logging.info("- Checking booted vs installed OCLP Build")
        if self.constants.computer.oclp_version is None:
            logging.info("- Booted version not found")
            return True

        if self.constants.computer.oclp_version == self.constants.patcher_version:
            logging.info("- Versions match")
            return True

        if self.constants.special_build is True:
            # Version doesn't match and we're on a special build
            # Special builds don't have good ways to compare versions
            logging.info("- Special build detected, assuming installed is older")
            return False

        # Check if installed version is newer than booted version
        if updates.CheckBinaryUpdates(self.constants).check_if_newer(self.constants.computer.oclp_version):
            logging.info("- Installed version is newer than booted version")
            return True

        args = [
            "osascript",
            "-e",
            f"""display dialog "OpenCore Legacy Patcher has detected that you are booting {'a different' if self.constants.special_build else 'an outdated'} OpenCore build\n- Booted: {self.constants.computer.oclp_version}\n- Installed: {self.constants.patcher_version}\n\nWould you like to update the OpenCore bootloader?" """
            f'with icon POSIX file "{self.constants.app_icon_path}"',
        ]
        output = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        if output.returncode == 0:
            logging.info("- Launching GUI's Build/Install menu")
            self.constants.start_build_install = True
            gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.BUILD_OC)

        return False


    def _determine_if_boot_matches(self):
        """
        Determine if the boot drive matches the macOS drive
        ie. Booted from USB, but macOS is on internal disk

        Goal of this function is to determine whether the user
        is using a USB drive to Boot OpenCore but macOS does not
        reside on the same drive as the USB.

        If we determine them to be mismatched, notify the user
        and ask if they want to install to install to disk.
        """

        logging.info("- Determining if macOS drive matches boot drive")

        should_notify = global_settings.GlobalEnviromentSettings().read_property("AutoPatch_Notify_Mismatched_Disks")
        if should_notify is False:
            logging.info("- Skipping due to user preference")
            return
        if self.constants.host_is_hackintosh is True:
            logging.info("- Skipping due to hackintosh")
            return
        if not self.constants.booted_oc_disk:
            logging.info("- Failed to find disk OpenCore launched from")
            return

        root_disk = self.constants.booted_oc_disk.strip("disk")
        root_disk = "disk" + root_disk.split("s")[0]

        logging.info(f"  - Boot Drive: {self.constants.booted_oc_disk} ({root_disk})")
        macOS_disk = utilities.get_disk_path()
        logging.info(f"  - macOS Drive: {macOS_disk}")
        physical_stores = utilities.find_apfs_physical_volume(macOS_disk)
        logging.info(f"  - APFS Physical Stores: {physical_stores}")

        disk_match = False
        for disk in physical_stores:
            if root_disk in disk:
                logging.info(f"- Boot drive matches macOS drive ({disk})")
                disk_match = True
                break

        if disk_match is True:
            return

        # Check if OpenCore is on a USB drive
        logging.info("- Boot Drive does not match macOS drive, checking if OpenCore is on a USB drive")

        disk_info = plistlib.loads(subprocess.run(["diskutil", "info", "-plist", root_disk], stdout=subprocess.PIPE).stdout)
        try:
            if disk_info["Ejectable"] is False:
                logging.info("- Boot Disk is not removable, skipping prompt")
                return

            logging.info("- Boot Disk is ejectable, prompting user to install to internal")

            args = [
                "osascript",
                "-e",
                f"""display dialog "OpenCore Legacy Patcher has detected that you are booting OpenCore from an USB or External drive.\n\nIf you would like to boot your Mac normally without a USB drive plugged in, you can install OpenCore to the internal hard drive.\n\nWould you like to launch OpenCore Legacy Patcher and install to disk?" """
                f'with icon POSIX file "{self.constants.app_icon_path}"',
            ]
            output = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            if output.returncode == 0:
                logging.info("- Launching GUI's Build/Install menu")
                self.constants.start_build_install = True
                gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.BUILD_OC)

        except KeyError:
            logging.info("- Unable to determine if boot disk is removable, skipping prompt")


    def install_auto_patcher_launch_agent(self, kdk_caching_needed: bool = False):
        """
        Install the Auto Patcher Launch Agent

        Installs the following:
            - OpenCore-Patcher.app in /Library/Application Support/Dortania/
            - com.dortania.opencore-legacy-patcher.auto-patch.plist in /Library/LaunchAgents/

        See start_auto_patch() comments for more info
        """

        if self.constants.launcher_script is not None:
            logging.info("- Skipping Auto Patcher Launch Agent, not supported when running from source")
            return

        services = {
            self.constants.auto_patch_launch_agent_path:        "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist",
            self.constants.update_launch_daemon_path:           "/Library/LaunchDaemons/com.dortania.opencore-legacy-patcher.macos-update.plist",
            **({ self.constants.rsr_monitor_launch_daemon_path: "/Library/LaunchDaemons/com.dortania.opencore-legacy-patcher.rsr-monitor.plist" } if self._create_rsr_monitor_daemon() else {}),
            **({ self.constants.kdk_launch_daemon_path:         "/Library/LaunchDaemons/com.dortania.opencore-legacy-patcher.os-caching.plist" } if kdk_caching_needed is True else {} ),
        }

        for service in services:
            name = Path(service).name
            logging.info(f"- Installing {name}")
            if Path(services[service]).exists():
                if hashlib.sha256(open(service, "rb").read()).hexdigest() == hashlib.sha256(open(services[service], "rb").read()).hexdigest():
                    logging.info(f"  - {name} checksums match, skipping")
                    continue
                logging.info(f"  - Existing service found, removing")
                utilities.process_status(utilities.elevated(["rm", services[service]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            # Create parent directories
            if not Path(services[service]).parent.exists():
                logging.info(f"  - Creating {Path(services[service]).parent} directory")
                utilities.process_status(utilities.elevated(["mkdir", "-p", Path(services[service]).parent], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["cp", service, services[service]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Set the permissions on the service
            utilities.process_status(utilities.elevated(["chmod", "644", services[service]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "root:wheel", services[service]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        if self.constants.launcher_binary.startswith("/Library/Application Support/Dortania/"):
            logging.info("- Skipping Patcher Install, already installed")
            return

        # Verify our binary isn't located in '/Library/Application Support/Dortania/'
        # As we'd simply be duplicating ourselves
        logging.info("- Installing Auto Patcher Launch Agent")

        if not Path("Library/Application Support/Dortania").exists():
            logging.info("- Creating /Library/Application Support/Dortania/")
            utilities.process_status(utilities.elevated(["mkdir", "-p", "/Library/Application Support/Dortania"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        logging.info("- Copying OpenCore Patcher to /Library/Application Support/Dortania/")
        if Path("/Library/Application Support/Dortania/OpenCore-Patcher.app").exists():
            logging.info("- Deleting existing OpenCore-Patcher")
            utilities.process_status(utilities.elevated(["rm", "-R", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        # Strip everything after OpenCore-Patcher.app
        path = str(self.constants.launcher_binary).split("/Contents/MacOS/OpenCore-Patcher")[0]
        logging.info(f"- Copying {path} to /Library/Application Support/Dortania/")
        utilities.process_status(utilities.elevated(["ditto", path, "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        if not Path("/Library/Application Support/Dortania/OpenCore-Patcher.app").exists():
            # Sometimes the binary the user launches may have a suffix (ie. OpenCore-Patcher 3.app)
            # We'll want to rename it to OpenCore-Patcher.app
            path = path.split("/")[-1]
            logging.info(f"- Renaming {path} to OpenCore-Patcher.app")
            utilities.process_status(utilities.elevated(["mv", f"/Library/Application Support/Dortania/{path}", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        subprocess.run(["xattr", "-cr", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Making app alias
        # Simply an easy way for users to notice the app
        # If there's already an alias or exiting app, skip
        if not Path("/Applications/OpenCore-Patcher.app").exists():
            logging.info("- Making app alias")
            utilities.process_status(utilities.elevated(["ln", "-s", "/Library/Application Support/Dortania/OpenCore-Patcher.app", "/Applications/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))


    def _create_rsr_monitor_daemon(self) -> bool:
        # Get kext list in /Library/Extensions that have the 'GPUCompanionBundles' property
        # This is used to determine if we need to run the RSRMonitor
        logging.info("- Checking if RSRMonitor is needed")

        cryptex_path = f"/System/Volumes/Preboot/{utilities.get_preboot_uuid()}/cryptex1/current/OS.dmg"
        if not Path(cryptex_path).exists():
            logging.info("- No OS.dmg, skipping RSRMonitor")
            return False

        kexts = []
        for kext in Path("/Library/Extensions").glob("*.kext"):
            if not Path(f"{kext}/Contents/Info.plist").exists():
                continue
            try:
                kext_plist = plistlib.load(open(f"{kext}/Contents/Info.plist", "rb"))
            except Exception as e:
                logging.info(f"  - Failed to load plist for {kext.name}: {e}")
                continue
            if "GPUCompanionBundles" not in kext_plist:
                continue
            logging.info(f"  - Found kext with GPUCompanionBundles: {kext.name}")
            kexts.append(kext.name)

        # If we have no kexts, we don't need to run the RSRMonitor
        if not kexts:
            logging.info("- No kexts found with GPUCompanionBundles, skipping RSRMonitor")
            return False

        # Load the RSRMonitor plist
        rsr_monitor_plist = plistlib.load(open(self.constants.rsr_monitor_launch_daemon_path, "rb"))

        arguments = ["rm", "-Rfv"]
        arguments += [f"/Library/Extensions/{kext}" for kext in kexts]

        # Add the arguments to the RSRMonitor plist
        rsr_monitor_plist["ProgramArguments"] = arguments

        # Next add monitoring for '/System/Volumes/Preboot/{UUID}/cryptex1/OS.dmg'
        logging.info(f"  - Adding monitor: {cryptex_path}")
        rsr_monitor_plist["WatchPaths"] = [
            cryptex_path,
        ]

        # Write the RSRMonitor plist
        plistlib.dump(rsr_monitor_plist, Path(self.constants.rsr_monitor_launch_daemon_path).open("wb"))

        return True
