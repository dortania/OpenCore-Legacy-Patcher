"""
gui_support.py: Utilities for interacting with wxPython GUI
"""

import wx
import sys
import time
import logging
import plistlib
import threading
import subprocess
import applescript
import packaging.version

from pathlib import Path

from . import gui_about

from .. import constants

from ..detections import device_probe

from ..datasets import (
    model_array,
    os_data,
    smbios_data
)


def get_font_face():
    if not get_font_face.font_face:
        get_font_face.font_face = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetFaceName() or "Lucida Grande"

    return get_font_face.font_face


get_font_face.font_face = None


# Centralize the common options for font creation
def font_factory(size: int, weight):
    return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight, False, get_font_face())


class AutoUpdateStages:
    INACTIVE = 0
    CHECKING = 1
    BUILDING = 2
    INSTALLING = 3
    ROOT_PATCHING = 4
    FINISHED = 5


class GenerateMenubar:

    def __init__(self, frame: wx.Frame, global_constants: constants.Constants) -> None:
        self.frame: wx.Frame = frame
        self.constants: constants.Constants = global_constants


    def generate(self) -> wx.MenuBar:
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

        aboutItem = fileMenu.Append(wx.ID_ABOUT, "&About OpenCore Legacy Patcher")
        fileMenu.AppendSeparator()
        revealLogItem = fileMenu.Append(wx.ID_ANY, "&Reveal Log File")

        menubar.Append(fileMenu, "&File")
        self.frame.SetMenuBar(menubar)

        self.frame.Bind(wx.EVT_MENU, lambda event: gui_about.AboutFrame(self.constants), aboutItem)
        self.frame.Bind(wx.EVT_MENU, lambda event: subprocess.run(["/usr/bin/open", "--reveal", self.constants.log_filepath]), revealLogItem)


class GaugePulseCallback:
    """
    Uses an alternative Pulse() method for wx.Gauge() on macOS Monterey+ with non-Metal GPUs
    Dirty hack, however better to display some form of animation than none at all

    Note: This work-around is no longer needed on hosts using PatcherSupportPkg 1.1.2 or newer
    """

    def __init__(self, global_constants: constants.Constants, gauge: wx.Gauge) -> None:
        self.gauge: wx.Gauge = gauge

        self.pulse_thread: threading.Thread = None
        self.pulse_thread_active: bool = False

        self.gauge_value: int = 0
        self.pulse_forward: bool = True

        self.max_value: int = gauge.GetRange()

        self.non_metal_alternative: bool = CheckProperties(global_constants).host_is_non_metal()
        if self.non_metal_alternative is True:
            if CheckProperties(global_constants).host_psp_version() >= packaging.version.Version("1.1.2"):
                self.non_metal_alternative = False


    def start_pulse(self) -> None:
        if self.non_metal_alternative is False:
            self.gauge.Pulse()
            return
        self.pulse_thread_active = True
        self.pulse_thread = threading.Thread(target=self._pulse)
        self.pulse_thread.start()


    def stop_pulse(self) -> None:
        if self.non_metal_alternative is False:
            return
        self.pulse_thread_active = False
        self.pulse_thread.join()


    def _pulse(self) -> None:
        while self.pulse_thread_active:
            if self.gauge_value == 0:
                self.pulse_forward = True

            elif self.gauge_value == self.max_value:
                self.pulse_forward = False

            if self.pulse_forward:
                self.gauge_value += 1
            else:
                self.gauge_value -= 1

            wx.CallAfter(self.gauge.SetValue, self.gauge_value)
            time.sleep(0.005)


