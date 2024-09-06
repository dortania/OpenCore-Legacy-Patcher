"""
start.py: Start automatic patching of host
"""

import wx
import wx.html2

import logging
import plistlib
import requests
import markdown2
import subprocess
import webbrowser


from ... import constants

from ...datasets import css_data

from ...wx_gui import (
    gui_entry,
    gui_support
)
from ...support import (
    utilities,
    updates,
    global_settings,
    network_handler,
)
from ..patchsets import (
    HardwarePatchsetDetection,
    HardwarePatchsetValidation
)


class StartAutomaticPatching:
    """
    Start automatic patching of host
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

            html_markdown = markdown2.markdown(changelog, extras=["tables"])
            html_css = css_data.updater_css
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
            html_code = f'''
<html>
    <head>
        <style>
            {html_css}
        </style>
    </head>
    <body class="markdown-body">
        {html_markdown.replace("<a href=", "<a target='_blank' href=")}
    </body>
</html>
'''
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
            patches = HardwarePatchsetDetection(self.constants).device_properties
            if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
                patches = {}
            if patches:
                logging.info("- Detected applicable patches, determining whether possible to patch")
                if patches[HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE] is True:
                    logging.info("- Cannot run patching")
                    return

                logging.info("- Determined patching is possible, checking for OCLP updates")
                patch_string = ""
                for patch in patches:
                    if patches[patch] is True and not patch.startswith("Settings") and not patch.startswith("Validation"):
                        patch_string += f"- {patch}\n"

                logging.info("- No new binaries found on Github, proceeding with patching")

                warning_str = ""
                if network_handler.NetworkUtilities("https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/releases/latest").verify_network_connection() is False:
                    warning_str = f"""\n\nWARNING: We're unable to verify whether there are any new releases of OpenCore Legacy Patcher on Github. Be aware that you may be using an outdated version for this OS. If you're unsure, verify on Github that OpenCore Legacy Patcher {self.constants.patcher_version} is the latest official release"""

                args = [
                    "/usr/bin/osascript",
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
                    gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.SYS_PATCH, start_patching=True)
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
            "/usr/bin/osascript",
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

        disk_info = plistlib.loads(subprocess.run(["/usr/sbin/diskutil", "info", "-plist", root_disk], stdout=subprocess.PIPE).stdout)
        try:
            if disk_info["Ejectable"] is False:
                logging.info("- Boot Disk is not removable, skipping prompt")
                return

            logging.info("- Boot Disk is ejectable, prompting user to install to internal")

            args = [
                "/usr/bin/osascript",
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