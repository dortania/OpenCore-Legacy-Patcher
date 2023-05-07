
import wx
import logging
import plistlib
from pathlib import Path

from resources import constants
from resources.sys_patch import (
    sys_patch,
    sys_patch_detect
)

from resources.wx_gui import (
    gui_main_menu
)

class SysPatchMenu(wx.Frame):
    """
    Create a frame for building OpenCore
    Uses a Modal Dialog for smoother transition from other frames
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        super(SysPatchMenu, self).__init__(parent, title=title, size=(350, 260))

        self.title = title
        self.constants: constants.Constants = global_constants
        self.frame_modal: wx.Dialog = None

        self.frame_modal = wx.Dialog(self, title=title, size=(360, 200))

        self._generate_elements(self.frame_modal)

        self.SetPosition(screen_location) if screen_location else self.Centre()
        self.frame_modal.ShowWindowModal()



    def _generate_elements(self, frame=None) -> None:
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
        patches: dict = sys_patch_detect.DetectRootPatch(self.constants.computer.real_model, self.constants).detect_patch_set()
        can_unpatch: bool = patches["Validation: Unpatching Possible"]

        if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
            logging.info("- No applicable patches available")
            patches = []

        # Check if OCLP has already applied the same patches
        no_new_patches = not self._check_if_new_patches_needed(patches) if patches else False


        if not patches:
            # Prompt user with no patches found
            patch_label = wx.StaticText(frame, label="No patches needed", pos=(-1, available_label.GetPosition()[1] + 20))
            patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            patch_label.Center(wx.HORIZONTAL)

        else:
            # Add Label for each patch
            i = 0
            if no_new_patches is True:
                patch_label = wx.StaticText(frame, label="No new patches needed", pos=(-1, 50))
                patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                patch_label.Center(wx.HORIZONTAL)
                i = i + 10
            else:
                for patch in patches:
                    if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                        logging.info(f"- Adding patch: {patch} - {patches[patch]}")
                        patch_label = wx.StaticText(frame, label=f"- {patch}", pos=(available_label.GetPosition()[0]
                            , available_label.GetPosition()[1] + 20 + i))
                        patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                        i = i + 5


            if patches["Validation: Patching Possible"] is False:
                # Cannot patch due to the following reasons:
                i = i + 10
                patch_label = wx.StaticText(frame, label="Cannot patch due to the following reasons:", pos=(-1, patch_label.GetPosition().y + i + 10))
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
                    # patch_label.Center(wx.HORIZONTAL)


        # Button: Start Root Patching
        start_button = wx.Button(frame, label="Start Root Patching", pos=(10, patch_label.GetPosition().y + 20), size=(170, 30))
        start_button.Bind(wx.EVT_BUTTON, lambda event: self._start_root_patching(frame, patches, no_new_patches))
        start_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        start_button.Center(wx.HORIZONTAL)

        # Button: Revert Root Patches
        revert_button = wx.Button(frame, label="Revert Root Patches", pos=(10, start_button.GetPosition().y + start_button.GetSize().height - 5), size=(170, 30))
        revert_button.Bind(wx.EVT_BUTTON, lambda event: self._revert_root_patching(frame, patches, can_unpatch))
        revert_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        revert_button.Center(wx.HORIZONTAL)

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(10, revert_button.GetPosition().y + revert_button.GetSize().height), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        return_button.Center(wx.HORIZONTAL)

        if not patches:
            start_button.Disable()
            revert_button.Disable()

        # Set frame size
        frame.SetSize((-1, return_button.GetPosition().y + return_button.GetSize().height + 35))



    def _start_root_patching(self, frame: wx.Frame, patches: dict, no_new_patches: bool):
        pass


    def _revert_root_patching(self, frame: wx.Frame, patches: dict, can_unpatch: bool):
        pass

    def on_return_to_main_menu(self, event):
        self.frame_modal.Hide()
        main_menu_frame = gui_main_menu.MainMenu(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        self.frame_modal.Destroy()
        self.Destroy()




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