class CheckProperties:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants


    def host_can_build(self):
        """
        Check if host supports building OpenCore configs
        """
        if self.constants.custom_model:
            return True
        if self.constants.host_is_hackintosh is True:
            return False
        if self.constants.allow_oc_everywhere is True:
            return True
        if self.constants.computer.real_model in model_array.SupportedSMBIOS:
            return True

        return False


    def host_is_non_metal(self, general_check: bool = False):
        """
        Check if host is non-metal
        Primarily for wx.Gauge().Pulse() workaround (where animation doesn't work on Monterey+)
        """

        if self.constants.detected_os < os_data.os_data.monterey and general_check is False:
            return False
        if self.constants.detected_os < os_data.os_data.big_sur and general_check is True:
            return False
        if not Path("/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLightOld.dylib").exists():
            # SkyLight stubs are only used on non-Metal
            return False

        return True


    def host_has_cpu_gen(self, gen: int) -> bool:
        """
        Check if host has a CPU generation equal to or greater than the specified generation
        """
        model = self.constants.custom_model if self.constants.custom_model else self.constants.computer.real_model
        if model in smbios_data.smbios_dictionary:
            if smbios_data.smbios_dictionary[model]["CPU Generation"] >= gen:
                return True
        return False


    def host_psp_version(self) -> packaging.version.Version:
        """
        Grab PatcherSupportPkg version from OpenCore-Legacy-Patcher.plist
        """
        oclp_plist_path = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"
        if not Path(oclp_plist_path).exists():
            return packaging.version.Version("0.0.0")

        oclp_plist = plistlib.load(open(oclp_plist_path, "rb"))
        if "PatcherSupportPkg" not in oclp_plist:
            return packaging.version.Version("0.0.0")

        if oclp_plist["PatcherSupportPkg"].startswith("v"):
            oclp_plist["PatcherSupportPkg"] = oclp_plist["PatcherSupportPkg"][1:]

        return packaging.version.parse(oclp_plist["PatcherSupportPkg"])

    def host_has_3802_gpu(self) -> bool:
        """
        Check if either host, or override model, has a 3802 GPU
        """

        gpu_archs = []
        if self.constants.custom_model:
            model = self.constants.custom_model
        else:
            model = self.constants.computer.real_model
            gpu_archs = [gpu.arch for gpu in self.constants.computer.gpus]

        if not gpu_archs:
            gpu_archs = smbios_data.smbios_dictionary.get(model, {}).get("Stock GPUs", [])

        for arch in gpu_archs:
            if arch in [
                device_probe.Intel.Archs.Ivy_Bridge,
                device_probe.Intel.Archs.Haswell,
                device_probe.NVIDIA.Archs.Kepler,
            ]:
                return True

        return False

class PayloadMount:

    def __init__(self, global_constants: constants.Constants, frame: wx.Frame) -> None:
        self.constants: constants.Constants = global_constants
        self.frame: wx.Frame = frame


    def is_unpack_finished(self):
        if self.constants.unpack_thread.is_alive():
            return False

        if Path(self.constants.payload_kexts_path).exists():
            return True

        # Raise error to end program
        popup = wx.MessageDialog(
            self.frame,
            f"During unpacking of our internal files, we seemed to have encountered an error.\n\nIf you keep seeing this error, please try rebooting and redownloading the application.",
            "Internal Error occurred!",
            style=wx.OK | wx.ICON_EXCLAMATION
        )
        popup.ShowModal()
        self.frame.Freeze()
        sys.exit(1)


class ThreadHandler(logging.Handler):
    """
    Reroutes logging output to a wx.TextCtrl using UI callbacks
    """

    def __init__(self, text_box: wx.TextCtrl):
        logging.Handler.__init__(self)
        self.text_box = text_box


    def emit(self, record: logging.LogRecord):
        wx.CallAfter(self.text_box.AppendText, self.format(record) + '\n')


class RestartHost:
    """
    Restarts the host machine
    """

    def __init__(self, frame: wx.Frame) -> None:
        self.frame: wx.Frame = frame


    def restart(self, event: wx.Event = None, message: str = ""):
        self.popup = wx.MessageDialog(
            self.frame,
            message,
            "Reboot to apply?",
            wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
        )
        self.popup.SetYesNoLabels("Reboot", "Ignore")
        answer = self.popup.ShowModal()
        if answer == wx.ID_YES:
            # Reboots with Count Down prompt (user can still dismiss if needed)
            self.frame.Hide()
            wx.Yield()
            try:
                applescript.AppleScript('tell app "loginwindow" to «event aevtrrst»').run()
            except applescript.ScriptError as e:
                logging.error(f"Error while trying to reboot: {e}")
            sys.exit(0)