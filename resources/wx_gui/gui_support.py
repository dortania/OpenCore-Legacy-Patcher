import wx
import time
import sys
import time
import logging
import subprocess
import threading

from pathlib import Path

from resources import constants
from data import model_array, os_data


class GenerateMenubar:

    def __init__(self) -> None:
        self.menubar: wx.MenuBar = None


    def generate(self) -> wx.MenuBar:
        self.menubar = wx.MenuBar()
        return self.menubar



class GaugePulseCallback:
    """
    Uses an alternative Pulse() method for wx.Gauge() on macOS Monterey+
    Dirty hack, however better to display some form of animation than none at all
    """

    def __init__(self, global_constants: constants.Constants, gauge: wx.Gauge) -> None:
        self.gauge: wx.Gauge = gauge

        self.pulse_thread: threading.Thread = None
        self.pulse_thread_active: bool = False

        self.gauge_value: int = 0
        self.pulse_forward: bool = True

        self.non_metal_alternative: bool = CheckProperties(global_constants).host_is_non_metal()


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

            elif self.gauge_value == 100:
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
        if self.constants.host_is_hackintosh is True:
            return False
        if self.constants.allow_oc_everywhere is True:
            return True
        if self.constants.custom_model:
            return True
        if self.constants.computer.real_model in model_array.SupportedSMBIOS:
            return True

        return False


    def host_is_non_metal(self):
        """
        Check if host is non-metal
        Primarily for wx.Gauge().Pulse() workaround (where animation doesn't work on Monterey+)
        """

        if self.constants.detected_os < os_data.os_data.monterey:
            return False
        if not Path("/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLightOld.dylib").exists():
            # SkyLight stubs are only used on non-Metal
            return False

        return True



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
            style = wx.OK | wx.ICON_EXCLAMATION
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
            wx.YES_NO | wx.ICON_INFORMATION
        )
        self.popup.SetYesNoLabels("Reboot", "Ignore")
        answer = self.popup.ShowModal()
        if answer == wx.ID_YES:
            # Reboots with Count Down prompt (user can still dismiss if needed)
            self.frame.Hide()
            wx.GetApp().Yield()
            subprocess.call(['osascript', '-e', 'tell app "loginwindow" to «event aevtrrst»'])
            sys.exit(0)


class RelaunchApplicationAsRoot:
    """
    Relaunches the application as root
    """

    def __init__(self, frame: wx.Frame, global_constants: constants.Constants) -> None:
        self.constants = global_constants
        self.frame: wx.Frame = frame

    def relaunch(self, event: wx.Event):

        self.dialog = wx.MessageDialog(
            self.frame,
            "OpenCore Legacy Patcher needs to relaunch as admin to continue. You will be prompted to enter your password.",
            "Relaunch as root?",
            wx.YES_NO | wx.ICON_QUESTION
        )

        # Show Dialog Box
        if self.dialog.ShowModal() != wx.ID_YES:
            logging.info("User cancelled relaunch")
            return

        timer: int = 5
        program_arguments: str = ""

        if event:
            if event.GetEventObject() != wx.Menu:
                try:
                    if event.GetEventObject().GetLabel() in ["Start Root Patching", "Reinstall Root Patches"]:
                        program_arguments = " --gui_patch"
                    elif event.GetEventObject().GetLabel() == "Revert Root Patches":
                        program_arguments = " --gui_unpatch"
                except TypeError:
                    pass

        if self.constants.launcher_script is None:
            program_arguments = f"'{self.constants.launcher_binary}'{program_arguments}"
        else:
            program_arguments = f"{self.constants.launcher_binary} {self.constants.launcher_script}{program_arguments}"

        # Relaunch as root
        args = [
            "osascript",
            "-e",
            f'''do shell script "{program_arguments}"'''
            ' with prompt "OpenCore Legacy Patcher needs administrator privileges to relaunch as admin."'
            " with administrator privileges"
            " without altering line endings",
        ]

        self.frame.DestroyChildren()
        self.frame.SetSize(400, 300)

        # Header
        header = wx.StaticText(self.frame, label="Relaunching as root")
        header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        header.Centre(wx.HORIZONTAL)

        # Add count down label
        countdown_label = wx.StaticText(self.frame, label=f"Closing old process in {timer} seconds", pos=(0, header.GetPosition().y + header.GetSize().height + 3))
        countdown_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        countdown_label.Center(wx.HORIZONTAL)

        # Set size of frame
        self.frame.SetSize((-1, countdown_label.GetPosition().y + countdown_label.GetSize().height + 40))

        wx.GetApp().Yield()

        logging.info(f"- Relaunching as root with command: {program_arguments}")
        subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            wx.GetApp().Yield()
            countdown_label.SetLabel(f"Closing old process in {timer} seconds")
            time.sleep(1)
            timer -= 1
            if timer == 0:
                break

        sys.exit(0)