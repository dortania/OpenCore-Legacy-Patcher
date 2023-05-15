
import wx
import os
import sys
import time
import logging
import plistlib
import traceback
import threading
import subprocess

from pathlib import Path

from resources import (
    constants,
    kdk_handler,
)
from resources.sys_patch import (
    sys_patch,
    sys_patch_detect
)
from resources.wx_gui import (
    gui_main_menu,
    gui_support,
    gui_download,
)
from data import os_data


class SysPatchFrame(wx.Frame):
    """
    Create a frame for root patching
    Uses a Modal Dialog for smoother transition from other frames
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None, patches: dict = {}):
        super(SysPatchFrame, self).__init__(parent, title=title, size=(350, 260), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.title = title
        self.constants: constants.Constants = global_constants
        self.frame_modal: wx.Dialog = None
        self.return_button: wx.Button = None

        self.frame_modal = wx.Dialog(self, title=title, size=(360, 200))
        self.SetPosition(screen_location) if screen_location else self.Centre()

        if patches:
            return

        self._generate_elements_display_patches(self.frame_modal, patches)
        self.frame_modal.ShowWindowModal()


    def _kdk_download(self, frame: wx.Frame = None) -> bool:
        frame = self if not frame else frame

        logging.info("KDK missing, generating KDK download frame")

        header = wx.StaticText(frame, label="Downloading Kernel Debug Kit", pos=(-1,5))
        header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        header.Center(wx.HORIZONTAL)

        subheader = wx.StaticText(frame, label="Fetching KDK database...", pos=(-1, header.GetPosition()[1] + header.GetSize()[1] + 5))
        subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        subheader.Center(wx.HORIZONTAL)

        progress_bar = wx.Gauge(frame, range=100, pos=(-1, subheader.GetPosition()[1] + subheader.GetSize()[1] + 5), size=(250, 20))
        progress_bar.Center(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        # Set size of frame
        frame.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 35))
        frame.Show()

        # Generate KDK object
        self.kdk_obj: kdk_handler.KernelDebugKitObject = None
        def kdk_thread_spawn():
            self.kdk_obj = kdk_handler.KernelDebugKitObject(self.constants, self.constants.detected_os_build, self.constants.detected_os_version)

        kdk_thread = threading.Thread(target=kdk_thread_spawn)
        kdk_thread.start()

        while kdk_thread.is_alive():
            wx.GetApp().Yield()

        if self.kdk_obj.success is False:
            progress_bar_animation.stop_pulse()
            progress_bar.SetValue(0)
            wx.MessageBox(f"KDK download failed: {self.kdk_obj.error_msg}", "Error", wx.OK | wx.ICON_ERROR)
            return False

        kdk_download_obj = self.kdk_obj.retrieve_download()
        if not kdk_download_obj:
            # KDK is already downloaded
            return True

        gui_download.DownloadFrame(
            self,
            title=self.title,
            global_constants=self.constants,
            download_obj=kdk_download_obj,
            item_name=f"KDK Build {self.kdk_obj.kdk_url_build}"
        )
        if kdk_download_obj.download_complete is False:
            return False

        header.SetLabel(f"Validating KDK: {self.kdk_obj.kdk_url_build}")
        header.Center(wx.HORIZONTAL)

        subheader.SetLabel("Checking if checksum is valid...")
        subheader.Center(wx.HORIZONTAL)
        wx.GetApp().Yield()

        progress_bar_animation.stop_pulse()

        if self.kdk_obj.validate_kdk_checksum() is False:
            progress_bar.SetValue(0)
            logging.error("KDK checksum validation failed")
            logging.error(self.kdk_obj.error_msg)
            msg = wx.MessageDialog(frame, f"KDK checksum validation failed: {self.kdk_obj.error_msg}", "Error", wx.OK | wx.ICON_ERROR)
            msg.ShowModal()
            return False

        progress_bar.SetValue(100)

        logging.info("KDK download complete")
        return True


    def _generate_elements_display_patches(self, frame: wx.Frame = None, patches: dict = {}) -> None:
        """
        Generate UI elements for root patching frame

        Format:
            - Title label:        Post-Install Menu
            - Label:              Available patches:
            - Labels:             {patch name}
            - Button:             Start Root Patching
            - Button:             Revert Root Patches
            - Button:             Return to Main Menu
        """
        frame = self if not frame else frame

        title_label = wx.StaticText(frame, label="Post-Install Menu", pos=(-1, 10))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Center(wx.HORIZONTAL)

        # Label: Available patches:
        available_label = wx.StaticText(frame, label="Available patches for your system:", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 10))
        available_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        available_label.Center(wx.HORIZONTAL)

        # Labels: {patch name}
        patches: dict = sys_patch_detect.DetectRootPatch(self.constants.computer.real_model, self.constants).detect_patch_set() if not patches else patches
        can_unpatch: bool = patches["Validation: Unpatching Possible"]

        if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
            logging.info("- No applicable patches available")
            patches = []

        # Check if OCLP has already applied the same patches
        no_new_patches = not self._check_if_new_patches_needed(patches) if patches else False

        if not patches:
            # Prompt user with no patches found
            patch_label = wx.StaticText(frame, label="No patches required", pos=(-1, available_label.GetPosition()[1] + 20))
            patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            patch_label.Center(wx.HORIZONTAL)

        else:
            # Add Label for each patch
            i = 0
            if no_new_patches is True:
                patch_label = wx.StaticText(frame, label="All applicable patches already installed", pos=(-1, available_label.GetPosition()[1] + 20))
                patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                patch_label.Center(wx.HORIZONTAL)
                i = i + 20
            else:
                for patch in patches:
                    if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                        i = i + 20
                        logging.info(f"- Adding patch: {patch} - {patches[patch]}")
                        patch_label = wx.StaticText(frame, label=f"- {patch}", pos=(available_label.GetPosition()[0] + 20, available_label.GetPosition()[1] + i))
                        patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

            if patches["Validation: Patching Possible"] is False:
                # Cannot patch due to the following reasons:
                patch_label = wx.StaticText(frame, label="Cannot patch due to the following reasons:", pos=(-1, patch_label.GetPosition().y + 25))
                patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                patch_label.Center(wx.HORIZONTAL)

                for patch in patches:
                    if not patch.startswith("Validation"):
                        continue
                    if patches[patch] is False:
                        continue
                    if patch == "Validation: Unpatching Possible":
                        continue

                    patch_label = wx.StaticText(frame, label=f"- {patch.split('Validation: ')[1]}", pos=(available_label.GetPosition().x - 10, patch_label.GetPosition().y + 20))
                    patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            else:
                if self.constants.computer.oclp_sys_version and self.constants.computer.oclp_sys_date:
                    date = self.constants.computer.oclp_sys_date.split(" @")
                    date = date[0] if len(date) == 2 else ""

                    patch_text = f"{self.constants.computer.oclp_sys_version}, {date}"

                    patch_label = wx.StaticText(frame, label="Root Volume last patched:", pos=(-1, patch_label.GetPosition().y + 25))
                    patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    patch_label.Center(wx.HORIZONTAL)

                    patch_label = wx.StaticText(frame, label=patch_text, pos=(available_label.GetPosition().x - 10, patch_label.GetPosition().y + 20))
                    patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                    patch_label.Center(wx.HORIZONTAL)


        # Button: Start Root Patching
        start_button = wx.Button(frame, label="Start Root Patching", pos=(10, patch_label.GetPosition().y + 25), size=(170, 30))
        start_button.Bind(wx.EVT_BUTTON, lambda event: self.start_root_patching(frame, patches, no_new_patches))
        start_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        start_button.Center(wx.HORIZONTAL)

        # Button: Revert Root Patches
        revert_button = wx.Button(frame, label="Revert Root Patches", pos=(10, start_button.GetPosition().y + start_button.GetSize().height - 5), size=(170, 30))
        revert_button.Bind(wx.EVT_BUTTON, lambda event: self.revert_root_patching(frame, patches, can_unpatch))
        revert_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        revert_button.Center(wx.HORIZONTAL)

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(10, revert_button.GetPosition().y + revert_button.GetSize().height), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        return_button.Center(wx.HORIZONTAL)
        self.return_button = return_button

        # Disable buttons if unsupported
        if not patches:
            start_button.Disable()
        else:
            if patches["Validation: Patching Possible"] is False:
                start_button.Disable()
        if can_unpatch is False:
            revert_button.Disable()


        # Relaunch as root if not root
        uid = os.geteuid()
        if uid != 0:
            start_button.Bind(wx.EVT_BUTTON, gui_support.RelaunchApplicationAsRoot(frame, self.constants).relaunch)
            revert_button.Bind(wx.EVT_BUTTON, gui_support.RelaunchApplicationAsRoot(frame, self.constants).relaunch)

        # Set frame size
        frame.SetSize((-1, return_button.GetPosition().y + return_button.GetSize().height + 35))


    def _generate_modal(self, patches: dict = {}, variant: str = "Root Patching"):
        """
        Create UI for root patching/unpatching
        """
        supported_variants = ["Root Patching", "Revert Root Patches"]
        if variant not in supported_variants:
            logging.error(f"Unsupported variant: {variant}")
            return

        self.frame_modal.Close()

        dialog = wx.Dialog(self, title=self.title, size=(400, 200))

        # Title
        title = wx.StaticText(dialog, label=variant, pos=(-1, 10))
        title.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title.Center(wx.HORIZONTAL)

        if variant == "Root Patching":
            # Label
            label = wx.StaticText(dialog, label="Root Patching will patch the following:", pos=(-1, title.GetPosition()[1] + 30))
            label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            label.Center(wx.HORIZONTAL)

            # Labels
            i = 0
            for patch in patches:
                if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                    logging.info(f"- Adding patch: {patch} - {patches[patch]}")
                    patch_label = wx.StaticText(dialog, label=f"- {patch}", pos=(label.GetPosition()[0], label.GetPosition()[1] + 20 + i))
                    patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                    i = i + 5
            if i == 0:
                patch_label = wx.StaticText(dialog, label="- No patches to apply", pos=(label.GetPosition()[0], label.GetPosition()[1] + 20))
                patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        else:
            patch_label = wx.StaticText(dialog, label="Reverting to last sealed snapshot", pos=(-1, title.GetPosition()[1] + 30))
            patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            patch_label.Center(wx.HORIZONTAL)


        # Text box
        text_box = wx.TextCtrl(dialog, pos=(10, patch_label.GetPosition()[1] + 20), size=(400, 400), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        text_box.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        text_box.Center(wx.HORIZONTAL)
        self.text_box = text_box

        # Button: Return to Main Menu
        return_button = wx.Button(dialog, label="Return to Main Menu", pos=(10, text_box.GetPosition()[1] + text_box.GetSize()[1] + 5), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        return_button.Center(wx.HORIZONTAL)
        self.return_button = return_button

        # Set frame size
        dialog.SetSize((-1, return_button.GetPosition().y + return_button.GetSize().height + 33))

        dialog.ShowWindowModal()


    def start_root_patching(self, patches: dict):
        logging.info("Starting root patching")

        while gui_support.PayloadMount(self.constants, self).is_unpack_finished() is False:
            wx.Yield()

        if patches["Settings: Kernel Debug Kit missing"] is True:
            if self._kdk_download(self) is False:
                self.on_return_to_main_menu()
                return

        self._generate_modal(patches, "Root Patching")

        thread = threading.Thread(target=self._start_root_patching, args=(patches,))
        thread.start()

        while thread.is_alive():
            wx.GetApp().Yield()

        self._post_patch()
        self.return_button.Enable()


    def _start_root_patching(self, patches: dict):
        logger = logging.getLogger()
        logger.addHandler(gui_support.ThreadHandler(self.text_box))
        try:
            sys_patch.PatchSysVolume(self.constants.computer.real_model, self.constants, patches).start_patch()
        except:
            logging.error("- An internal error occurred while running the Root Patcher:\n")
            logging.error(traceback.format_exc())
        logger.removeHandler(logger.handlers[2])


    def revert_root_patching(self, patches: dict):
        logging.info("Reverting root patches")
        self._generate_modal(patches, "Revert Root Patches")

        thread = threading.Thread(target=self._revert_root_patching, args=(patches,))
        thread.start()

        while thread.is_alive():
            wx.GetApp().Yield()

        self._post_patch()
        self.return_button.Enable()


    def _revert_root_patching(self, patches: dict):
        logger = logging.getLogger()
        logger.addHandler(gui_support.ThreadHandler(self.text_box))
        try:
            sys_patch.PatchSysVolume(self.constants.computer.real_model, self.constants, patches).start_unpatch()
        except:
            logging.error("- An internal error occurred while running the Root Patcher:\n")
            logging.error(traceback.format_exc())
        logger.removeHandler(logger.handlers[2])


    def on_return_to_main_menu(self, event: wx.Event = None):
        self.frame_modal.Hide()
        main_menu_frame = gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        self.frame_modal.Destroy()
        self.Destroy()


    def _post_patch(self):
        if self.constants.root_patcher_succeeded is False:
            return

        if self.constants.needs_to_open_preferences is False:
            gui_support.RestartHost(self).restart(message="Root Patcher finished successfully!\n\nWould you like to reboot now?")
            return

        if self.constants.detected_os >= os_data.os_data.ventura:
            gui_support.RestartHost(self).restart(message="Root Patcher finished successfully!\nIf you were prompted to open System Settings to authorize new kexts, this can be ignored. Your system is ready once restarted.\n\nWould you like to reboot now?")
            return

        # Create dialog box to open System Preferences -> Security and Privacy
        self.popup = wx.MessageDialog(
            self.frame_modal,
            "We just finished installing the patches to your Root Volume!\n\nHowever, Apple requires users to manually approve the kernel extensions installed before they can be used next reboot.\n\nWould you like to open System Preferences?",
            "Open System Preferences?",
            wx.YES_NO | wx.ICON_INFORMATION
        )
        self.popup.SetYesNoLabels("Open System Preferences", "Ignore")
        answer = self.popup.ShowModal()
        if answer == wx.ID_YES:
            output =subprocess.run(
                [
                    "osascript", "-e",
                    'tell app "System Preferences" to activate',
                    "-e", 'tell app "System Preferences" to reveal anchor "General" of pane id "com.apple.preference.security"',
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if output.returncode != 0:
                # Some form of fallback if unaccelerated state errors out
                subprocess.run(["open", "-a", "System Preferences"])
            time.sleep(5)
            sys.exit(0)


    def _check_if_new_patches_needed(self, patches: dict) -> bool:
        """
        Checks if any new patches are needed for the user to install
        Newer users will assume the root patch menu will present missing patches.
        Thus we'll need to see if the exact same OCLP build was used already
        """

        if self.constants.commit_info[0] in ["Running from source", "Built from source"]:
            return True

        if self.constants.computer.oclp_sys_url != self.constants.commit_info[2]:
            # If commits are different, assume patches are as well
            return True

        oclp_plist = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"
        if not Path(oclp_plist).exists():
            # If it doesn't exist, no patches were ever installed
            # ie. all patches applicable
            return True

        oclp_plist_data = plistlib.load(open(oclp_plist, "rb"))
        for patch in patches:
            if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                # Patches should share the same name as the plist key
                # See sys_patch_dict.py for more info
                patch_installed = False
                for key in oclp_plist_data:
                    if "Display Name" not in oclp_plist_data[key]:
                        continue
                    if oclp_plist_data[key]["Display Name"] == patch:
                        patch_installed = True
                        break

                if patch_installed is False:
                    logging.info(f"- Patch {patch} not installed")
                    return True

        logging.info("- No new patches detected for system")
        return False