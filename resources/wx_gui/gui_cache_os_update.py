"""
UI to display to users before a macOS update is applied
Primarily for caching updates required for incoming OS (ex. KDKs)
"""

import wx
import sys
import time
import logging
import threading

from pathlib import Path

from resources import constants, kdk_handler, utilities
from resources.wx_gui import gui_support, gui_download


class OSUpdateFrame(wx.Frame):
    """
    Create a modal frame for displaying information to the user before an update is applied
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        logging.info("Initializing Prepare Update Frame")

        if parent:
            self.frame = parent
        else:
            super().__init__(parent, title=title, size=(360, 140), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
            self.frame = self
            self.frame.Centre()

        self.title = title
        self.constants: constants.Constants = global_constants

        os_data = utilities.fetch_staged_update(variant="Preflight")
        if os_data[0] is None:
            logging.info("No staged update found")
            self._exit()
        logging.info(f"Staged update found: {os_data[0]} ({os_data[1]})")
        self.os_data = os_data

        self._generate_ui()

        self.kdk_obj: kdk_handler.KernelDebugKitObject = None
        def _kdk_thread_spawn():
            self.kdk_obj = kdk_handler.KernelDebugKitObject(self.constants, self.os_data[1], self.os_data[0], passive=True, check_backups_only=True)

        kdk_thread = threading.Thread(target=_kdk_thread_spawn)
        kdk_thread.start()

        while kdk_thread.is_alive():
            wx.Yield()

        if self.kdk_obj.success is False:
            self._exit()

        kdk_download_obj = self.kdk_obj.retrieve_download()
        if not kdk_download_obj:
            # KDK is already downloaded
            # Return false since we didn't display anything
            self._exit()

        self.kdk_download_obj = kdk_download_obj

        self.frame.Show()

        self.did_cancel = -1
        self._notifyUser()

        # Allow 10 seconds for the user to cancel the download
        # If nothing, continue
        for i in range(0, 10):
            if self.did_cancel == 1:
                self._exit()
            if self.did_cancel == -1:
                time.sleep(1)

        gui_download.DownloadFrame(
            self,
            title=self.title,
            global_constants=self.constants,
            download_obj=kdk_download_obj,
            item_name=f"KDK Build {self.kdk_obj.kdk_url_build}"
        )
        if kdk_download_obj.download_complete is False:
            self._exit()

        logging.info("KDK download complete, validating with hdiutil")
        self.kdk_checksum_result = False
        def _validate_kdk_checksum_thread():
            self.kdk_checksum_result = self.kdk_obj.validate_kdk_checksum()

        kdk_checksum_thread = threading.Thread(target=_validate_kdk_checksum_thread)
        kdk_checksum_thread.start()

        while kdk_checksum_thread.is_alive():
            wx.Yield()

        if self.kdk_checksum_result is False:
            logging.error("KDK checksum validation failed")
            logging.error(self.kdk_obj.error_msg)
            self._exit()

        logging.info("KDK checksum validation passed")

        logging.info("Mounting KDK")
        if not Path(self.constants.kdk_download_path).exists():
            logging.error("KDK download path does not exist")
            self._exit()

        self.kdk_install_result = False
        def _install_kdk_thread():
            self.kdk_install_result = kdk_handler.KernelDebugKitUtilities().install_kdk_dmg(self.constants.kdk_download_path, only_install_backup=True)

        kdk_install_thread = threading.Thread(target=_install_kdk_thread)
        kdk_install_thread.start()

        while kdk_install_thread.is_alive():
            wx.Yield()

        if self.kdk_install_result is False:
            logging.info("Failed to install KDK")
            self._exit()

        logging.info("KDK installed successfully")
        self._exit()


    def _generate_ui(self) -> None:
        """
        Display frame


        Title: OpenCore Legacy Patcher is preparing to update your system
        Body:  Please wait while we prepare your system for the update.
               This may take a few minutes.
        """

        header = wx.StaticText(self.frame, label="Preparing for macOS Software Update", pos=(-1,5))
        header.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        header.Centre(wx.HORIZONTAL)

        # list OS
        label = wx.StaticText(self.frame, label=f"macOS {self.os_data[0]} ({self.os_data[1]})", pos=(-1, 35))
        label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        label.Centre(wx.HORIZONTAL)

        # this may take a few minutes
        label = wx.StaticText(self.frame, label="This may take a few minutes.", pos=(-1, 55))
        label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        label.Centre(wx.HORIZONTAL)

        # Add a progress bar
        self.progress_bar = wx.Gauge(self.frame, range=100, pos=(10, 75), size=(340, 20))
        self.progress_bar.SetValue(0)
        self.progress_bar.Pulse()

        # Set frame size below progress bar
        self.frame.SetSize((360, 140))


    def _notifyUser(self) -> None:
        """
        Notify user of what OCLP is doing
        Note will be spawned through wx.CallAfter
        """
        threading.Thread(target=self._notifyUserThread).start()


    def _notifyUserThread(self) -> None:
        """
        Notify user of what OCLP is doing
        """
        message=f"OpenCore Legacy Patcher has detected that a macOS update is being downloaded:\n{self.os_data[0]} ({self.os_data[1]})\n\nThe patcher needs to prepare the system for the update, and will download any additional resources it may need post-update.\n\nThis may take a few minutes, the patcher will exit when it is done."
        # Yes/No for caching
        dlg = wx.MessageDialog(self.frame, message=message, caption="OpenCore Legacy Patcher", style=wx.YES_NO | wx.ICON_INFORMATION)
        dlg.SetYesNoLabels("&Ok", "&Cancel")
        result = dlg.ShowModal()
        if result == wx.ID_NO:
            logging.info("User cancelled OS caching")
            self.kdk_download_obj.stop()
            self.did_cancel = 1
        else:
            self.did_cancel = 0

    def _exit(self):
        """
        Exit the frame
        """
        self.frame.Close()
        sys.exit()
