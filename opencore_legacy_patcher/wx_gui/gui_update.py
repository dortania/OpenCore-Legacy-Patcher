"""
gui_update.py: Generate UI for updating the patcher
"""

import wx
import sys
import time
import logging
import threading
import subprocess

from pathlib import Path

from .. import constants

from ..wx_gui import (
    gui_download,
    gui_support
)
from ..support import (
    network_handler,
    updates,
    subprocess_wrapper
)


class UpdateFrame(wx.Frame):
    """
    Create a frame for updating the patcher
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: wx.Point, url: str = "", version_label: str = "") -> None:
        logging.info("Initializing Update Frame")
        if parent:
            self.parent: wx.Frame = parent

            for child in self.parent.GetChildren():
                child.Hide()
            parent.Hide()
        else:
            super(UpdateFrame, self).__init__(parent, title=title, size=(350, 300), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
            gui_support.GenerateMenubar(self, global_constants).generate()

        self.title: str = title
        self.constants: constants.Constants = global_constants
        self.pkg_download_path = self.constants.payload_path / "OpenCore-Patcher.pkg"
        self.screen_location: wx.Point = screen_location
        if parent:
            self.parent.Centre()
            self.screen_location = parent.GetScreenPosition()
        else:
            self.Centre()
            self.screen_location = self.GetScreenPosition()


        if url == "" or version_label == "":
            dict = updates.CheckBinaryUpdates(self.constants).check_binary_updates()
            if dict:
                version_label = dict["Version"]
                url = dict["Link"]
            else:
                wx.MessageBox("Failed to get update info", "Critical Error")
                sys.exit(1)

        self.version_label = version_label
        self.url = url

        logging.info(f"Update URL: {url}")
        logging.info(f"Update Version: {version_label}")

        self.frame: wx.Frame = wx.Frame(
            parent=parent if parent else self,
            title=self.title,
            size=(350, 130),
            pos=self.screen_location,
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX
        )

        # Title: Preparing update
        title_label = wx.StaticText(self.frame, label="Preparing download...", pos=(-1,1))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(self.frame, range=100, pos=(10, 50), size=(300, 20))
        progress_bar.Centre(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        self.progress_bar = progress_bar
        self.progress_bar_animation = progress_bar_animation

        self.frame.Centre()
        self.frame.Show()
        wx.Yield()

        download_obj = None
        def _fetch_update() -> None:
            nonlocal download_obj
            file_name = "OpenCore-Patcher.pkg.zip" if url.endswith(".zip") else "OpenCore-Patcher.pkg"
            download_obj = network_handler.DownloadObject(url, self.constants.payload_path / file_name)

        thread = threading.Thread(target=_fetch_update)
        thread.start()
        while thread.is_alive():
            wx.Yield()

        gui_download.DownloadFrame(
            self.frame,
            title=self.title,
            global_constants=self.constants,
            download_obj=download_obj,
            item_name=f"OpenCore Patcher {version_label}",
            download_icon=str(self.constants.app_icon_path)
        )

        if download_obj.download_complete is False:
            progress_bar_animation.stop_pulse()
            progress_bar.SetValue(0)
            wx.MessageBox("Failed to download update. If you continue to have this issue, please manually download OpenCore Legacy Patcher off Github", "Critical Error!", wx.OK | wx.ICON_ERROR)
            sys.exit(1)

        # Title: Extracting update
        title_label.SetLabel("Extracting update...")
        title_label.Centre(wx.HORIZONTAL)
        wx.Yield()

        thread = threading.Thread(target=self._extract_update)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        # Title: Installing update
        title_label.SetLabel("Installing update...")
        title_label.Centre(wx.HORIZONTAL)

        thread = threading.Thread(target=self._install_update)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        # Title: Update complete
        title_label.SetLabel("Update complete!")
        title_label.Centre(wx.HORIZONTAL)

        # Progress bar
        progress_bar.Hide()
        progress_bar_animation.stop_pulse()

        # Label: 0.6.6 has been installed to:
        installed_label = wx.StaticText(self.frame, label=f"{version_label} has been installed:", pos=(-1, progress_bar.GetPosition().y - 15))
        installed_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        installed_label.Centre(wx.HORIZONTAL)

        # Label: '/Library/Application Support/Dortania'
        installed_path_label = wx.StaticText(self.frame, label='/Library/Application Support/Dortania', pos=(-1, installed_label.GetPosition().y + 20))
        installed_path_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        installed_path_label.Centre(wx.HORIZONTAL)

        # Label: Launching update shortly...
        launch_label = wx.StaticText(self.frame, label="Launching update shortly...", pos=(-1, installed_path_label.GetPosition().y + 30))
        launch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        launch_label.Centre(wx.HORIZONTAL)

        # Adjust frame size
        self.frame.SetSize((-1, launch_label.GetPosition().y + 60))

        thread = threading.Thread(target=self._launch_update)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        timer = 5
        while True:
            launch_label.SetLabel(f"Closing old process in {timer} seconds")
            launch_label.Centre(wx.HORIZONTAL)
            wx.Yield()
            time.sleep(1)
            timer -= 1
            if timer == 0:
                break

        sys.exit(0)


    def _extract_update(self) -> None:
        """
        Extracts the update

        Logic:
        - Distributed through GitHub Actions: Requires extraction
        - Distributed through GitHub Releases: No extraction required
        """
        # GitHub Release
        if not self.url.endswith(".zip"):
            return

        logging.info("Extracting nightly update")
        if Path(self.pkg_download_path).exists():
            subprocess.run(["/bin/rm", "-rf", str(self.pkg_download_path)])

        result = subprocess.run(
            ["/usr/bin/ditto", "-xk", str(self.constants.payload_path / "OpenCore-Patcher.pkg.zip"), str(self.constants.payload_path)], capture_output=True
        )
        if result.returncode != 0:
            logging.error(f"Failed to extract update.")
            subprocess_wrapper.log(result)
            wx.CallAfter(self.progress_bar_animation.stop_pulse)
            wx.CallAfter(self.progress_bar.SetValue, 0)
            wx.CallAfter(wx.MessageBox, f"Failed to extract update. Error: {result.stderr.decode('utf-8')}", "Critical Error!", wx.OK | wx.ICON_ERROR)
            wx.CallAfter(sys.exit, 1)


    def _install_update(self) -> None:
        """
        Install PKG
        """
        logging.info(f"Installing update: {self.pkg_download_path}")
        result = subprocess_wrapper.run_as_root(["/usr/sbin/installer", "-pkg", str(self.pkg_download_path), "-target", "/"], capture_output=True)
        if result.returncode != 0:
            wx.CallAfter(self.progress_bar_animation.stop_pulse)
            wx.CallAfter(self.progress_bar.SetValue, 0)
            if "User cancelled" in result.stderr.decode("utf-8"):
                logging.info("User cancelled update")
                wx.CallAfter(wx.MessageBox, "User cancelled update", "Update Cancelled", wx.OK | wx.ICON_INFORMATION)
            else:
                logging.critical("Failed to install update.")
                subprocess_wrapper.log(result)

                # If it fails, fall back to opening the PKG
                logging.error("Failed to install update, attempting to open PKG")
                subprocess.run(["/usr/bin/open", str(self.pkg_download_path)])

                wx.CallAfter(wx.MessageBox, f"Failed to install update. Please try installing the OpenCore-Patcher.pkg manually or download from GitHub", "Critical Error!", wx.OK | wx.ICON_ERROR)
            wx.CallAfter(sys.exit, 1)


    def _launch_update(self) -> None:
        """
        Launches newly installed update
        """
        logging.info("Launching update: '/Library/Application Support/Dortania/OpenCore-Patcher.app'")
        subprocess.Popen(["/Library/Application Support/Dortania/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher", "--update_installed"])
