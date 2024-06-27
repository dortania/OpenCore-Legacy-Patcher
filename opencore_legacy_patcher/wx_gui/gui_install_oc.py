"""
gui_install_oc.py: Frame for installing OpenCore to disk
"""

import wx
import logging
import threading
import traceback

from .. import constants

from ..datasets import os_data
from ..support import install

from ..wx_gui import (
    gui_main_menu,
    gui_support,
    gui_sys_patch_display
)


class InstallOCFrame(wx.Frame):
    """
    Create a frame for installing OpenCore to disk
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        logging.info("Initializing Install OpenCore Frame")
        super(InstallOCFrame, self).__init__(parent, title=title, size=(300, 120), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        gui_support.GenerateMenubar(self, global_constants).generate()

        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.result: bool = False

        self.available_disks: dict = None
        self.stock_output = logging.getLogger().handlers[0].stream

        self.progress_bar_animation: gui_support.GaugePulseCallback = None

        self.hyperlink_colour = (25, 179, 231)

        self._generate_elements()

        if self.constants.update_stage != gui_support.AutoUpdateStages.INACTIVE:
            self.constants.update_stage = gui_support.AutoUpdateStages.INSTALLING

        self.Centre()
        self.Show()

        self._display_disks()


    def _generate_elements(self) -> None:
        """
        Display indeterminate progress bar while collecting disk information

        Format:
            - Title label:        Install OpenCore
            - Text:               Fetching information on local disks...
            - Progress bar:       {indeterminate}
        """

        # Title label: Install OpenCore
        title_label = wx.StaticText(self, label="Install OpenCore", pos=(-1,5))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Text: Parsing local disks...
        text_label = wx.StaticText(self, label="Fetching information on local disks...", pos=(-1,30))
        text_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        text_label.Centre(wx.HORIZONTAL)
        self.text_label = text_label

        # Progress bar: {indeterminate}
        progress_bar = wx.Gauge(self, range=100, pos=(-1, text_label.GetPosition()[1] + text_label.GetSize()[1]), size=(150, 30), style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        progress_bar.Centre(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        self.progress_bar_animation = progress_bar_animation
        self.progress_bar = progress_bar


    def _fetch_disks(self) -> None:
        """
        Fetch information on local disks
        """
        self.available_disks = install.tui_disk_installation(self.constants).list_disks()

        # Need to clean up output on pre-Sierra
        # Disk images are mixed in with regular disks (ex. payloads.dmg)
        ignore = ["disk image", "read-only", "virtual"]
        for disk in self.available_disks.copy():
            if any(string in self.available_disks[disk]['name'].lower() for string in ignore):
                del self.available_disks[disk]


    def _display_disks(self) -> None:
        """
        Display disk selection dialog
        """
        thread = threading.Thread(target=self._fetch_disks)
        thread.start()

        while thread.is_alive():
            wx.Yield()
            continue

        self.progress_bar_animation.stop_pulse()
        self.progress_bar.Hide()

        # Create wxDialog for disk selection
        dialog = wx.Dialog(self, title=self.title, size=(380, -1))

        # Title label: Install OpenCore
        title_label = wx.StaticText(dialog, label="Install OpenCore", pos=(-1,5))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Text: select disk to install OpenCore onto
        text_label = wx.StaticText(dialog, label="Select disk to install OpenCore onto:", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
        text_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        text_label.Centre(wx.HORIZONTAL)

        # Add note: "Missing disks? Ensure they're FAT32 or formatted as GUID/GPT"
        gpt_note = wx.StaticText(dialog, label="Missing disks? Ensure they're FAT32 or formatted as GUID/GPT", pos=(-1, text_label.GetPosition()[1] + text_label.GetSize()[1] + 5))
        gpt_note.SetFont(gui_support.font_factory(10, wx.FONTWEIGHT_NORMAL))
        gpt_note.Centre(wx.HORIZONTAL)

        # Add buttons for each disk
        if self.available_disks:
            # Only show booted disk if building for host
            disk_root = self.constants.booted_oc_disk if self.constants.custom_model is None else None
            if disk_root:
                # disk6s1 -> disk6
                disk_root = self.constants.booted_oc_disk.strip("disk")
                disk_root = "disk" + disk_root.split("s")[0]
                logging.info(f"Checking if booted disk is present: {disk_root}")

            # Add buttons for each disk
            items = len(self.available_disks)
            longest_label = max((len(self.available_disks[disk]['disk']) + len(self.available_disks[disk]['name']) + len(str(self.available_disks[disk]['size']))) for disk in self.available_disks)
            longest_label = longest_label * 9
            spacer = 0
            logging.info("Available disks:")
            for disk in self.available_disks:
                # Create a button for each disk
                logging.info(f"- {self.available_disks[disk]['disk']} - {self.available_disks[disk]['name']} - {self.available_disks[disk]['size']}")
                disk_button = wx.Button(dialog, label=f"{self.available_disks[disk]['disk']} - {self.available_disks[disk]['name']} - {self.available_disks[disk]['size']}", size=(longest_label ,30), pos=(-1, gpt_note.GetPosition()[1] + gpt_note.GetSize()[1] + 5 + spacer))
                disk_button.Centre(wx.HORIZONTAL)
                disk_button.Bind(wx.EVT_BUTTON, lambda event, disk=disk: self._display_volumes(disk, self.available_disks))
                if disk_root == self.available_disks[disk]['disk'] or items == 1:
                    disk_button.SetDefault()
                spacer += 25

            if disk_root:
                # Add note: "Note: Blue represent the disk OpenCore is currently booted from"
                disk_label = wx.StaticText(dialog, label="Note: Blue represent the disk OpenCore is currently booted from", pos=(-1, disk_button.GetPosition()[1] + disk_button.GetSize()[1] + 5))
                disk_label.SetFont(gui_support.font_factory(10, wx.FONTWEIGHT_NORMAL))
                disk_label.Centre(wx.HORIZONTAL)
            else:
                disk_label = wx.StaticText(dialog, label="", pos=(-1, disk_button.GetPosition()[1] + 15))
                disk_label.SetFont(gui_support.font_factory(10, wx.FONTWEIGHT_NORMAL))
        else:
            # Text: Failed to find any applicable disks
            disk_label = wx.StaticText(dialog, label="Failed to find any applicable disks", pos=(-1, gpt_note.GetPosition()[1] + gpt_note.GetSize()[1] + 5))
            disk_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
            disk_label.Centre(wx.HORIZONTAL)

        # Add button: Search for disks again
        search_button = wx.Button(dialog, label="Search for disks again", size=(150,30), pos=(-1, disk_label.GetPosition()[1] + disk_label.GetSize()[1] + 5))
        search_button.Centre(wx.HORIZONTAL)
        search_button.Bind(wx.EVT_BUTTON, self.on_reload_frame)

        # Add button: Return to main menu
        return_button = wx.Button(dialog, label="Return to Main Menu", size=(150,30), pos=(-1, search_button.GetPosition()[1] + 20))
        return_button.Centre(wx.HORIZONTAL)
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)

        # Set size
        dialog.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))
        dialog.ShowWindowModal()
        self.dialog = dialog


    def _display_volumes(self, disk: str, dataset: dict) -> None:
        """
        List volumes on disk
        """

        self.dialog.Close()

        # Create dialog
        dialog = wx.Dialog(
            self,
            title=f"Volumes on {disk}",
            style=wx.CAPTION | wx.CLOSE_BOX,
            size=(300, 300)
        )

        # Add text: "Volumes on {disk}"
        text_label = wx.StaticText(dialog, label=f"Volumes on {disk}", pos=(-1, 10))
        text_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        text_label.Centre(wx.HORIZONTAL)

        partitions = install.tui_disk_installation(self.constants).list_partitions(disk, dataset)
        items = len(partitions)
        longest_label = max((len(partitions[partition]['partition']) + len(partitions[partition]['name']) + len(str(partitions[partition]['size']))) for partition in partitions)
        longest_label = longest_label * 10
        spacer = 0
        logging.info(f"Available partitions for {disk}:")
        for partition in partitions:
            logging.info(f"- {partitions[partition]['partition']} - {partitions[partition]['name']} - {partitions[partition]['size']}")
            disk_button = wx.Button(dialog, label=f"{partitions[partition]['partition']} - {partitions[partition]['name']} - {partitions[partition]['size']}", size=(longest_label,30), pos=(-1, text_label.GetPosition()[1] + text_label.GetSize()[1] + 5 + spacer))
            disk_button.Centre(wx.HORIZONTAL)
            disk_button.Bind(wx.EVT_BUTTON, lambda event, partition=partition: self._install_oc_process(partition))
            if items == 1 or self.constants.booted_oc_disk == partitions[partition]['partition']:
                disk_button.SetDefault()
            spacer += 25

        # Add button: Return to main menu
        return_button = wx.Button(dialog, label="Return to Main Menu", size=(150,30), pos=(-1, disk_button.GetPosition()[1] + disk_button.GetSize()[1]))
        return_button.Centre(wx.HORIZONTAL)
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)

        # Set size
        dialog.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))

        # Show dialog
        dialog.ShowWindowModal()
        self.dialog = dialog


    def _install_oc_process(self, partition: dict) -> None:
        """
        Install OpenCore to disk
        """
        self.dialog.Close()

        # Create dialog
        dialog = wx.Dialog(
            self,
            title=f"Installing OpenCore to {partition}",
            style=wx.CAPTION | wx.CLOSE_BOX,
            size=(370, 200)
        )

        # Add text: "Installing OpenCore to {partition}"
        text_label = wx.StaticText(dialog, label=f"Installing OpenCore to {partition}", pos=(-1, 10))
        text_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        text_label.Centre(wx.HORIZONTAL)

        # Read-only text box: {empty}
        text_box = wx.TextCtrl(dialog, value="", pos=(-1, text_label.GetPosition()[1] + text_label.GetSize()[1] + 10), size=(350, 200), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        text_box.Centre(wx.HORIZONTAL)
        self.text_box = text_box

        # Add button: Return to main menu
        return_button = wx.Button(dialog, label="Return to Main Menu", size=(150,30), pos=(-1, text_box.GetPosition()[1] + text_box.GetSize()[1] + 10))
        return_button.Centre(wx.HORIZONTAL)
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.Disable()

        # Set size
        dialog.SetSize((370, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))

        # Show dialog
        dialog.ShowWindowModal()
        self.dialog = dialog

        # Install OpenCore
        self._invoke_install_oc(partition)
        return_button.Enable()


    def _invoke_install_oc(self, partition: dict) -> None:
        """
        Invoke OpenCore installation
        """
        thread = threading.Thread(target=self._install_oc, args=(partition,))
        thread.start()

        while thread.is_alive():
            wx.Yield()

        if self.result is True:
            if self.constants.update_stage != gui_support.AutoUpdateStages.INACTIVE and self.constants.detected_os >= os_data.os_data.big_sur:
                self.constants.update_stage = gui_support.AutoUpdateStages.ROOT_PATCHING
                popup_message = wx.MessageDialog(
                    self,
                    f"OpenCore has finished installing to disk.\n\nWould you like to update your root patches next?", "Success",
                    wx.YES_NO | wx.YES_DEFAULT
                )
                popup_message.ShowModal()
                if popup_message.GetReturnCode() == wx.ID_YES:
                    self.Hide()
                    gui_sys_patch_display.SysPatchDisplayFrame(
                        parent=None,
                        title=self.title,
                        global_constants=self.constants,
                        screen_location=self.GetPosition()
                    )
                    self.Destroy()
                return

            elif not self.constants.custom_model:
                gui_support.RestartHost(self).restart(message="OpenCore has finished installing to disk.\n\nYou will need to reboot and hold the Option key and select OpenCore/Boot EFI's option.\n\nWould you like to reboot?")
            else:
                popup_message = wx.MessageDialog(
                    self,
                    f"OpenCore has finished installing to disk.\n\nYou can eject the drive, insert it into the {self.constants.custom_model}, reboot, hold the Option key and select OpenCore/Boot EFI's option.", "Success",
                    wx.OK
                )
                popup_message.ShowModal()
        else:
            if self.constants.update_stage != gui_support.AutoUpdateStages.INACTIVE:
                self.constants.update_stage = gui_support.AutoUpdateStages.FINISHED


    def _install_oc(self, partition: dict) -> None:
        """
        Install OpenCore to disk
        """
        logging.info(f"Installing OpenCore to {partition}")

        logger = logging.getLogger()
        logger.addHandler(gui_support.ThreadHandler(self.text_box))
        try:
            self.result = install.tui_disk_installation(self.constants).install_opencore(partition)
        except:
            logging.error("An internal error occurred while installing:\n")
            logging.error(traceback.format_exc())
        logger.removeHandler(logger.handlers[2])


    def on_reload_frame(self, event: wx.Event = None) -> None:
        """
        Reload frame
        """
        self.Destroy()
        frame = InstallOCFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        frame.Show()


    def on_return_to_main_menu(self, event: wx.Event = None) -> None:
        """
        Return to main menu
        """
        main_menu_frame = gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        self.Destroy()




