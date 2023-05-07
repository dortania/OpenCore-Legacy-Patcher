import wx
import time
import sys
import time
import logging
import subprocess

from pathlib import Path

from resources import constants


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