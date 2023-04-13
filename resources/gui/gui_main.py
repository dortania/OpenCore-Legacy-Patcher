# Setup GUI
# Implemented using wxPython
# Currently Work in Progress

import plistlib
from pathlib import Path
from datetime import datetime

import os
import sys
import subprocess
import threading

import webbrowser

import time

import logging
import tempfile

import wx
import wx.adv
from wx.lib.agw import hyperlink

import py_sip_xnu

from resources import (
    constants,
    defaults,
    install,
    utilities,
    generate_smbios,
    updates,
    integrity_verification,
    global_settings,
    kdk_handler,
    network_handler,
    macos_installer_handler
)

from resources.sys_patch import sys_patch_detect, sys_patch
from resources.build import build
from resources.gui import menu_redirect, gui_help

from data import model_array, os_data, smbios_data, sip_data, cpu_data



class wx_python_gui:
    def __init__(self, versions, frame=None, frame_modal=None):
        self.constants: constants.Constants = versions
        self.computer = self.constants.computer
        self.constants.gui_mode = True
        self.walkthrough_mode = False
        self.finished_auto_patch = False
        self.finished_cim_process = False
        self.target_disk = ""
        self.pulse_forward = False
        self.prepare_result = False
        self.non_metal_required = self.use_non_metal_alternative()
        self.hyperlink_colour = (25, 179, 231)

        # Backup stdout for usage with wxPython
        self.stock_stream = logging.getLogger().handlers[0].stream

        current_uid = os.getuid()

        # Define Window Size
        self.WINDOW_WIDTH_MAIN = 350
        self.WINDOW_HEIGHT_MAIN = 220
        self.WINDOW_WIDTH_BUILD = 400
        self.WINDOW_HEIGHT_BUILD = 500
        self.WINDOW_SETTINGS_WIDTH = 250
        self.WINDOW_SETTINGS_HEIGHT = 320

        # Create Application
        self.app = wx.App()
        if frame is None:
            self.frame = wx.Frame(
                None, title=f"OpenCore Legacy Patcher ({self.constants.patcher_version})",
                size=(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN),
                style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
            )
            self.frame.Centre(~wx.MAXIMIZE_BOX)
            self.frame.Show()
            self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
            # Create Menubar (allows Cmd+Q usage)
            self.menubar = wx.MenuBar()
            self.file_menu = wx.Menu()
            self.file_menu.Append(wx.ID_EXIT, "Quit", "Quit Application" )
            self.file_menu.Append(wx.ID_REDO, f"Relaunch as Root (UID: {int(current_uid)})", "Relaunch OpenCore Legacy Patcher as Root")
            self.menubar.Append(self.file_menu, "File")
            self.frame.Bind(wx.EVT_MENU, self.OnCloseFrame, id=wx.ID_EXIT)
            self.frame.Bind(wx.EVT_MENU, self.relaunch_as_root, id=wx.ID_REDO)
            self.frame.SetMenuBar(self.menubar)
        else:
            self.frame = frame

        # Modal Frames
        self.frame_modal = frame_modal

        if current_uid == 0:
            self.file_menu.Enable(wx.ID_REDO, False)


    def OnCloseFrame(self, event=None):
        self.frame.SetTransparent(0)
        wx.GetApp().Yield()
        self.frame.DestroyChildren()
        self.frame.Destroy()
        self.app.ExitMainLoop()
        sys.exit()

    def reboot_system(self, event=None, message=""):
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
            subprocess.call(['osascript', '-e', 'tell app "loginwindow" to «event aevtrrst»'])
            self.OnCloseFrame(event)

    def reset_window(self):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)
        logging.getLogger().handlers[0].stream = self.stock_stream
        self.reset_frame_modal()

        # Re-enable sleep if we failed to do so before returning to the main menu
        utilities.enable_sleep_after_running()

    def reset_frame_modal(self):
        if not self.frame_modal:
            self.frame_modal = wx.Dialog(self.frame)
        else:
            self.frame_modal.DestroyChildren()
            self.frame_modal.Close()

            # This is a hack to fix window sizing issues
            # If the previous frame was a modal, the new frame will anchor onto it
            # instead of the core frame
            # Calling ShowWithoutActivating() resets the frame position
            if self.constants.detected_os >= os_data.os_data.big_sur:
                self.frame_modal.ShowWithoutActivating()

    def use_non_metal_alternative(self):
        if self.constants.detected_os >= os_data.os_data.monterey:
            if Path("/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLightOld.dylib").exists():
                if self.constants.host_is_non_metal is True:
                    return True
        return False

    def is_unpack_finished(self):
        if not self.constants.unpack_thread.is_alive():
            if Path(self.constants.payload_kexts_path).exists():
                return True
            else:
                # Raise error to end program
                self.popup = wx.MessageDialog(
                    self.frame,
                    f"During unpacking of our internal files, we seemed to have encountered an error.\n\nIf you keep seeing this error, please try rebooting and redownloading the application.",
                    "Internal Error occurred!",
                    style = wx.OK | wx.ICON_EXCLAMATION
                )
                self.popup.ShowModal()
                self.frame.Freeze()
                self.OnCloseFrame(None)
        return False

    def pulse_alternative(self, progress_bar):
        if self.non_metal_required is True:
            if progress_bar.GetValue() == 0:
                self.pulse_forward = True

            elif progress_bar.GetValue() == 100:
                self.pulse_forward = False

            if self.pulse_forward:
                progress_bar.SetValue(progress_bar.GetValue() + 1)
            else:
                progress_bar.SetValue(progress_bar.GetValue() - 1)
            time.sleep(0.005)

    def preflight_check(self):
        if (
                self.constants.computer.build_model != None and
                self.constants.computer.build_model != self.constants.computer.real_model and
                self.constants.host_is_hackintosh is False
            ):
            # Notify user they're booting an unsupported configuration
            self.constants.start_build_install = True
            self.popup = wx.MessageDialog(
            self.frame,
                f"We found you are currently booting OpenCore built for a different unit: {self.constants.computer.build_model}\n\nWe builds configs to match individual units and cannot be mixed or reused with different Macs.\n\nPlease Build and Install a new OpenCore config, and reboot your Mac.",
                "Unsupported Configuration Detected!",
                style = wx.OK | wx.ICON_EXCLAMATION
            )
            self.popup.ShowModal()
        else:
            # Spawn thread to check for updates
            threading.Thread(target=self.check_for_updates).start()

    def check_for_local_installs(self, event=None):
        # Update app in '/Library/Application Support/Dortania' folder

        # Skip if we're running from source
        if self.constants.launcher_script:
            return False

        # Only performed if application is already installed (ie. we're updating)
        application_path = Path("/Library/Application Support/Dortania/OpenCore-Patcher.app")
        if not application_path.exists():
            return False

        # Check application version
        # If we're older than the installed version, skip
        application_plist_path = application_path / "Contents/Info.plist"
        if not application_plist_path.exists():
            return False

        application_plist = plistlib.load(application_plist_path.open("rb"))
        if not "CFBundleShortVersionString" in application_plist:
            return False

        application_version = application_plist["CFBundleShortVersionString"].split(".")
        local_version = self.constants.patcher_version.split(".")

        if application_version == local_version:
            if "Build Date" not in application_plist:
                return False

            # Check build date of installed version
            plist_path = self.constants.launcher_binary.replace("MacOS/OpenCore-Patcher", "Info.plist")
            if not Path(plist_path).exists():
                return False

            plist = plistlib.load(Path(plist_path).open("rb"))
            if "Build Date" not in plist:
                return False

            if plist["Build Date"] == application_plist["Build Date"]:
                return False

            local_build_date = datetime.strptime(plist["Build Date"], "%Y-%m-%d %H:%M:%S")
            installed_build_date = datetime.strptime(application_plist["Build Date"], "%Y-%m-%d %H:%M:%S")

            if local_build_date <= installed_build_date:
                return False

        elif updates.CheckBinaryUpdates(self.constants)._check_if_build_newer(local_version, application_version) is False:
            return False

        # Ask user if they want to move the application to the Applications folder
        self.popup = wx.MessageDialog(
            self.frame,
            f"We've detected an old version of OpenCore-Patcher.app installed in the Application Support directory.\n\nWould you like to replace it with this version?",
            "Move to Applications?",
            wx.YES_NO | wx.ICON_INFORMATION
        )
        self.popup.SetYesNoLabels("Replace", "Ignore")
        answer = self.popup.ShowModal()
        if answer != wx.ID_YES:
            return False

        path = str(self.constants.launcher_binary).split("/Contents/MacOS/OpenCore-Patcher")[0]

        args = [
            "osascript",
            "-e",
            f'''do shell script "ditto {path} '/Library/Application Support/Dortania/OpenCore-Patcher.app'"'''
            ' with prompt "OpenCore Legacy Patcher needs administrator privileges to copy in."'
            " with administrator privileges"
            " without altering line endings",
        ]

        result = subprocess.run(args,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logging.info("- Failed to move application into /Library/Application Support/Dortania/OpenCore-Patcher.app")
            # Notify user we failed to move the application
            self.popup = wx.MessageDialog(
                self.frame,
                f"Failed to move the application to the Applications folder.\n\nThis is likely due to permission errors, you can copy the app manually into '/Library/Application Support/Dortania/OpenCore-Patcher.app' if you continue to see this error.",
                "Failed to Move!",
                style = wx.OK | wx.ICON_EXCLAMATION
            )
            self.popup.ShowModal()
            return False

        subprocess.run(["xattr", "-cr", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["open", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if "AppTranslocation" not in path:
            subprocess.run(["rm", "-R", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.OnCloseFrame()

    def check_for_updates(self, event=None):
        if self.constants.has_checked_updates is True:
            return

        did_find_update = False
        ignore_updates = global_settings.GlobalEnviromentSettings().read_property("IgnoreAppUpdates")
        if ignore_updates is not True:
            self.constants.ignore_updates = False
            self.constants.has_checked_updates = True
            dict = updates.CheckBinaryUpdates(self.constants).check_binary_updates()
            if dict:
                for entry in dict:
                    version = dict[entry]["Version"]
                    github_link = dict[entry]["Github Link"]
                    logging.info(f"New version: {version}")
                    self.dialog = wx.MessageDialog(
                        parent=self.frame,
                        message=f"Current Version: {self.constants.patcher_version}\nNew version: {version}\nWould you like to view?",
                        caption="Update Available for OpenCore Legacy Patcher!",
                        style=wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
                    )
                    self.dialog.SetYesNoCancelLabels("View on Github", "Always Ignore", "Ignore Once")
                    response = self.dialog.ShowModal()
                    did_find_update = True
                    if response == wx.ID_YES:
                        webbrowser.open(github_link)
                    elif response == wx.ID_NO:
                        logging.info("- Setting IgnoreAppUpdates to True")
                        self.constants.ignore_updates = True
                        global_settings.GlobalEnviromentSettings().write_property("IgnoreAppUpdates", True)
        else:
            self.constants.ignore_updates = True
            logging.info("- Ignoring App Updates due to defaults")

        # if did_find_update is False:
        #     self.check_for_local_installs()

    def relaunch_as_root(self, event=None):

        # Add Dialog Box asking if it's ok to relaunch as root
        # If yes, relaunch as root
        # If no, do nothing

        # Create Dialog Box
        self.dialog = wx.MessageDialog(
            self.frame,
            "OpenCore Legacy Patcher needs to relaunch as admin to continue. You will be prompted to enter your password.",
            "Relaunch as root?",
            wx.YES_NO | wx.ICON_QUESTION
        )

        # Show Dialog Box
        if self.dialog.ShowModal() == wx.ID_YES:
            logging.info("Relaunching as root")

            timer_val = 5
            extension = ""
            if event:
                if event.GetEventObject() != wx.Menu:
                    try:
                        if event.GetEventObject().GetLabel() in ["Start Root Patching", "Reinstall Root Patches"]:
                            extension = " --gui_patch"
                        elif event.GetEventObject().GetLabel() == "Revert Root Patches":
                            extension = " --gui_unpatch"
                    except TypeError:
                        pass

            if self.constants.launcher_script is None:
                args_string = f"'{self.constants.launcher_binary}'{extension}"
            else:
                args_string = f"{self.constants.launcher_binary} {self.constants.launcher_script}{extension}"

            args = [
                "osascript",
                "-e",
                f'''do shell script "{args_string}"'''
                ' with prompt "OpenCore Legacy Patcher needs administrator privileges to relaunch as admin."'
                " with administrator privileges"
                " without altering line endings",
            ]

            self.frame.DestroyChildren()
            self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)

            # Header
            self.header = wx.StaticText(self.frame, label="Relaunching as root")
            self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
            self.header.Centre(wx.HORIZONTAL)

            # Add count down label
            self.countdown_label = wx.StaticText(self.frame, label=f"Closing old process in {timer_val} seconds")
            self.countdown_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            # Set below header
            self.countdown_label.SetPosition(
                (
                    self.header.GetPosition().x + 3,
                    self.header.GetPosition().y + self.header.GetSize().height + 3
                )
            )
            self.countdown_label.Centre(wx.HORIZONTAL)
            # Label: You can close this window if app finished relaunching
            self.countdown_label2 = wx.StaticText(self.frame, label="You can close this window if app finished relaunching")
            self.countdown_label2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            # Set below countdown label
            self.countdown_label2.SetPosition(
                (
                    self.countdown_label.GetPosition().x,
                    self.countdown_label.GetPosition().y + self.countdown_label.GetSize().height + 3
                )
            )
            self.countdown_label2.Centre(wx.HORIZONTAL)

            # Set frame right below countdown label
            self.frame.SetSize(
                (
                    -1,
                    self.countdown_label2.GetPosition().y + self.countdown_label2.GetSize().height + 40
                )
            )

            wx.GetApp().Yield()
            subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            while True:
                wx.GetApp().Yield()
                self.countdown_label.SetLabel(f"Closing old process in {timer_val} seconds")
                time.sleep(1)
                timer_val -= 1
                if timer_val == 0:
                    break
            # Close Current Application
            self.OnCloseFrame(event)

    def not_yet_implemented_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)

        # Header
        self.header = wx.StaticText(self.frame, label="🚧 Not Yet Implemented")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Return to main menu
        self.return_button = wx.Button(self.frame, label="Return to Main Menu")
        self.return_button.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_button.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.return_button.Centre(wx.HORIZONTAL)

    def main_menu(self, event=None):
        # Define Menu
        # - Header: OpenCore Legacy Patcher v{self.constants.patcher_version}
        # - Subheader: Model: {self.constants.custom_model or self.computer.real_model}
        # - Options:
        #   - Build and Install OpenCore
        #   - Post Install Root Patch
        #   - Create macOS Installer
        #   - Settings

        # Reset Data in the event of re-run
        self.reset_window()

        # Set header text
        self.frame.SetTitle(f"OpenCore Legacy Patcher ({self.constants.patcher_version})")
        # Header
        self.header = wx.StaticText(self.frame, label=f"OpenCore Legacy Patcher v{self.constants.patcher_version}")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label=f"Model: {self.constants.custom_model or self.computer.real_model}")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Build and Install OpenCore
        self.build_install = wx.Button(self.frame, label="Build and Install OpenCore", size=(200,30))
        self.build_install.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                 self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.build_install.Bind(wx.EVT_BUTTON, self.build_install_menu)
        self.build_install.Centre(wx.HORIZONTAL)

        # Disable button if real_model not in model_array.SupportedSMBIOS
        if (
            (
                self.constants.allow_oc_everywhere is False and \
                self.constants.custom_model is None and \
                self.computer.real_model not in model_array.SupportedSMBIOS
            ) or (
                self.constants.custom_model is None and \
                self.constants.host_is_hackintosh is True
            )
        ):
            self.build_install.Disable()
            self.build_install.SetToolTip(wx.ToolTip("""If building for a native Mac model, \nselect 'Allow Native Models' in Settings.\nIf building for another Mac, change model in Settings"""))

        # Post Install Root Patch
        self.post_install = wx.Button(self.frame, label="Post Install Root Patch", size=(200,30))
        self.post_install.SetPosition(
            wx.Point(
                self.build_install.GetPosition().x,
                 self.build_install.GetPosition().y + self.build_install.GetSize().height
            )
        )
        self.post_install.Bind(wx.EVT_BUTTON, self.root_patch_menu)
        self.post_install.Centre(wx.HORIZONTAL)
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina]:
            self.post_install.SetToolTip(wx.ToolTip("""Graphics Acceleration for Mojave and Catalina has been removed in 0.4.4 onwards.\n\nIf you require this feature, use 0.4.3 or older"""))
            self.post_install.Disable()
        elif self.constants.detected_os < os_data.os_data.mojave:
            self.post_install.SetToolTip(wx.ToolTip("""Root Patching is only available for Big Sur and newer."""))
            self.post_install.Disable()

        # Create macOS Installer
        self.create_installer = wx.Button(self.frame, label="Create macOS Installer", size=(200,30))
        self.create_installer.SetPosition(
            wx.Point(
                self.post_install.GetPosition().x,
                 self.post_install.GetPosition().y + self.post_install.GetSize().height
            )
        )
        self.create_installer.Bind(wx.EVT_BUTTON, self.create_macos_menu)
        self.create_installer.Centre(wx.HORIZONTAL)

        # Settings
        self.settings = wx.Button(self.frame, label="Settings", size=(200,30))
        self.settings.SetPosition(
            wx.Point(
                self.create_installer.GetPosition().x,
                self.create_installer.GetPosition().y + self.create_installer.GetSize().height
            )
        )
        self.settings.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.settings.Centre(wx.HORIZONTAL)

        # Help Button
        self.help_button = wx.Button(self.frame, label="Help", size=(200,30))
        self.help_button.SetPosition(
            wx.Point(
                self.settings.GetPosition().x,
                self.settings.GetPosition().y + self.settings.GetSize().height
            )
        )
        self.help_button.Bind(wx.EVT_BUTTON, gui_help.gui_help_menu(self.constants, self.frame, self.frame_modal).help_menu)
        self.help_button.Centre(wx.HORIZONTAL)


        # Copyright Label
        self.copyright = wx.StaticText(self.frame, label=self.constants.copyright_date)
        self.copyright.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.copyright.SetPosition(
            wx.Point(
                self.help_button.GetPosition().x,
                self.help_button.GetPosition().y + self.help_button.GetSize().height + 5
            )
        )
        self.copyright.Centre(wx.HORIZONTAL)

        # Set Window Size to below Copyright Label
        self.frame.SetSize(
            (
                -1,
                self.copyright.GetPosition().y + self.copyright.GetSize().height + 40
            )
        )

        self.preflight_check()
        if self.finished_auto_patch is False:
            if self.constants.start_build_install is True:
                self.build_install_menu()
            elif "--gui_patch" in sys.argv:
                self.patches = sys_patch_detect.DetectRootPatch(self.computer.real_model, self.constants).detect_patch_set()
                self.root_patch_start()
            elif "--gui_unpatch" in sys.argv:
                self.patches = sys_patch_detect.DetectRootPatch(self.computer.real_model, self.constants).detect_patch_set()
                self.root_patch_revert()
        self.finished_auto_patch = True
        self.constants.start_build_install = False

        if self.app.MainLoop() is None:
            self.app.MainLoop()

    def help_menu(self, event=None):
        # Define Menu
        # Header: Get help with OpenCore Legacy Patcher
        # Subheader: Following resources are available:
        # Button: Official Guide
        # Button: Official Discord Server

        self.reset_frame_modal()
        self.frame_modal.SetSize((self.WINDOW_WIDTH_MAIN - 40,-1))

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Patcher Resources", pos=(10,10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame_modal, label="Following resources are available:")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)


        # Official Guide
        self.guide = wx.Button(self.frame_modal, label="Official Guide", size=(200,30))
        self.guide.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 5

            )
        )
        self.guide.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(self.constants.guide_link))
        self.guide.Centre(wx.HORIZONTAL)

        # Official Discord Server
        self.discord = wx.Button(self.frame_modal, label="Official Discord Server", size=(200,30))
        self.discord.SetPosition(
            wx.Point(
                self.guide.GetPosition().x,
                self.guide.GetPosition().y + self.guide.GetSize().height
            )
        )
        self.discord.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(self.constants.discord_link))
        self.discord.Centre(wx.HORIZONTAL)

        # Overclock Button
        self.overclock = wx.Button(self.frame_modal, label="Official Support Phone", size=(200,30))
        self.overclock.SetPosition(
            wx.Point(
                self.discord.GetPosition().x,
                self.discord.GetPosition().y + self.discord.GetSize().height
            )
        )
        self.overclock.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.overclock.Centre(wx.HORIZONTAL)


        self.return_to_main = wx.Button(self.frame_modal, label="Return to Main Menu", size=(150,30))
        self.return_to_main.SetPosition(
            wx.Point(
                self.overclock.GetPosition().x,
                self.overclock.GetPosition().y + self.overclock.GetSize().height + 5
            )
        )
        self.return_to_main.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main.Centre(wx.HORIZONTAL)

        # Set Window Size to below Copyright Label
        self.frame_modal.SetSize(
            (
                -1,
                self.return_to_main.GetPosition().y + self.return_to_main.GetSize().height + 40
            )
        )
        self.frame_modal.ShowWindowModal()

    def build_install_menu(self, event=None):
        # Define Menu
        # - Header: Build and Install OpenCore
        # - Subheader: Model: {self.constants.custom_model or self.computer.real_model}
        # - Button: Build OpenCore
        # - Textbox: stdout
        # - Button: Return to Main Menu

        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_BUILD, self.WINDOW_HEIGHT_BUILD + 10)

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Build and Install OpenCore", pos=(10,10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame_modal, label=f"Model: {self.constants.custom_model or self.computer.real_model}")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Build OpenCore
        self.build_opencore = wx.Button(self.frame_modal, label="🔨 Build OpenCore", size=(150,30))
        self.build_opencore.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.build_opencore.Bind(wx.EVT_BUTTON, self.build_start)
        self.build_opencore.Centre(wx.HORIZONTAL)

        # Textbox
        # Redirect stdout to a text box
        self.stdout_text = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.stdout_text.SetPosition(wx.Point(self.build_opencore.GetPosition().x, self.build_opencore.GetPosition().y + self.build_opencore.GetSize().height + 10))
        self.stdout_text.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
        # Set width to same as frame
        self.stdout_text.SetSize(self.WINDOW_WIDTH_BUILD, 340)
        # Centre the text box to top of window
        self.stdout_text.Centre(wx.HORIZONTAL)
        self.stdout_text.SetValue("")

        # Set StreamHandler to redirect stdout to textbox
        logging.getLogger().handlers[0].stream = menu_redirect.RedirectText(self.stdout_text, False)

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.stdout_text.GetPosition().x,
                self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame_modal.ShowWindowModal()

        self.build_start()

    def build_start(self, event=None):
        self.build_opencore.Disable()

        while self.is_unpack_finished() is False:
            time.sleep(0.1)

        build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants)
        # Once finished, change build_opencore button to "Install OpenCore"
        self.build_opencore.SetLabel("🔩 Install OpenCore")
        self.build_opencore.Bind(wx.EVT_BUTTON, self.install_menu)

        # Reset stdout
        logging.getLogger().handlers[0].stream = self.stock_stream

        # Throw popup asking to install OpenCore
        self.dialog = wx.MessageDialog(
            parent=self.frame_modal,
            message=f"Would you like to install OpenCore now?",
            caption="Finished building your OpenCore configuration!",
            style=wx.YES_NO | wx.ICON_QUESTION
        )
        self.dialog.SetYesNoLabels("Install to disk", "View build log")
        if self.dialog.ShowModal() == wx.ID_YES:
            self.install_menu()
        else:
            self.build_opencore.Enable()

    def install_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, -1)
        i = 0

        # Header
        self.header = wx.StaticText(self.frame, label="Install OpenCore")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: Select Disk to install OpenCore onto
        self.subheader = wx.StaticText(self.frame, label="Select Disk to install OpenCore onto")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Label: If you're missing disks, ensure they're either FAT32 or formatted as GUI/GPT
        self.missing_disks = wx.StaticText(self.frame, label="Loading disks shortly...")
        self.missing_disks.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.missing_disks.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 5
            )
        )
        self.missing_disks.Centre(wx.HORIZONTAL)

        self.color_note = wx.StaticText(self.frame, label="Note: Blue represent the disk OpenCore is currently booted from")
        self.color_note.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.color_note.SetPosition(
            wx.Point(
                self.missing_disks.GetPosition().x,
                self.missing_disks.GetPosition().y + self.missing_disks.GetSize().height + 5
            )
        )
        self.color_note.Centre(wx.HORIZONTAL)
        self.color_note.Hide()


        # Progress Bar
        self.progress_bar = wx.Gauge(self.frame, range=100, style=wx.GA_HORIZONTAL)
        self.progress_bar.SetPosition(
            wx.Point(
                self.missing_disks.GetPosition().x,
                self.missing_disks.GetPosition().y + self.missing_disks.GetSize().height + 5
            )
        )
        self.progress_bar.SetSize(wx.Size(self.WINDOW_WIDTH_BUILD - 30, 20))
        self.progress_bar.Centre(wx.HORIZONTAL)
        self.progress_bar.SetValue(0)

        self.frame.SetSize(-1, self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 40)

        # Request Disks Present
        def get_disks():
            self.list_disks = install.tui_disk_installation(self.constants).list_disks()

        thread_disk = threading.Thread(target=get_disks)
        thread_disk.start()
        self.progress_bar.Pulse()


        while thread_disk.is_alive():
            self.pulse_alternative(self.progress_bar)
            wx.GetApp().Yield()
        self.progress_bar.Destroy()
        list_disks = self.list_disks

        self.color_note.Show()
        self.missing_disks.SetLabel("Missing disks? Ensure they're FAT32 or formatted as GUID/GPT")
        self.missing_disks.Centre(wx.HORIZONTAL)

        if list_disks:
            if self.constants.booted_oc_disk is not None:
                # disk6s1 -> disk6
                disk_root = self.constants.booted_oc_disk.strip("disk")
                disk_root = "disk" + disk_root.split("s")[0]
            else:
                disk_root = None

            for disk in list_disks:
                # Create a button for each disk
                logging.info(f"{list_disks[disk]['disk']} - {list_disks[disk]['name']} - {list_disks[disk]['size']}")
                self.install_button = wx.Button(self.frame, label=disk, size=(300,30))
                self.install_button.SetLabel(f"{list_disks[disk]['disk']} - {list_disks[disk]['name']} - {list_disks[disk]['size']}")
                self.install_button.SetPosition(
                    wx.Point(
                        self.color_note.GetPosition().x,
                        self.color_note.GetPosition().y + self.color_note.GetSize().height + 3 + i
                    )
                )
                self.install_button.Bind(wx.EVT_BUTTON, lambda event, temp=disk: self.install_oc_disk_select(temp, list_disks))
                self.install_button.Centre(wx.HORIZONTAL)
                i += self.install_button.GetSize().height + 3
                if disk_root == list_disks[disk]['disk']:
                    # Set label colour to red
                    self.install_button.SetForegroundColour(self.hyperlink_colour)

        else:
            # Label: No disks found
            self.install_button = wx.StaticText(self.frame, label="Failed to find any applicable disks")
            self.install_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
            self.install_button.SetPosition(
                wx.Point(
                    self.color_note.GetPosition().x,
                    self.color_note.GetPosition().y + self.color_note.GetSize().height + 3
                )
            )
            self.install_button.Centre(wx.HORIZONTAL)


        self.reload_button = wx.Button(self.frame, label="Search for Disks Again", size=(170,-1))
        self.reload_button.SetPosition(
            wx.Point(
                self.install_button.GetPosition().x,
                self.install_button.GetPosition().y + self.install_button.GetSize().height + 10
            )
        )
        self.reload_button.Bind(wx.EVT_BUTTON, self.install_menu)
        self.reload_button.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu", size=(170,-1))
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.reload_button.GetPosition().x,
                self.reload_button.GetPosition().y + self.reload_button.GetSize().height + 8
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def install_oc_disk_select(self, disk, disk_data):
        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_BUILD - 40, -1)

        i = 0

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Install OpenCore", pos=(10,10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: Select Partition to install OpenCore onto
        self.subheader = wx.StaticText(self.frame_modal, label="Select Partition to install OpenCore onto")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        list_partitions = install.tui_disk_installation(self.constants).list_partitions(disk, disk_data)
        for partition in list_partitions:
            logging.info(f"{list_partitions[partition]['partition']} - {list_partitions[partition]['name']} - {list_partitions[partition]['size']}")
            self.install_button = wx.Button(self.frame_modal, label=partition, size=(300,30))
            self.install_button.SetLabel(f"{list_partitions[partition]['partition']} - {list_partitions[partition]['name']} - {list_partitions[partition]['size']}")
            self.install_button.SetPosition(
                wx.Point(
                    self.subheader.GetPosition().x,
                    self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                )
            )
            self.install_button.Bind(wx.EVT_BUTTON, lambda event, temp=partition: self.install_oc_process(temp))
            self.install_button.Centre(wx.HORIZONTAL)
            i += self.install_button.GetSize().height + 3
            if self.constants.booted_oc_disk == list_partitions[partition]['partition']:
                # Set label colour to red
                self.install_button.SetForegroundColour(self.hyperlink_colour)

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.install_button.GetPosition().x,
                self.install_button.GetPosition().y + self.install_button.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, lambda event: self.frame_modal.Close())
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame_modal.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        self.frame_modal.ShowWindowModal()

    def install_oc_process(self, partition):
        logging.info(f"Installing OpenCore to {partition}")
        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_BUILD - 20, self.WINDOW_HEIGHT_BUILD)

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Install OpenCore", pos=(10,10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Textbox
        # Redirect stdout to a text box
        self.stdout_text = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.stdout_text.SetPosition(wx.Point(self.header.GetPosition().x, self.header.GetPosition().y + self.header.GetSize().height + 10))
        self.stdout_text.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
        # Set width to same as frame
        self.stdout_text.SetSize(self.WINDOW_WIDTH_BUILD - 40, 240)
        # Centre the text box to top of window
        self.stdout_text.Centre(wx.HORIZONTAL)
        self.stdout_text.SetValue("")

        # Update frame height to right below
        self.frame_modal.SetSize(-1, self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 40)
        self.frame_modal.ShowWindowModal()

        logging.getLogger().handlers[0].stream = menu_redirect.RedirectText(self.stdout_text, False)
        result = install.tui_disk_installation(self.constants).install_opencore(partition)
        logging.getLogger().handlers[0].stream = self.stock_stream

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.stdout_text.GetPosition().x,
                self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 10

            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame_modal.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 20)

        if result is True:
            if not self.constants.custom_model:
                self.reboot_system(message="OpenCore has finished installing to disk.\n\nYou will need to reboot and hold the Option key and select OpenCore/Boot EFI's option.\n\nWould you like to reboot?")
            else:
                popup_message = wx.MessageDialog(self.frame,f"OpenCore has finished installing to disk.\n\nYou can eject the drive, insert it into the {self.constants.custom_model}, reboot, hold the Option key and select OpenCore/Boot EFI's option.", "Success", wx.OK)
                popup_message.ShowModal()

    def check_if_new_patches_needed(self, patches):
        # Check if there's any new patches for the user to install
        # Newer users will assume the root patch menu will present missing patches.
        # Thus we'll need to see if the exact same OCLP build was used already
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


    def root_patch_menu(self, event=None):
        # Define Menu
        # Header: Post-Install Menu
        # Subheader: Available patches for system:
        # Label: Placeholder for patch name
        # Button: Start Root Patching
        # Button: Revert Root Patches
        # Button: Return to Main Menu
        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_BUILD - 40, -1)

        # Header
        self.header = wx.StaticText(self.frame_modal, label=f"Post-Install Menu", pos=(10,10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame_modal, label="Available patches for system:")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        patches = sys_patch_detect.DetectRootPatch(self.computer.real_model, self.constants).detect_patch_set()
        self.patches = patches
        can_unpatch = patches["Validation: Unpatching Possible"]
        if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
            logging.info("- No applicable patches available")
            patches = []

        # Check if OCLP has already applied the same patches
        no_new_patches = False
        if patches:
            no_new_patches = not self.check_if_new_patches_needed(patches)

        i = 0
        if patches:
            if no_new_patches is False:
                for patch in patches:
                    # Add Label for each patch
                    if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                        logging.info(f"- Adding patch: {patch} - {patches[patch]}")
                        self.patch_label = wx.StaticText(self.frame_modal, label=f"- {patch}")
                        self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                        self.patch_label.SetPosition(
                            wx.Point(
                                self.subheader.GetPosition().x,
                                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                            )
                        )
                        i = i + self.patch_label.GetSize().height + 3
            else:
                self.patch_label = wx.StaticText(self.frame_modal, label=f"All applicable patches already installed")
                self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                self.patch_label.SetPosition(
                    wx.Point(
                        self.subheader.GetPosition().x,
                        self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                    )
                )
                i = i + self.patch_label.GetSize().height + 3
                self.patch_label.Centre(wx.HORIZONTAL)
            if patches["Validation: Patching Possible"] is False:
                self.patch_label = wx.StaticText(self.frame_modal, label="Cannot Patch due to following reasons:")
                self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                self.patch_label.SetPosition(
                    wx.Point(
                        self.subheader.GetPosition().x,
                        self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                    )
                )
                self.patch_label.Centre(wx.HORIZONTAL)
                i = i + self.patch_label.GetSize().height + 3
                for patch in patches:
                    if patch == "Validation: Unpatching Possible":
                        continue
                    if patch.startswith("Validation") and patches[patch] is True:
                        logging.info(f"- Adding check: {patch} - {patches[patch]}")
                        self.patch_label = wx.StaticText(self.frame_modal, label=f"- {patch[12:]}")
                        self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                        self.patch_label.SetPosition(
                            wx.Point(
                                self.subheader.GetPosition().x,
                                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                            )
                        )
                        i = i + self.patch_label.GetSize().height + 3

                i += 10
                if self.constants.host_is_hackintosh is False:
                    self.patch_label = wx.StaticText(self.frame_modal, label="Please run 'Build and Install OpenCore' and reboot")
                    self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                    self.patch_label.SetPosition(
                        wx.Point(
                            self.subheader.GetPosition().x,
                            self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                        )
                    )
                    self.patch_label.Centre(wx.HORIZONTAL)
                    i = i + self.patch_label.GetSize().height + 3

                    self.patch_label = wx.StaticText(self.frame_modal, label="to remove these errors.")
                    self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                    self.patch_label.SetPosition(
                        wx.Point(
                            self.subheader.GetPosition().x,
                            self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                        )
                    )
                    self.patch_label.Centre(wx.HORIZONTAL)
                    i = i + self.patch_label.GetSize().height + 3


            else:
                if self.constants.computer.oclp_sys_version and self.constants.computer.oclp_sys_date:
                    date = self.constants.computer.oclp_sys_date.split(" @")
                    if len(date) == 2:
                        date = date[0]
                    else:
                        date = ""
                    patch_text = f"{self.constants.computer.oclp_sys_version}, {date}"

                    self.patch_label = wx.StaticText(self.frame_modal, label="Root Volume last patched:")
                    self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    self.patch_label.SetPosition(
                        wx.Point(
                            self.subheader.GetPosition().x,
                            self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                        )
                    )
                    self.patch_label.Centre(wx.HORIZONTAL)
                    i = i + self.patch_label.GetSize().height + 3

                    self.patch_label = wx.StaticText(self.frame_modal, label=patch_text)
                    self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                    self.patch_label.SetPosition(
                        wx.Point(
                            self.subheader.GetPosition().x + 20,
                            self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                        )
                    )
                    self.patch_label.Centre(wx.HORIZONTAL)
                    i = i + self.patch_label.GetSize().height + 3
        else:
            # Prompt user with no patches found
            self.patch_label = wx.StaticText(self.frame_modal, label="No patches needed")
            self.patch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            self.patch_label.SetPosition(
                wx.Point(
                    self.subheader.GetPosition().x,
                    self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                )
            )
            self.patch_label.Centre(wx.HORIZONTAL)

        # Start Root Patching
        self.start_root_patching = wx.Button(self.frame_modal, label="Start Root Patching", size=(170, -1))
        if no_new_patches is True:
            self.start_root_patching.Label = "Reinstall Root Patches"
        self.start_root_patching.SetPosition(
            wx.Point(
                self.patch_label.GetPosition().x,
                self.patch_label.GetPosition().y + self.patch_label.GetSize().height + 10
            )
        )

        self.start_root_patching.Centre(wx.HORIZONTAL)
        if not patches:
            self.start_root_patching.Disable()

        # Revert Root Patches
        self.revert_root_patches = wx.Button(self.frame_modal, label="Revert Root Patches", size=(170, -1))
        self.revert_root_patches.SetPosition(
            wx.Point(
                self.start_root_patching.GetPosition().x,
                self.start_root_patching.GetPosition().y + self.start_root_patching.GetSize().height + 3
            )
        )

        self.revert_root_patches.Centre(wx.HORIZONTAL)
        if self.constants.detected_os < os_data.os_data.big_sur:
            self.revert_root_patches.Disable()

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.revert_root_patches.GetPosition().x,
                self.revert_root_patches.GetPosition().y + self.revert_root_patches.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        uid = os.geteuid()
        if uid == 0:
            self.start_root_patching.Bind(wx.EVT_BUTTON, self.root_patch_start)
            self.revert_root_patches.Bind(wx.EVT_BUTTON, self.root_patch_revert)
        else:
            self.start_root_patching.Bind(wx.EVT_BUTTON, self.relaunch_as_root)
            self.revert_root_patches.Bind(wx.EVT_BUTTON, self.relaunch_as_root)

        if patches:
            if patches["Validation: Patching Possible"] is False:
                self.start_root_patching.Disable()
        if can_unpatch is False:
            self.revert_root_patches.Disable()

        self.frame_modal.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        self.frame_modal.ShowWindowModal()

    def root_patch_start(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.WINDOW_HEIGHT_MAIN)

        # Header
        self.header = wx.StaticText(self.frame, label="Root Patching", pos=(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label="Preparing PatcherSupportPkg binaries")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        self.developer_note = wx.StaticText(self.frame, label="Starting shortly")
        self.developer_note.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.developer_note.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.developer_note.Centre(wx.HORIZONTAL)

        self.progress_bar = wx.Gauge(self.frame, range=100, size=(200, 10))
        self.progress_bar.SetPosition(
            wx.Point(
                self.developer_note.GetPosition().x,
                self.developer_note.GetPosition().y + self.developer_note.GetSize().height + 10
            )
        )
        self.progress_bar.SetValue(0)
        self.progress_bar.Centre(wx.HORIZONTAL)
        self.progress_bar.Pulse()

        self.frame.SetSize(-1, self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 60)
        self.frame.Show()
        while self.is_unpack_finished() is False:
            self.pulse_alternative(self.progress_bar)
            wx.GetApp().Yield()

        if self.patches["Settings: Kernel Debug Kit missing"] is True:
            # Download KDK (if needed)
            self.subheader.SetLabel("Downloading Kernel Debug Kit")
            self.subheader.Centre(wx.HORIZONTAL)
            self.developer_note.SetLabel("Starting shortly")

            wx.GetApp().Yield()

            kdk_result = False
            self.kdk_obj = None
            def kdk_thread_spawn():
                self.kdk_obj = kdk_handler.KernelDebugKitObject(self.constants, self.constants.detected_os_build, self.constants.detected_os_version)

            kdk_thread = threading.Thread(target=kdk_thread_spawn)
            kdk_thread.start()

            while kdk_thread.is_alive():
                self.pulse_alternative(self.progress_bar)
                wx.GetApp().Yield()

            self.progress_bar.Hide()

            if self.kdk_obj.success is True:
                kdk_download_obj = self.kdk_obj.retrieve_download()
                if not kdk_download_obj:
                    kdk_result = True
                else:
                    kdk_download_obj.download()

                    self.header.SetLabel(f"Downloading KDK Build: {self.kdk_obj.kdk_url_build}")
                    self.header.Centre(wx.HORIZONTAL)

                    self.progress_bar.SetValue(0)
                    # Set below developer note
                    self.progress_bar.SetPosition(
                        wx.Point(
                            self.developer_note.GetPosition().x,
                            self.developer_note.GetPosition().y + self.developer_note.GetSize().height + 10
                        )
                    )
                    self.progress_bar.Centre(wx.HORIZONTAL)
                    self.progress_bar.Show()

                    self.frame.SetSize(-1, self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 60)

                    while kdk_download_obj.is_active():
                        self.subheader.SetLabel(f"{utilities.human_fmt(kdk_download_obj.downloaded_file_size)} downloaded of {utilities.human_fmt(kdk_download_obj.total_file_size)} ({kdk_download_obj.get_percent():.2f}%)")
                        self.subheader.Centre(wx.HORIZONTAL)
                        self.developer_note.SetLabel(
                            f"Average download speed: {utilities.human_fmt(kdk_download_obj.get_speed())}/s"
                        )
                        self.developer_note.Centre(wx.HORIZONTAL)

                        self.progress_bar.SetValue(int(kdk_download_obj.get_percent()))

                        wx.GetApp().Yield()
                        time.sleep(0.1)

                    if kdk_download_obj.download_complete is False:
                        logging.error("Failed to download KDK")
                        logging.error(kdk_download_obj.error_msg)
                        error_msg = kdk_download_obj.error_msg
                    else:
                        kdk_result = self.kdk_obj.validate_kdk_checksum()
                        error_msg = self.kdk_obj.error_msg
            else:
                logging.error("Failed to download KDK")
                logging.error(self.kdk_obj.error_msg)
                error_msg = self.kdk_obj.error_msg

            if kdk_result is False:
                # Create popup window to inform user of error
                self.popup = wx.MessageDialog(
                    self.frame,
                    f"A problem occurred trying to download the Kernel Debug Kit:\n\n{error_msg}",
                    "Kernel Debug Kit",
                    wx.ICON_ERROR
                )
                self.popup.ShowModal()
                self.finished_auto_patch = True
                self.main_menu()

        self.reset_frame_modal()
        self.frame_modal.SetSize(-1, self.WINDOW_HEIGHT_MAIN)

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Root Patching", pos=(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame_modal, label="Starting root volume patching")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        self.developer_note = wx.StaticText(self.frame_modal, label="Starting shortly")
        self.developer_note.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.developer_note.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.developer_note.Centre(wx.HORIZONTAL)

        # Text Box
        self.text_box = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.text_box.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.text_box.SetPosition(
            wx.Point(
                self.developer_note.GetPosition().x,
                self.developer_note.GetPosition().y + self.developer_note.GetSize().height + 3
            )
        )
        self.text_box.SetSize(
            wx.Size(
                self.frame_modal.GetSize().width - 10,
                self.frame_modal.GetSize().height + self.text_box.GetPosition().y + 80
            )
        )
        self.text_box.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.text_box.GetPosition().x,
                self.text_box.GetPosition().y + self.text_box.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
        self.return_to_main_menu.Disable()

        self.frame_modal.SetSize(self.WINDOW_WIDTH_BUILD, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

        logging.getLogger().handlers[0].stream = menu_redirect.RedirectText(self.text_box, True)
        self.frame_modal.ShowWindowModal()
        wx.GetApp().Yield()
        try:
            sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, self.patches).start_patch()
        except Exception as e:
            self.text_box.AppendText(f"- An internal error occurred while running the Root Patcher:\n{str(e)}")
            pass
        logging.getLogger().handlers[0].stream = self.stock_stream
        if self.constants.root_patcher_succeeded is True:
            logging.info("- Root Patcher finished successfully")
            if self.constants.needs_to_open_preferences is True:
                if self.constants.detected_os >= os_data.os_data.ventura:
                    self.reboot_system(message="Root Patcher finished successfully!\nIf you were prompted to open System Settings to authorize new kexts, this can be ignored. Your system is ready once restarted.\n\nWould you like to reboot now?")
                else:
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
                        self.OnCloseFrame(None)
            else:
                self.reboot_system(message="Root Patcher finished successfully\nWould you like to reboot now?")
        self.return_to_main_menu.Enable()

        wx.GetApp().Yield()

    def root_patch_revert(self, event=None):
        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_BUILD, self.WINDOW_HEIGHT_MAIN)

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Revert Root Patches", pos=(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        if self.constants.detected_os == os_data.os_data.big_sur:
            self.subheader = wx.StaticText(self.frame_modal, label="Currently experimental in Big Sur")
        else:
            self.subheader = wx.StaticText(self.frame_modal, label="Reverting to last sealed snapshot")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        self.developer_note = wx.StaticText(self.frame_modal, label="Starting shortly")
        self.developer_note.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.developer_note.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.developer_note.Centre(wx.HORIZONTAL)

        # Text Box
        self.text_box = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.text_box.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.text_box.SetPosition(
            wx.Point(
                self.developer_note.GetPosition().x,
                self.developer_note.GetPosition().y + self.developer_note.GetSize().height + 3
            )
        )
        self.text_box.SetSize(
            wx.Size(
                self.frame_modal.GetSize().width - 10,
                self.frame_modal.GetSize().height + self.text_box.GetPosition().y + 10
            )
        )
        self.text_box.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.text_box.GetPosition().x,
                self.text_box.GetPosition().y + self.text_box.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
        self.return_to_main_menu.Disable()

        self.frame_modal.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

        # Start reverting root patches
        logging.getLogger().handlers[0].stream = menu_redirect.RedirectText(self.text_box, True)
        wx.GetApp().Yield()
        self.frame_modal.ShowWindowModal()
        while self.is_unpack_finished() is False:
            time.sleep(0.1)
        try:
            sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, self.patches).start_unpatch()
        except Exception as e:
            self.text_box.AppendText(f"- An internal error occurred while running the Root Patcher:\n{str(e)}")
            pass
        logging.getLogger().handlers[0].stream = self.stock_stream
        if self.constants.root_patcher_succeeded is True:
            logging.info("- Root Patcher finished successfully")
            self.reboot_system(message="Root Patcher finished successfully\nWould you like to reboot now?")
        self.return_to_main_menu.Enable()
        wx.GetApp().Yield()

    def create_macos_menu(self, event=None):
        # Define Menu
        # Header: Create macOS Installer
        # Options:
        #   - Download macOS Installer
        #   - Use existing macOS Installer
        #   - Return to Main Menu

        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_MAIN - 20 , -1)

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Create macOS Installer", pos=wx.Point(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Button: Download macOS Installer
        self.download_macos_installer = wx.Button(self.frame_modal, label="Download macOS Installer", size=(200, 30))
        self.download_macos_installer.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.download_macos_installer.Bind(wx.EVT_BUTTON, self.grab_installer_data)
        self.download_macos_installer.Centre(wx.HORIZONTAL)

        # Button: Use existing macOS Installer
        self.use_existing_macos_installer = wx.Button(self.frame_modal, label="Use existing macOS Installer", size=(200, 30))
        self.use_existing_macos_installer.SetPosition(
            wx.Point(
                self.download_macos_installer.GetPosition().x,
                self.download_macos_installer.GetPosition().y + self.download_macos_installer.GetSize().height
            )
        )
        self.use_existing_macos_installer.Bind(wx.EVT_BUTTON, self.flash_installer_menu)
        self.use_existing_macos_installer.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.use_existing_macos_installer.GetPosition().x,
                self.use_existing_macos_installer.GetPosition().y + self.use_existing_macos_installer.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame_modal.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        self.frame_modal.ShowWindowModal()

    def grab_installer_data(self, event=None, ias=None):
        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label="Pulling installer catalog")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Label: Download...
        self.download_label = wx.StaticText(self.frame, label="Downloading installer catalog...")
        self.download_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
        self.download_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 15
            )
        )
        self.download_label.Centre(wx.HORIZONTAL)

        # Progress Bar
        self.progress_bar = wx.Gauge(self.frame, range=100, size=(200, 30))
        self.progress_bar.SetPosition(
            wx.Point(
                self.download_label.GetPosition().x,
                self.download_label.GetPosition().y + self.download_label.GetSize().height + 10
            )
        )
        self.progress_bar.Centre(wx.HORIZONTAL)
        self.progress_bar.Pulse()


        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.progress_bar.GetPosition().x,
                self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 15
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        self.frame.Show()
        wx.GetApp().Yield()

        # Download installer catalog
        if ias is None:
            def ia():
                remote_obj = macos_installer_handler.RemoteInstallerCatalog(seed_override=macos_installer_handler.SeedType.DeveloperSeed)
                self.available_installers        = remote_obj.available_apps
                self.available_installers_latest = remote_obj.available_apps_latest

            logging.info("- Downloading installer catalog...")
            thread_ia = threading.Thread(target=ia)
            thread_ia.start()

            while thread_ia.is_alive() or self.is_unpack_finished() is False:
                self.pulse_alternative(self.progress_bar)
                wx.GetApp().Yield()
            available_installers = self.available_installers
        else:
            logging.info("- Using existing installer catalog...")
            available_installers = ias

        self.reset_frame_modal()
        self.frame_modal.SetSize(self.WINDOW_WIDTH_MAIN - 20, -1)

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Download macOS Installer", pos=wx.Point(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader:
        self.subheader = wx.StaticText(self.frame_modal, label="Installers currently available from Apple:")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        available_installers_backup = available_installers.copy()

        i = -20
        if available_installers:
            if ias is None:
                available_installers = self.available_installers_latest
            for app in available_installers:
                logging.info(f"macOS {available_installers[app]['Version']} ({available_installers[app]['Build']}):\n  - Size: {utilities.human_fmt(available_installers[app]['Size'])}\n  - Source: {available_installers[app]['Source']}\n  - Variant: {available_installers[app]['Variant']}\n  - Link: {available_installers[app]['Link']}\n")
                if available_installers[app]['Variant'] in ["DeveloperSeed" , "PublicSeed"]:
                    extra = " Beta"
                else:
                    extra = ""
                self.install_selection = wx.Button(self.frame_modal, label=f"macOS {available_installers[app]['Version']}{extra} ({available_installers[app]['Build']} - {utilities.human_fmt(available_installers[app]['Size'])})", size=(280, 30))
                i = i + 25
                self.install_selection.SetPosition(
                    wx.Point(
                        self.subheader.GetPosition().x,
                        self.subheader.GetPosition().y + self.subheader.GetSize().height + i
                    )
                )
                self.install_selection.Bind(wx.EVT_BUTTON, lambda event, temp=app: self.download_macos_click(available_installers[temp]))
                self.install_selection.Centre(wx.HORIZONTAL)
        else:
            self.install_selection = wx.StaticText(self.frame_modal, label="No installers available")
            i = i + 25
            self.install_selection.SetPosition(
                wx.Point(
                    self.subheader.GetPosition().x,
                    self.subheader.GetPosition().y + self.subheader.GetSize().height + i
                )
            )
            self.install_selection.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
            self.install_selection.Centre(wx.HORIZONTAL)

        self.load_all_installers = wx.Button(self.frame_modal, label="Show all available installers")
        self.load_all_installers.SetPosition(
            wx.Point(
                self.install_selection.GetPosition().x,
                self.install_selection.GetPosition().y + self.install_selection.GetSize().height + 7
            )
        )
        self.load_all_installers.Bind(wx.EVT_BUTTON, lambda event: self.reload_macos_installer_catalog(ias=available_installers_backup))
        self.load_all_installers.Centre(wx.HORIZONTAL)
        if ias or not available_installers:
            self.load_all_installers.Disable()

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.load_all_installers.GetPosition().x,
                self.load_all_installers.GetPosition().y + self.load_all_installers.GetSize().height + 5
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame_modal.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        self.frame_modal.ShowWindowModal()

    def reload_macos_installer_catalog(self, event=None, ias=None):
        self.grab_installer_data(ias=ias)

    def download_macos_click(self, app_dict):
        # Unsupported Models include:
        #   - USB 1.1 machines (Penryn, MacPro3,1-5,1)
        #   - Non-Metal GPUs
        has_legacy_usb = False
        issues_list = ""
        model = self.constants.custom_model or self.constants.computer.real_model
        if model in ["MacPro3,1", "MacPro4,1", "MacPro5,1"]:
            has_legacy_usb = True
            issues_list = "- Lack of Keyboard/Mouse in macOS installer without a USB hub\n"
        elif model in smbios_data.smbios_dictionary[model]:
            if "CPU Generation" in smbios_data.smbios_dictionary[model]:
                if smbios_data.smbios_dictionary[model]["CPU Generation"] <= cpu_data.cpu_data.penryn:
                    has_legacy_usb = True
                    if model.startswith("MacBook"):
                        issues_list = "- Lack of internal Keyboard/Trackpad in macOS installer\n"
                    elif not model.startswith("MacPro"):
                        issues_list = "- Lack of internal Keyboard/Mouse in macOS installer\n"

        if has_legacy_usb:
            try:
                app_major = app_dict['Version'].split(".")[0]
                if float(app_major) > self.constants.os_support:
                    # Throw pop up warning OCLP does not support this OS
                    os =  os_data.os_conversion.convert_kernel_to_marketing_name(os_data.os_conversion.os_to_kernel(app_major))
                    dlg = wx.MessageDialog(self.frame_modal, f"OpenCore Legacy Patcher may not fully support macOS {os} on your machine ({model}).\n\nThe main issues include:\n{issues_list}\nThe newest version we recommend is macOS {os_data.os_conversion.convert_kernel_to_marketing_name(os_data.os_conversion.os_to_kernel(str(self.constants.os_support)))}. For more information, see the associated Github Issue.\n\nWould you still want to continue downloading macOS {os}?", "Unsupported OS", style=wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                    dlg.SetYesNoCancelLabels("View Github Issue", "Download Anyways", "Cancel")
                    result = dlg.ShowModal()
                    if result == wx.ID_YES:
                        webbrowser.open("https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021")
                        return
                    elif result == wx.ID_NO:
                        pass
                    else:
                        return
            except ValueError:
                pass

        # Ensure we have space to both download and extract the installer
        host_space = utilities.get_free_space()
        needed_space = app_dict['Size'] * 2
        if host_space < needed_space:
            dlg = wx.MessageDialog(self.frame_modal, f"You do not have enough free space to download and extract this installer. Please free up some space and try again\n\n{utilities.human_fmt(host_space)} available vs {utilities.human_fmt(needed_space)} required", "Insufficient Space", wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            return

        self.frame.DestroyChildren()
        installer_name = f"macOS {app_dict['Version']} ({app_dict['Build']})"

        # Header
        self.header = wx.StaticText(self.frame, label=f"Downloading {installer_name}")
        self.frame.SetSize(self.header.GetSize().width + 200, -1)
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Label: Download...
        self.download_label = wx.StaticText(self.frame, label="Starting download shortly...")
        self.download_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
        self.download_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.download_label.Centre(wx.HORIZONTAL)

        self.download_label_2 = wx.StaticText(self.frame, label="")
        self.download_label_2.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.download_label_2.SetPosition(
            wx.Point(
                self.download_label.GetPosition().x,
                self.download_label.GetPosition().y + self.download_label.GetSize().height + 5
            )
        )
        self.download_label_2.Centre(wx.HORIZONTAL)

        # Progress Bar
        self.download_progress = wx.Gauge(self.frame, range=100, size=(self.frame.GetSize().width - 100, 20))
        self.download_progress.SetPosition(
            wx.Point(
                self.download_label_2.GetPosition().x,
                self.download_label_2.GetPosition().y + self.download_label_2.GetSize().height + 5
            )
        )
        self.download_progress.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.download_progress.GetPosition().x,
                self.download_progress.GetPosition().y + self.download_progress.GetSize().height + 15
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        wx.GetApp().Yield()


        ia_download = network_handler.DownloadObject(app_dict['Link'], self.constants.payload_path / "InstallAssistant.pkg")
        ia_download.download()

        while ia_download.is_active():
            wx.GetApp().Yield()
            self.download_label.SetLabel(f"{utilities.human_fmt(ia_download.downloaded_file_size)} downloaded of {utilities.human_fmt(ia_download.total_file_size)} ({ia_download.get_percent():.2f}%)")
            self.download_label.Centre(wx.HORIZONTAL)
            self.download_label_2.SetLabel(
                f"Average download speed: {utilities.human_fmt(ia_download.get_speed())}/s"
            )
            self.download_label_2.Centre(wx.HORIZONTAL)

            self.download_progress.SetValue(int(ia_download.get_percent()))

            wx.GetApp().Yield()
            time.sleep(0.1)


        # Download macOS install data
        if ia_download.download_complete is True:
            self.download_label.SetLabel(f"Finished Downloading {installer_name}")
            self.download_label.Centre(wx.HORIZONTAL)
            wx.App.Get().Yield()
            self.installer_validation(apple_integrity_file_link=app_dict['integrity'])
        else:
            self.download_label.SetLabel(f"Failed to download {installer_name}")
            self.download_label.Centre(wx.HORIZONTAL)


    def installer_validation(self, event=None, apple_integrity_file_link=""):
        self.frame.DestroyChildren()

        # Header: Verifying InstallAssistant.pkg
        self.header = wx.StaticText(self.frame, label="Verifying InstallAssistant.pkg")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Label: Verifying Chunk 0 of 1200
        self.verifying_chunk_label = wx.StaticText(self.frame, label="Verifying Chunk 0 of 1200")
        self.verifying_chunk_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
        self.verifying_chunk_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.verifying_chunk_label.Centre(wx.HORIZONTAL)


        # Progress Bar
        self.progress_bar = wx.Gauge(self.frame, range=1200, size=(300, 25))
        self.progress_bar.SetPosition(
            wx.Point(
                self.verifying_chunk_label.GetPosition().x,
                self.verifying_chunk_label.GetPosition().y + self.verifying_chunk_label.GetSize().height + 10
            )
        )
        self.progress_bar.Centre(wx.HORIZONTAL)


        # Button: Return to Main Menu
        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.progress_bar.GetPosition().x,
                self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

        wx.App.Get().Yield()
        integrity_path = Path(Path(self.constants.payload_path) / Path(apple_integrity_file_link.split("/")[-1]))

        chunklist_stream = network_handler.NetworkUtilities().get(apple_integrity_file_link).content
        if chunklist_stream:
            # If we're unable to download the integrity file immediately after downloading the IA, there's a legitimate issue
            # on Apple's end.
            # Fail gracefully and just head to installing the IA.
            utilities.disable_sleep_while_running()
            chunk_obj = integrity_verification.ChunklistVerification(self.constants.payload_path / Path("InstallAssistant.pkg"), chunklist_stream)
            if chunk_obj.chunks:
                self.progress_bar.SetValue(chunk_obj.current_chunk)
                self.progress_bar.SetRange(chunk_obj.total_chunks)

                wx.App.Get().Yield()
                chunk_obj.validate()

                while chunk_obj.status == integrity_verification.ChunklistStatus.IN_PROGRESS:
                    self.progress_bar.SetValue(chunk_obj.current_chunk)
                    self.verifying_chunk_label.SetLabel(f"Verifying Chunk {chunk_obj.current_chunk} of {chunk_obj.total_chunks}")
                    wx.App.Get().Yield()

                if chunk_obj.status == integrity_verification.ChunklistStatus.FAILURE:
                    self.popup = wx.MessageDialog(
                        self.frame,
                            f"We've found that Chunk {chunk_obj.current_chunk} of {chunk_obj.total_chunks} has failed the integrity check.\n\nThis generally happens when downloading on unstable connections such as WiFi or cellular.\n\nPlease try redownloading again on a stable connection (ie. Ethernet)",
                            "Corrupted Installer!",
                            style = wx.OK | wx.ICON_EXCLAMATION
                        )
                    self.popup.ShowModal()
                    self.main_menu()

                logging.info("Integrity check passed!")
            else:
                logging.info("Invalid integrity file provided")
        else:
            logging.info("Failed to download integrity file, skipping integrity check.")

        wx.App.Get().Yield()
        self.header.SetLabel("Installing InstallAssistant.pkg")
        self.header.Centre(wx.HORIZONTAL)
        self.verifying_chunk_label.SetLabel("Installing into Applications folder")
        self.verifying_chunk_label.Centre(wx.HORIZONTAL)
        thread_install = threading.Thread(target=macos_installer_handler.InstallerCreation().install_macOS_installer, args=(self.constants.payload_path,))
        thread_install.start()
        self.progress_bar.Pulse()
        while thread_install.is_alive():
            wx.App.Get().Yield()

        self.progress_bar.SetValue(self.progress_bar.GetRange())
        self.return_to_main_menu.SetLabel("Flash Installer")
        self.verifying_chunk_label.SetLabel("Finished extracting to Applications folder!")
        self.verifying_chunk_label.Centre(wx.HORIZONTAL)
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.flash_installer_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
        utilities.enable_sleep_after_running()


    def flash_installer_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)
        # Header
        self.header = wx.StaticText(self.frame, label="Select macOS Installer")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)
        # Subheader: Installers found in /Applications
        self.subheader = wx.StaticText(self.frame, label="Searching for Installers in /Applications")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        self.available_installers = None

        # Spawn thread to get list of installers
        def get_installers():
            self.available_installers = macos_installer_handler.LocalInstallerCatalog().available_apps

        thread_get_installers = threading.Thread(target=get_installers)
        thread_get_installers.start()

        # Progress bar
        self.progress_bar = wx.Gauge(self.frame, range=100, size=(self.WINDOW_WIDTH_MAIN - 50, -1))
        self.progress_bar.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 10
            )
        )
        self.progress_bar.Centre(wx.HORIZONTAL)
        self.progress_bar.Pulse()

        # Set window size
        self.frame.SetSize(-1, self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 40)

        while thread_get_installers.is_alive():
            self.pulse_alternative(self.progress_bar)
            wx.App.Get().Yield()

        # Remove progress bar
        self.progress_bar.Destroy()

        self.subheader.SetLabel("Installers found in Applications folder")
        self.subheader.Centre(wx.HORIZONTAL)

        available_installers = self.available_installers

        i = -7
        if available_installers:
            logging.info("Installer(s) found:")
            for app in available_installers:
                logging.info(f"- {available_installers[app]['Short Name']}: {available_installers[app]['Version']} ({available_installers[app]['Build']})")
                self.install_selection = wx.Button(self.frame, label=f"{available_installers[app]['Short Name']}: {available_installers[app]['Version']} ({available_installers[app]['Build']})", size=(320, 30))
                i = i + 25
                self.install_selection.SetPosition(
                    wx.Point(
                        self.header.GetPosition().x,
                        self.header.GetPosition().y + self.header.GetSize().height + i
                    )
                )
                self.install_selection.Bind(wx.EVT_BUTTON, lambda event, temp=app: self.format_usb_menu(available_installers[temp]['Short Name'], available_installers[temp]['Path']))
                self.install_selection.Centre(wx.HORIZONTAL)
        else:
            logging.info("No installers found")
            # Label: No Installers Found
            self.install_selection = wx.StaticText(self.frame, label="No Installers Found in Applications folder")
            self.install_selection.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
            self.install_selection.SetPosition(
                # Set Position below header
                wx.Point(
                    self.header.GetPosition().x,
                    self.header.GetPosition().y + self.header.GetSize().height + 15
                )
            )
            self.install_selection.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.install_selection.GetPosition().x,
                self.install_selection.GetPosition().y + self.install_selection.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def format_usb_menu(self, installer_name, installer_path):
        self.frame.DestroyChildren()
        logging.info(installer_path)

        # Header
        self.header = wx.StaticText(self.frame, label="Format USB")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: Selected USB will be erased, please backup your data
        self.subheader = wx.StaticText(self.frame, label="Selected USB will be erased, please backup your data")
        self.subheader.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Label: Select USB
        self.usb_selection_label = wx.StaticText(self.frame, label="Missing drives? Ensure they're 14GB+ and removable")
        self.usb_selection_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.usb_selection_label.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 10
            )
        )
        self.usb_selection_label.Centre(wx.HORIZONTAL)

        i = -15
        available_disks = macos_installer_handler.InstallerCreation().list_disk_to_format()
        if available_disks:
            logging.info("Disks found")
            for disk in available_disks:
                logging.info(f"{disk}: {available_disks[disk]['name']} - {available_disks[disk]['size']}")
                self.usb_selection = wx.Button(self.frame, label=f"{disk} - {available_disks[disk]['name']} - {utilities.human_fmt(available_disks[disk]['size'])}", size=(300, 30))
                i = i + 25
                self.usb_selection.SetPosition(
                    wx.Point(
                        self.usb_selection_label.GetPosition().x,
                        self.usb_selection_label.GetPosition().y + self.usb_selection_label.GetSize().height + i
                    )
                )
                self.usb_selection.Bind(wx.EVT_BUTTON, lambda event, temp=disk: self.format_usb_progress(available_disks[temp]['identifier'], installer_name, installer_path))
                self.usb_selection.Centre(wx.HORIZONTAL)
        else:
            logging.info("No disks found")
            # Label: No Disks Found
            self.usb_selection = wx.StaticText(self.frame, label="No Disks Found")
            self.usb_selection.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, ".AppleSystemUIFont"))
            self.usb_selection.SetPosition(
                # Set Position below header
                wx.Point(
                    self.usb_selection_label.GetPosition().x,
                    self.usb_selection_label.GetPosition().y + self.usb_selection_label.GetSize().height + 10
                )
            )
            self.usb_selection.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.usb_selection.GetPosition().x,
                self.usb_selection.GetPosition().y + self.usb_selection.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def format_usb_progress(self, disk, installer_name, installer_path):
        self.frame.DestroyChildren()
        self.frame.SetSize(500, -1)
        # Header
        self.header = wx.StaticText(self.frame, label=f"Creating Installer: {installer_name}")
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.Centre(wx.HORIZONTAL)

        # Label: Creating macOS Installer
        self.creating_macos_installer_label = wx.StaticText(self.frame, label="Formatting and flashing installer to drive")
        self.creating_macos_installer_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.creating_macos_installer_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.creating_macos_installer_label.Centre(wx.HORIZONTAL)

        # Label: Developer Note: createinstallmedia output currently not implemented
        self.developer_note_label = wx.StaticText(self.frame, label="Developer Note: Creating macOS installers can take 30min+ on slower USB drives.")
        self.developer_note_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.developer_note_label.SetPosition(
            wx.Point(
                self.creating_macos_installer_label.GetPosition().x,
                self.creating_macos_installer_label.GetPosition().y + self.creating_macos_installer_label.GetSize().height + 10
            )
        )
        self.developer_note_label.Centre(wx.HORIZONTAL)

        # We will notify you when it's done. Do not close this window however
        self.developer_note_label_2 = wx.StaticText(self.frame, label="We will notify you when it's done, please do not close this window however")
        self.developer_note_label_2.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.developer_note_label_2.SetPosition(
            wx.Point(
                self.developer_note_label.GetPosition().x,
                self.developer_note_label.GetPosition().y + self.developer_note_label.GetSize().height
            )
        )
        self.developer_note_label_2.Centre(wx.HORIZONTAL)

        # Progress Bar
        max_file_size = 19000  # Best guess for installer + chainloaded packages
        self.progress_bar = wx.Gauge(self.frame, range=max_file_size, size=(-1, 20))
        self.progress_bar.SetPosition(
            wx.Point(
                self.developer_note_label_2.GetPosition().x,
                self.developer_note_label_2.GetPosition().y + self.developer_note_label_2.GetSize().height + 10
            )
        )
        self.progress_bar.SetSize(
            self.frame.GetSize().width - 40,
            20
        )
        self.progress_bar.Centre(wx.HORIZONTAL)

        self.progress_label = wx.StaticText(self.frame, label="Preparing files, beginning shortly...")
        self.progress_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.progress_label.SetPosition(
            wx.Point(
                self.progress_bar.GetPosition().x,
                self.progress_bar.GetPosition().y + self.progress_bar.GetSize().height + 10
            )
        )
        self.progress_label.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.progress_label.GetPosition().x,
                self.progress_label.GetPosition().y + self.progress_label.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
        self.return_to_main_menu.Disable()

        self.frame.Show()

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        wx.GetApp().Yield()
        # Create installer.sh script
        logging.info("- Creating installer.sh script")
        logging.info(f"- Disk: {disk}")
        logging.info(f"- Installer: {installer_path}")

        self.prepare_script_thread = threading.Thread(target=self.prepare_script, args=(installer_path,disk))
        self.prepare_script_thread.start()
        self.progress_bar.Pulse()

        while self.prepare_script_thread.is_alive():
            self.pulse_alternative(self.progress_bar)
            wx.GetApp().Yield()

        if self.prepare_result is True:
            self.progress_label.SetLabel("Bytes Written: 0")
            self.progress_label.Centre(wx.HORIZONTAL)
            logging.info("- Successfully generated creation script")
            logging.info("- Starting creation script as admin")
            wx.GetApp().Yield()
            time.sleep(1)
            disk = disk[5:]
            self.target_disk = disk
            install_thread = threading.Thread(target=self.start_script)
            install_thread.start()
            self.download_thread = threading.Thread(target=self.download_and_unzip_pkg)
            self.download_thread.start()
            default_output = float(utilities.monitor_disk_output(disk))
            self.progress_bar.SetValue(0)
            while True:
                time.sleep(0.1)
                output = float(utilities.monitor_disk_output(disk))
                bytes_written = output - default_output
                if install_thread.is_alive():
                    self.progress_bar.SetValue(int(bytes_written))
                    self.progress_label.SetLabel(f"Bytes Written: {round(bytes_written, 2)}MB")
                    wx.GetApp().Yield()
                else:
                    break
            self.progress_bar.SetValue(max_file_size)
            self.progress_label.SetLabel(f"Finished Running Installer Creation Script")
            self.progress_label.Centre(wx.HORIZONTAL)
            if self.finished_cim_process is True:
                self.finished_cim_process = False
                # Only prompt user with option to install OC to disk if
                # the model is supported.
                if (
                    (
                        self.constants.allow_oc_everywhere is False and \
                        self.constants.custom_model is None and \
                        self.computer.real_model not in model_array.SupportedSMBIOS
                    ) or (
                        self.constants.custom_model is None and \
                        self.constants.host_is_hackintosh is True
                    )
                ):
                    popup_message = wx.MessageDialog(self.frame, "Successfully created a macOS installer!", "Success", wx.OK)
                    popup_message.ShowModal()
                else:
                    self.dialog = wx.MessageDialog(
                        parent=self.frame,
                        message="Would you like to continue and Install OpenCore to this disk?",
                        caption="Successfully created the macOS installer!",
                        style=wx.YES_NO | wx.ICON_QUESTION
                    )
                    self.dialog.SetYesNoLabels("Install OpenCore to disk", "Skip")
                    response = self.dialog.ShowModal()
                    if response == wx.ID_YES:
                        self.constants.start_build_install = True
                        self.build_install_menu()
        else:
            logging.info("- Failed to create installer script")
            self.progress_label.SetLabel("Failed to copy files to tmp directory")
            self.progress_label.Centre(wx.HORIZONTAL)
            popup_message = wx.MessageDialog(self.frame, "Failed to prepare the base files for installer creation.\n\nPlease ensure you have 20GB~ free on-disk before starting to ensure the installer has enough room to work.", "Error", wx.OK)
            popup_message.ShowModal()
        self.return_to_main_menu.Enable()

    def prepare_script(self, installer_path, disk):
        self.prepare_result = macos_installer_handler.InstallerCreation().generate_installer_creation_script(self.constants.payload_path, installer_path, disk)

    def start_script(self):
        utilities.disable_sleep_while_running()
        args   = [self.constants.oclp_helper_path, "/bin/sh", self.constants.installer_sh_path]
        result = subprocess.run(args, capture_output=True, text=True)
        output = result.stdout
        error  = result.stderr if result.stderr else ""

        if "Install media now available at" in output:
            logging.info("- Successfully created macOS installer")
            while self.download_thread.is_alive():
                # wait for download_thread to finish
                # though highly unlikely this thread is still alive (flashing an Installer will take a while)
                time.sleep(0.1)
            logging.info("- Installing Root Patcher to drive")
            self.install_installer_pkg(self.target_disk)
            self.finished_cim_process = True
        else:
            logging.info("- Failed to create macOS installer")
            popup = wx.MessageDialog(self.frame, f"Failed to create macOS installer\n\nOutput: {output}\n\nError: {error}", "Error", wx.OK | wx.ICON_ERROR)
            popup.ShowModal()
        utilities.enable_sleep_after_running()


    def download_and_unzip_pkg(self):
        # Function's main goal is to grab the correct AutoPkg-Assets.pkg and unzip it
        # Note the following:
        #   - When running a release build, pull from Github's release page with the same versioning
        #   - When running from source/unable to find on Github, use the nightly.link variant
        #   - If nightly also fails, fall back to the manually uploaded variant
        link = self.constants.installer_pkg_url
        if network_handler.NetworkUtilities(link).validate_link() is False:
            logging.info("- Stock Install.pkg is missing on Github, falling back to Nightly")
            link = self.constants.installer_pkg_url_nightly

        if link.endswith(".zip"):
            path = self.constants.installer_pkg_zip_path
        else:
            path = self.constants.installer_pkg_path

        autopkg_download = network_handler.DownloadObject(link, path)
        autopkg_download.download(spawn_thread=False)

        if autopkg_download.download_complete is False:
            logging.warning("- Failed to download Install.pkg")
            logging.warning(autopkg_download.error_msg)
            return

        # Download thread will re-enable Idle Sleep after downloading
        utilities.disable_sleep_while_running()
        if not str(path).endswith(".zip"):
            return
        if Path(self.constants.installer_pkg_path).exists():
            subprocess.run(["rm", self.constants.installer_pkg_path])
        subprocess.run(["ditto", "-V", "-x", "-k", "--sequesterRsrc", "--rsrc", self.constants.installer_pkg_zip_path, self.constants.payload_path])


    def _kdk_chainload(self, build: str, version: str, download_dir: str):
        """
        Download the correct KDK to be chainloaded in the macOS installer

        Parameters
            build (str): The build number of the macOS installer (e.g. 20A5343j)
            version (str): The version of the macOS installer (e.g. 11.0.1)
        """

        kdk_dmg_path = Path(download_dir) / "KDK.dmg"
        kdk_pkg_path = Path(download_dir) / "KDK.pkg"

        if kdk_dmg_path.exists():
            kdk_dmg_path.unlink()
        if kdk_pkg_path.exists():
            kdk_pkg_path.unlink()

        logging.info("- Initiating KDK download")
        logging.info(f"  - Build: {build}")
        logging.info(f"  - Version: {version}")
        logging.info(f"  - Working Directory: {download_dir}")

        kdk_obj = kdk_handler.KernelDebugKitObject(self.constants, build, version, ignore_installed=True)
        if kdk_obj.success is False:
            logging.info("- Failed to retrieve KDK")
            logging.info(kdk_obj.error_msg)
            return

        kdk_download_obj = kdk_obj.retrieve_download(override_path=kdk_dmg_path)
        if kdk_download_obj is None:
            logging.info("- Failed to retrieve KDK")
            logging.info(kdk_obj.error_msg)

        # Check remaining disk space before downloading
        space = utilities.get_free_space(download_dir)
        if space < (kdk_obj.kdk_url_expected_size * 2):
            logging.info("- Not enough disk space to download and install KDK")
            logging.info(f"- Attempting to download locally first")
            if space < kdk_obj.kdk_url_expected_size:
                logging.info("- Not enough disk space to install KDK, skipping")
                return
            # Ideally we'd download the KDK onto the disk to display progress in the UI
            # However we'll just download to our temp directory and move it to the target disk
            kdk_dmg_path = self.constants.kdk_download_path

        kdk_download_obj.download(spawn_thread=False)
        if kdk_download_obj.download_complete is False:
            logging.info("- Failed to download KDK")
            logging.info(kdk_download_obj.error_msg)
            return

        if not kdk_dmg_path.exists():
            logging.info(f"- KDK missing: {kdk_dmg_path}")
            return

        # Now that we have a KDK, extract it to get the pkg
        with tempfile.TemporaryDirectory() as mount_point:
            logging.info("- Mounting KDK")
            result = subprocess.run(["hdiutil", "attach", kdk_dmg_path, "-mountpoint", mount_point, "-nobrowse"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.info("- Failed to mount KDK")
                logging.info(result.stdout.decode("utf-8"))
                return

            logging.info("- Copying KDK")
            subprocess.run(["cp", "-r", f"{mount_point}/KernelDebugKit.pkg", kdk_pkg_path])

            logging.info("- Unmounting KDK")
            result = subprocess.run(["hdiutil", "detach", mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.info("- Failed to unmount KDK")
                logging.info(result.stdout.decode("utf-8"))
                return

        logging.info("- Removing KDK Disk Image")
        kdk_dmg_path.unlink()


    def install_installer_pkg(self, disk):
        disk = disk + "s2" # ESP sits at 1, and we know macOS will have created the main partition at 2

        if not Path(self.constants.installer_pkg_path).exists():
            return

        path = utilities.grab_mount_point_from_disk(disk)
        if not Path(path + "/System/Library/CoreServices/SystemVersion.plist").exists():
            return

        os_version = plistlib.load(Path(path + "/System/Library/CoreServices/SystemVersion.plist").open("rb"))
        kernel_version = os_data.os_conversion.os_to_kernel(os_version["ProductVersion"])
        if int(kernel_version) < os_data.os_data.big_sur:
            logging.info("- Installer unsupported, requires Big Sur or newer")
            return

        subprocess.run(["mkdir", "-p", f"{path}/Library/Packages/"])
        subprocess.run(["cp", "-r", self.constants.installer_pkg_path, f"{path}/Library/Packages/"])

        self._kdk_chainload(os_version["ProductBuildVersion"], os_version["ProductVersion"], Path(path + "/Library/Packages/"))


    def settings_menu(self, event=None):
        # Define Menu
        # - Header: Settings
        # - Dropdown: Model
        # - Checkboxes:
        #   - Verbose
        #   - Kext Debug
        #   - OpenCore Debug
        #   - SIP
        #   - SecureBootModel
        #   - Show Boot Picker
        # - Buttons:
        #   - Developer Settings
        # - Return to Main Menu

        # Create wxDialog and have Settings menu be WindowModal

        # Create Menu
        self.reset_frame_modal()

        self.frame_modal.SetSize(wx.Size(self.WINDOW_SETTINGS_WIDTH, self.WINDOW_SETTINGS_HEIGHT))
        self.frame_modal.SetTitle("Settings")

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Settings", pos=wx.Point(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.SetPosition((-1, 5))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame_modal, label="Changing settings here require you")
        self.subheader.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)
        self.subheader2 = wx.StaticText(self.frame_modal, label="to run 'Build and Install OpenCore'")
        self.subheader2.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.subheader2.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height
            )
        )
        self.subheader2.Centre(wx.HORIZONTAL)
        self.subheader3 = wx.StaticText(self.frame_modal, label="then reboot for changes to be applied")
        self.subheader3.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ".AppleSystemUIFont"))
        self.subheader3.SetPosition(
            wx.Point(
                self.subheader2.GetPosition().x,
                self.subheader2.GetPosition().y + self.subheader2.GetSize().height
            )
        )
        self.subheader3.Centre(wx.HORIZONTAL)

        # Dropdown
        self.dropdown_model = wx.Choice(self.frame_modal)
        for model in model_array.SupportedSMBIOS:
            self.dropdown_model.Append(model)
        if self.computer.real_model not in self.dropdown_model.GetItems():
            # In the event an unsupported model is loaded, add it to the dropdown
            # Supported situation: If user wants to run on native model
            self.dropdown_model.Append(self.computer.real_model)
        self.dropdown_model.SetSelection(self.dropdown_model.GetItems().index(self.constants.custom_model or self.computer.real_model))
        self.dropdown_model.SetPosition(
            wx.Point(
                self.subheader3.GetPosition().x,
                self.subheader3.GetPosition().y + self.subheader3.GetSize().height + 10
            )
        )
        # Set size to largest item
        self.dropdown_model.SetSize(
            wx.Size(
                self.dropdown_model.GetBestSize().width,
                self.dropdown_model.GetBestSize().height
            )
        )
        self.dropdown_model.Bind(wx.EVT_CHOICE, self.model_choice_click)
        self.dropdown_model.Centre(wx.HORIZONTAL)
        self.dropdown_model.ToolTip = wx.ToolTip("Select the model you want to build for")

        # Checkboxes
        # Checkbox: Allow native models
        self.checkbox_allow_native_models = wx.CheckBox(self.frame_modal, label="Allow native models")
        self.checkbox_allow_native_models.SetValue(self.constants.allow_oc_everywhere)
        self.checkbox_allow_native_models.SetPosition(wx.Point(self.dropdown_model.GetPosition().x, self.dropdown_model.GetPosition().y + self.dropdown_model.GetSize().height + 10))
        self.checkbox_allow_native_models.Bind(wx.EVT_CHECKBOX, self.allow_native_models_click)
        self.checkbox_allow_native_models.ToolTip = wx.ToolTip("""Select to allow OpenCore to be installed on native models\nGenerally used for enabling OS features Apple locks out of native Macs\nie. AirPlay to Mac, Sidecar.""")

        # Checkbox: Verbose
        self.verbose_checkbox = wx.CheckBox(self.frame_modal, label="Verbose")
        self.verbose_checkbox.SetValue(self.constants.verbose_debug)
        self.verbose_checkbox.SetPosition(wx.Point(self.checkbox_allow_native_models.GetPosition().x, self.checkbox_allow_native_models.GetPosition().y + self.checkbox_allow_native_models.GetSize().height))
        self.verbose_checkbox.Bind(wx.EVT_CHECKBOX, self.verbose_checkbox_click)
        self.verbose_checkbox.ToolTip = wx.ToolTip("""Add -v (verbose) to boot-args during build""")

        # Checkbox: Kext Debug
        self.kext_checkbox = wx.CheckBox(self.frame_modal, label="Kext Debug")
        self.kext_checkbox.SetValue(self.constants.kext_debug)
        self.kext_checkbox.SetPosition(wx.Point(self.verbose_checkbox.GetPosition().x , self.verbose_checkbox.GetPosition().y + self.verbose_checkbox.GetSize().height))
        self.kext_checkbox.Bind(wx.EVT_CHECKBOX, self.kext_checkbox_click)
        self.kext_checkbox.ToolTip = wx.ToolTip("""Enables additional kext logging, including expanded message buffer""")

        # Checkbox: OpenCore Debug
        self.opencore_checkbox = wx.CheckBox(self.frame_modal, label="OpenCore Debug")
        self.opencore_checkbox.SetValue(self.constants.opencore_debug)
        self.opencore_checkbox.SetPosition(wx.Point(self.kext_checkbox.GetPosition().x , self.kext_checkbox.GetPosition().y + self.kext_checkbox.GetSize().height))
        self.opencore_checkbox.Bind(wx.EVT_CHECKBOX, self.oc_checkbox_click)
        self.opencore_checkbox.ToolTip = wx.ToolTip("""Enables OpenCore logging, can heavily impact boot times""")

        # Checkbox: SecureBootModel
        self.secureboot_checkbox = wx.CheckBox(self.frame_modal, label="SecureBootModel")
        self.secureboot_checkbox.SetValue(self.constants.secure_status)
        self.secureboot_checkbox.SetPosition(wx.Point(self.opencore_checkbox.GetPosition().x , self.opencore_checkbox.GetPosition().y + self.opencore_checkbox.GetSize().height))
        self.secureboot_checkbox.Bind(wx.EVT_CHECKBOX, self.secureboot_checkbox_click)
        self.secureboot_checkbox.ToolTip = wx.ToolTip("""Sets SecureBootModel, useful for models spoofing T2 Macs to get OTA updates""")

        # Checkbox: Show Boot Picker
        self.bootpicker_checkbox = wx.CheckBox(self.frame_modal, label="Show Boot Picker")
        self.bootpicker_checkbox.SetValue(self.constants.showpicker)
        self.bootpicker_checkbox.SetPosition(wx.Point(self.secureboot_checkbox.GetPosition().x , self.secureboot_checkbox.GetPosition().y + self.secureboot_checkbox.GetSize().height))
        self.bootpicker_checkbox.Bind(wx.EVT_CHECKBOX, self.show_picker_checkbox_click)
        self.bootpicker_checkbox.ToolTip = wx.ToolTip("""Shows OpenCore's Boot Picker on machine start\nToggling this off will hide the picker, and only load when holding either Option or Escape""")

        # Buttons

        # Button: SIP Settings
        if self.constants.custom_sip_value:
            sip_string = "Custom"
        elif self.constants.sip_status:
            sip_string = "Enabled"
        else:
            sip_string = "Lowered"
        self.sip_button = wx.Button(self.frame_modal, label=f"SIP Settings ({sip_string})",  size=(155,30))
        self.sip_button.SetPosition(wx.Point(self.bootpicker_checkbox.GetPosition().x , self.bootpicker_checkbox.GetPosition().y + self.bootpicker_checkbox.GetSize().height + 10))
        self.sip_button.Bind(wx.EVT_BUTTON, self.sip_config_menu)
        self.sip_button.Center(wx.HORIZONTAL)

        # Button: SMBIOS Settings
        self.smbios_button = wx.Button(self.frame_modal, label="SMBIOS Settings",  size=(155,30))
        self.smbios_button.SetPosition(wx.Point(self.sip_button.GetPosition().x , self.sip_button.GetPosition().y + self.sip_button.GetSize().height))
        self.smbios_button.Bind(wx.EVT_BUTTON, self.smbios_settings_menu)
        self.smbios_button.Center(wx.HORIZONTAL)

        # Button: Misc Settings
        self.misc_button = wx.Button(self.frame_modal, label="Misc Settings",  size=(155,30))
        self.misc_button.SetPosition(wx.Point(self.smbios_button.GetPosition().x , self.smbios_button.GetPosition().y + self.smbios_button.GetSize().height))
        self.misc_button.Bind(wx.EVT_BUTTON, self.misc_settings_menu)
        self.misc_button.Center(wx.HORIZONTAL)

        # Button: non-Metal Settings
        self.nonmetal_button = wx.Button(self.frame_modal, label="Non-Metal Settings",  size=(155,30))
        self.nonmetal_button.SetPosition(wx.Point(self.misc_button.GetPosition().x , self.misc_button.GetPosition().y + self.misc_button.GetSize().height))
        self.nonmetal_button.Bind(wx.EVT_BUTTON, self.non_metal_config_menu)
        self.nonmetal_button.Center(wx.HORIZONTAL)

        # Button: Developer Settings
        self.miscellaneous_button = wx.Button(self.frame_modal, label="Developer Settings",  size=(155,30))
        self.miscellaneous_button.SetPosition(wx.Point(self.nonmetal_button.GetPosition().x , self.nonmetal_button.GetPosition().y + self.nonmetal_button.GetSize().height))
        self.miscellaneous_button.Bind(wx.EVT_BUTTON, self.dev_settings_menu)
        self.miscellaneous_button.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame_modal, label="Return to Main Menu", size=(155,30))
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.miscellaneous_button.GetPosition().x,
                self.miscellaneous_button.GetPosition().y + self.miscellaneous_button.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        # Set frame size to below return_to_main_menu button
        self.frame_modal.SetSize(wx.Size(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()

    def model_choice_click(self, event=None):
        user_choice = self.dropdown_model.GetStringSelection()
        if user_choice == self.computer.real_model:
            logging.info(f"Using Real Model: {user_choice}")
            self.constants.custom_model = None
            defaults.GenerateDefaults(self.computer.real_model, True, self.constants)
        else:
            logging.info(f"Using Custom Model: {user_choice}")
            self.constants.custom_model = user_choice
            defaults.GenerateDefaults(self.constants.custom_model, False, self.constants)
        # Reload Settings
        self.settings_menu(None)

    def allow_native_models_click(self, event=None):
        if self.checkbox_allow_native_models.GetValue():
            # Throw a prompt warning about this
            dlg = wx.MessageDialog(self.frame_modal, "This option should only be used if your Mac natively supports the OSes you wish to run.\n\nIf you are currently running an unsupported OS, this option will break booting. Only toggle for enabling OS features on a native Mac.\n\nAre you certain you want to continue?", "Warning", wx.YES_NO | wx.ICON_WARNING)
            if dlg.ShowModal() == wx.ID_NO:
                self.checkbox_allow_native_models.SetValue(False)
                return
            # If the system is running an unsupported OS, throw a second warning
            if self.constants.computer.real_model in smbios_data.smbios_dictionary:
                if self.constants.detected_os > smbios_data.smbios_dictionary[self.constants.computer.real_model]["Max OS Supported"]:
                    chassis_type = "aluminum"
                    if self.constants.computer.real_model in ["MacBook4,1", "MacBook5,2", "MacBook6,1", "MacBook7,1"]:
                        chassis_type = "plastic"
                    dlg = wx.MessageDialog(self.frame_modal, f"This model, {self.constants.computer.real_model}, does not natively support macOS {os_data.os_conversion.kernel_to_os(self.constants.detected_os)}, {os_data.os_conversion.convert_kernel_to_marketing_name(self.constants.detected_os)}. The last native OS was macOS {os_data.os_conversion.kernel_to_os(smbios_data.smbios_dictionary[self.constants.computer.real_model]['Max OS Supported'])}, {os_data.os_conversion.convert_kernel_to_marketing_name(smbios_data.smbios_dictionary[self.constants.computer.real_model]['Max OS Supported'])}\n\nToggling this option will break booting on this OS. Are you absolutely certain this is desired?\n\nYou may end up with a nice {chassis_type} brick 🧱", "Are you certain?", wx.YES_NO | wx.ICON_WARNING)
                    if dlg.ShowModal() == wx.ID_NO:
                        self.checkbox_allow_native_models.SetValue(False)
                        return
            logging.info("Allow Native Models")
            self.constants.allow_oc_everywhere = True
            self.constants.serial_settings = "None"
        else:
            logging.info("Disallow Native Models")
            self.constants.allow_oc_everywhere = False
            self.constants.serial_settings = "Minimal"

    def verbose_checkbox_click(self, event=None):
        if self.verbose_checkbox.GetValue():
            logging.info("Verbose mode enabled")
            self.constants.verbose_debug = True
        else:
            logging.info("Verbose mode disabled")
            self.constants.verbose_debug = False

    def kext_checkbox_click(self, event=None):
        if self.kext_checkbox.GetValue():
            logging.info("Kext mode enabled")
            self.constants.kext_debug = True
            self.constants.kext_variant = "DEBUG"
        else:
            logging.info("Kext mode disabled")
            self.constants.kext_debug = False
            self.constants.kext_variant = "RELEASE"

    def oc_checkbox_click(self, event=None):
        if self.opencore_checkbox.GetValue():
            logging.info("OC mode enabled")
            self.constants.opencore_debug = True
            self.constants.opencore_build = "DEBUG"
        else:
            logging.info("OC mode disabled")
            self.constants.opencore_debug = False
            self.constants.opencore_build = "RELEASE"

    def sip_checkbox_click(self, event=None):
        if self.sip_checkbox.GetValue():
            logging.info("SIP mode enabled")
            self.constants.sip_status = True
        else:
            logging.info("SIP mode disabled")
            self.constants.sip_status = False

    def secureboot_checkbox_click(self, event=None):
        if self.secureboot_checkbox.GetValue():
            logging.info("SecureBoot mode enabled")
            self.constants.secure_status = True
        else:
            logging.info("SecureBoot mode disabled")
            self.constants.secure_status = False

    def show_picker_checkbox_click(self, event=None):
        if self.bootpicker_checkbox.GetValue():
            logging.info("Show Picker mode enabled")
            self.constants.showpicker = True
        else:
            logging.info("Show Picker mode disabled")
            self.constants.showpicker = False

    def dev_settings_menu(self, event=None):
        self.reset_frame_modal()

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Developer Settings", style=wx.ALIGN_CENTRE, pos=wx.Point(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.SetPosition(wx.Point(0, 10))
        self.header.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: If unfamiliar with the following settings, please do not change them.
        self.subheader = wx.StaticText(self.frame_modal, label="Do not change if unfamiliar", style=wx.ALIGN_CENTRE)
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(wx.Point(0, self.header.GetPosition().y + self.header.GetSize().height))
        self.subheader.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.subheader.Centre(wx.HORIZONTAL)

        # Label: Set GPU Model for MXM iMacs
        self.label_model = wx.StaticText(self.frame_modal, label="Set GPU Model for MXM iMacs:", style=wx.ALIGN_CENTRE)
        self.label_model.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.label_model.SetPosition(wx.Point(0, self.subheader.GetPosition().y + self.subheader.GetSize().height + 2))
        self.label_model.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.label_model.Centre(wx.HORIZONTAL)

        # Dropdown: GPU Model
        self.gpu_dropdown = wx.Choice(self.frame_modal)
        for gpu in ["None", "Nvidia Kepler", "AMD GCN", "AMD Polaris", "AMD Navi", "AMD Lexa"]:
            self.gpu_dropdown.Append(gpu)
        self.gpu_dropdown.SetSelection(0)
        self.gpu_dropdown.SetPosition(wx.Point(
            self.label_model.GetPosition().x,
            int(self.label_model.GetPosition().y + self.label_model.GetSize().height / 1.5)))
        self.gpu_dropdown.Bind(wx.EVT_CHOICE, self.gpu_selection_click)
        self.gpu_dropdown.Centre(wx.HORIZONTAL)
        self.gpu_dropdown.SetToolTip(wx.ToolTip("Configures MXM GPU Vendor logic on pre-built models\nIf you are not using MXM iMacs, please leave this setting as is."))
        models = ["iMac9,1", "iMac10,1", "iMac11,1", "iMac11,2", "iMac11,3", "iMac12,1", "iMac12,2"]
        if (not self.constants.custom_model and self.computer.real_model not in models) or (self.constants.custom_model and self.constants.custom_model not in models):
            self.gpu_dropdown.Disable()

        # OpenCore Picker Timeout (using wxSpinCtrl)
        # Label: Picker Timeout
        self.label_timeout = wx.StaticText(self.frame_modal, label="Picker Timeout (seconds):", style=wx.ALIGN_CENTRE)
        self.label_timeout.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.label_timeout.SetPosition(wx.Point(0, self.gpu_dropdown.GetPosition().y + self.gpu_dropdown.GetSize().height + 2))
        self.label_timeout.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.label_timeout.Centre(wx.HORIZONTAL)

        # Picker Timeout
        self.timeout_spinner = wx.SpinCtrl(self.frame_modal, value=f"{self.constants.oc_timeout}", min=0, max=60)
        self.timeout_spinner.SetPosition(wx.Point(
            self.label_timeout.GetPosition().x,
            int(self.label_timeout.GetPosition().y + self.label_timeout.GetSize().height / 2)))
        self.timeout_spinner.Bind(wx.EVT_SPINCTRL, self.timeout_spinner_click)
        self.timeout_spinner.Centre(wx.HORIZONTAL)

        # AMD GOP Injection
        self.set_amd_gop_injection = wx.CheckBox(self.frame_modal, label="AMD GOP Injection")
        self.set_amd_gop_injection.SetPosition(wx.Point(
            30,
            self.timeout_spinner.GetPosition().y + self.timeout_spinner.GetSize().height + 5))
        self.set_amd_gop_injection.SetValue(self.constants.amd_gop_injection)
        self.set_amd_gop_injection.Bind(wx.EVT_CHECKBOX, self.amd_gop_injection_checkbox_click)
        models = ["iMac9,1", "iMac10,1", "iMac11,1", "iMac11,2", "iMac11,3", "iMac12,1", "iMac12,2", "MacPro3,1", "MacPro4,1", "MacPro5,1", "Xserve2,1", "Xserve3,1"]
        if (not self.constants.custom_model and self.computer.real_model not in models) or (self.constants.custom_model and self.constants.custom_model not in models):
            self.set_amd_gop_injection.Disable()

        # Nvidia Kepler GOP injection
        self.set_nvidia_kepler_gop_injection = wx.CheckBox(self.frame_modal, label="Nvidia Kepler GOP Injection")
        self.set_nvidia_kepler_gop_injection.SetPosition(wx.Point(
            self.set_amd_gop_injection.GetPosition().x,
            self.set_amd_gop_injection.GetPosition().y + self.set_amd_gop_injection.GetSize().height))
        self.set_nvidia_kepler_gop_injection.SetValue(self.constants.nvidia_kepler_gop_injection)
        self.set_nvidia_kepler_gop_injection.Bind(wx.EVT_CHECKBOX, self.nvidia_kepler_gop_injection_checkbox_click)
        if (not self.constants.custom_model and self.computer.real_model not in models) or (self.constants.custom_model and self.constants.custom_model not in models):
            self.set_nvidia_kepler_gop_injection.Disable()

        # Disable Thunderbolt
        self.disable_thunderbolt_checkbox = wx.CheckBox(self.frame_modal, label="Disable Thunderbolt")
        self.disable_thunderbolt_checkbox.SetValue(self.constants.disable_tb)
        self.disable_thunderbolt_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_tb_click)
        self.disable_thunderbolt_checkbox.SetPosition(wx.Point(
            self.set_nvidia_kepler_gop_injection.GetPosition().x,
            self.set_nvidia_kepler_gop_injection.GetPosition().y + self.set_nvidia_kepler_gop_injection.GetSize().height))
        self.disable_thunderbolt_checkbox.SetToolTip(wx.ToolTip("Disables Thunderbolt support on MacBookPro11,x\nMainly applicable for systems that cannot boot with Thunderbolt enabled"))
        if not self.constants.custom_model and not self.computer.real_model.startswith("MacBookPro11"):
            self.disable_thunderbolt_checkbox.Disable()
        # Set TeraScale 2 Accel
        self.set_terascale_accel_checkbox = wx.CheckBox(self.frame_modal, label="Set TeraScale 2 Accel")
        self.set_terascale_accel_checkbox.SetValue(self.constants.allow_ts2_accel)
        self.set_terascale_accel_checkbox.Bind(wx.EVT_CHECKBOX, self.ts2_accel_click)
        self.set_terascale_accel_checkbox.SetPosition(wx.Point(
            self.disable_thunderbolt_checkbox.GetPosition().x,
            self.disable_thunderbolt_checkbox.GetPosition().y + self.disable_thunderbolt_checkbox.GetSize().height))
        self.set_terascale_accel_checkbox.SetToolTip(wx.ToolTip("This option will determine whether TeraScale 2 acceleration is available during Root Volume patching.\nOnly applicable if your system has a AMD TeraScale 2 GPU (ie. MacBookPro8,2/3)"))
        if self.computer.real_model not in ["MacBookPro8,2", "MacBookPro8,3"]:
            self.set_terascale_accel_checkbox.Disable()
            self.set_terascale_accel_checkbox.SetValue(False)

        # Windows GMUX
        self.windows_gmux_checkbox = wx.CheckBox(self.frame_modal, label="Windows GMUX")
        self.windows_gmux_checkbox.SetValue(self.constants.dGPU_switch)
        self.windows_gmux_checkbox.Bind(wx.EVT_CHECKBOX, self.windows_gmux_click)
        self.windows_gmux_checkbox.SetPosition(wx.Point(
            self.set_terascale_accel_checkbox.GetPosition().x,
            self.set_terascale_accel_checkbox.GetPosition().y + self.set_terascale_accel_checkbox.GetSize().height))
        self.windows_gmux_checkbox.SetToolTip(wx.ToolTip("Enable this option to allow usage of the hardware GMUX to switch between Intel and Nvidia/AMD GPUs in Windows."))

        # Hibernation Workaround
        self.hibernation_checkbox = wx.CheckBox(self.frame_modal, label="Hibernation Workaround")
        self.hibernation_checkbox.SetValue(self.constants.disable_connectdrivers)
        self.hibernation_checkbox.Bind(wx.EVT_CHECKBOX, self.hibernation_click)
        self.hibernation_checkbox.SetPosition(wx.Point(
            self.windows_gmux_checkbox.GetPosition().x,
            self.windows_gmux_checkbox.GetPosition().y + self.windows_gmux_checkbox.GetSize().height))
        self.hibernation_checkbox.SetToolTip(wx.ToolTip("This will disable the ConnectDrivers in OpenCore\nRecommended to toggle if your machine is having issues with hibernation.\nMainly applicable for MacBookPro9,1 and MacBookPro10,1"))

        # Disable Battery Throttling
        self.disable_battery_throttling_checkbox = wx.CheckBox(self.frame_modal, label="Disable Firmware Throttling")
        self.disable_battery_throttling_checkbox.SetValue(self.constants.disable_msr_power_ctl)
        self.disable_battery_throttling_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_battery_throttling_click)
        self.disable_battery_throttling_checkbox.SetPosition(wx.Point(
            self.hibernation_checkbox.GetPosition().x,
            self.hibernation_checkbox.GetPosition().y + self.hibernation_checkbox.GetSize().height))
        self.disable_battery_throttling_checkbox.SetToolTip(wx.ToolTip("This will forcefully disable MSR Power Control on Arrandale and newer Macs\nMainly applicable for systems with severe throttling due to missing battery or display"))

        # Disable XCPM
        self.disable_xcpm_checkbox = wx.CheckBox(self.frame_modal, label="Disable XCPM")
        self.disable_xcpm_checkbox.SetValue(self.constants.disable_xcpm)
        self.disable_xcpm_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_xcpm_click)
        self.disable_xcpm_checkbox.SetPosition(wx.Point(
            self.disable_battery_throttling_checkbox.GetPosition().x,
            self.disable_battery_throttling_checkbox.GetPosition().y + self.disable_battery_throttling_checkbox.GetSize().height))
        self.disable_xcpm_checkbox.SetToolTip(wx.ToolTip("This will forcefully disable XCPM on Ivy Bridge EP and newer Macs\nMainly applicable for systems with severe throttling due to missing battery or display"))

        # Software Demux
        self.software_demux_checkbox = wx.CheckBox(self.frame_modal, label="Software Demux")
        self.software_demux_checkbox.SetValue(self.constants.software_demux)
        self.software_demux_checkbox.Bind(wx.EVT_CHECKBOX, self.software_demux_click)
        self.software_demux_checkbox.SetPosition(wx.Point(
            self.disable_xcpm_checkbox.GetPosition().x,
            self.disable_xcpm_checkbox.GetPosition().y + self.disable_xcpm_checkbox.GetSize().height))
        self.software_demux_checkbox.SetToolTip(wx.ToolTip("This will force a software based demux on MacBookPro8,2/3 aiding for better battery life\nThis will require the dGPU to be disabled via NVRAM"))
        if not self.constants.custom_model and self.computer.real_model not in ["MacBookPro8,2", "MacBookPro8,3"]:
            self.software_demux_checkbox.Disable()

        # Disable CPUFriend
        self.disable_cpu_friend_checkbox = wx.CheckBox(self.frame_modal, label="Disable CPUFriend")
        self.disable_cpu_friend_checkbox.SetValue(self.constants.disallow_cpufriend)
        self.disable_cpu_friend_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_cpu_friend_click)
        self.disable_cpu_friend_checkbox.SetPosition(wx.Point(
            self.software_demux_checkbox.GetPosition().x,
            self.software_demux_checkbox.GetPosition().y + self.software_demux_checkbox.GetSize().height))
        self.disable_cpu_friend_checkbox.SetToolTip(wx.ToolTip("This will disable CPUFriend on your system when using Minimal or higher SMBIOS spoofing.\nMainly applicable for older iMacs (2007-9) that wish to disable CPU throttling"))
        if self.constants.serial_settings == "None":
            self.disable_cpu_friend_checkbox.Disable()

        # AppleALC Usage
        self.apple_alc_checkbox = wx.CheckBox(self.frame_modal, label="AppleALC Usage")
        self.apple_alc_checkbox.SetValue(self.constants.set_alc_usage)
        self.apple_alc_checkbox.Bind(wx.EVT_CHECKBOX, self.apple_alc_click)
        self.apple_alc_checkbox.SetPosition(wx.Point(
            self.disable_cpu_friend_checkbox.GetPosition().x,
            self.disable_cpu_friend_checkbox.GetPosition().y + self.disable_cpu_friend_checkbox.GetSize().height))
        self.apple_alc_checkbox.SetToolTip(wx.ToolTip("This will set whether AppleALC is allowed to be used during config building.\nMainly applicable for MacPro3,1s that do not have boot screen support, thus preventing AppleALC from working."))

        # Set WriteFlash
        self.set_writeflash_checkbox = wx.CheckBox(self.frame_modal, label="Set NVRAM WriteFlash")
        self.set_writeflash_checkbox.SetValue(self.constants.nvram_write)
        self.set_writeflash_checkbox.Bind(wx.EVT_CHECKBOX, self.set_writeflash_click)
        self.set_writeflash_checkbox.SetPosition(wx.Point(
            self.apple_alc_checkbox.GetPosition().x,
            self.apple_alc_checkbox.GetPosition().y + self.apple_alc_checkbox.GetSize().height))
        self.set_writeflash_checkbox.SetToolTip(wx.ToolTip("This will set whether OpenCore is allowed to write to hardware NVRAM.\nDisable this option if your system has degraded or fragile NVRAM."))
        # Set Enhanced 3rd Party SSD
        self.set_enhanced_3rd_party_ssd_checkbox = wx.CheckBox(self.frame_modal, label="Enhanced SSD Support")
        self.set_enhanced_3rd_party_ssd_checkbox.SetValue(self.constants.allow_3rd_party_drives)
        self.set_enhanced_3rd_party_ssd_checkbox.Bind(wx.EVT_CHECKBOX, self.set_enhanced_3rd_party_ssd_click)
        self.set_enhanced_3rd_party_ssd_checkbox.SetPosition(wx.Point(
            self.set_writeflash_checkbox.GetPosition().x,
            self.set_writeflash_checkbox.GetPosition().y + self.set_writeflash_checkbox.GetSize().height))
        self.set_enhanced_3rd_party_ssd_checkbox.SetToolTip(wx.ToolTip("This will set whether OpenCore is allowed to force Apple Vendor on 3rd Party SATA SSDs\nSome benefits from this patch include better SSD performance, TRIM support and hibernation support.\nDisable this option if your SSD does not support TRIM correctly"))
        if self.computer.third_party_sata_ssd is False and not self.constants.custom_model:
            self.set_enhanced_3rd_party_ssd_checkbox.Disable()

        # Disable Library Validation
        self.disable_library_validation_checkbox = wx.CheckBox(self.frame_modal, label="Disable Library Validation")
        self.disable_library_validation_checkbox.SetValue(self.constants.disable_cs_lv)
        self.disable_library_validation_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_library_validation_click)
        self.disable_library_validation_checkbox.SetPosition(wx.Point(
            self.set_enhanced_3rd_party_ssd_checkbox.GetPosition().x,
            self.set_enhanced_3rd_party_ssd_checkbox.GetPosition().y + self.set_enhanced_3rd_party_ssd_checkbox.GetSize().height
        ))

        # Disable AMFI
        self.disable_amfi_checkbox = wx.CheckBox(self.frame_modal, label="Disable AMFI")
        self.disable_amfi_checkbox.SetValue(self.constants.disable_amfi)
        self.disable_amfi_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_amfi_click)
        self.disable_amfi_checkbox.SetPosition(wx.Point(
            self.disable_library_validation_checkbox.GetPosition().x,
            self.disable_library_validation_checkbox.GetPosition().y + self.disable_library_validation_checkbox.GetSize().height
        ))
        if self.constants.disable_cs_lv is False:
            self.disable_amfi_checkbox.Disable()


        # Delete Unused KDKs during patching
        self.delete_unused_kdks_checkbox = wx.CheckBox(self.frame_modal, label="Delete Unused KDKs")
        self.delete_unused_kdks_checkbox.SetValue(self.constants.should_nuke_kdks)
        self.delete_unused_kdks_checkbox.Bind(wx.EVT_CHECKBOX, self.delete_unused_kdks_click)
        self.delete_unused_kdks_checkbox.SetPosition(wx.Point(
            self.disable_amfi_checkbox.GetPosition().x,
            self.disable_amfi_checkbox.GetPosition().y + self.disable_amfi_checkbox.GetSize().height
        ))
        self.delete_unused_kdks_checkbox.SetToolTip(wx.ToolTip("This will delete unused KDKs during root patching.\nThis will save space on your drive, however can be disabled if you wish to keep KDKs installed."))


        # Set Ignore App Updates
        self.set_ignore_app_updates_checkbox = wx.CheckBox(self.frame_modal, label="Ignore App Updates")
        self.set_ignore_app_updates_checkbox.SetValue(self.constants.ignore_updates)
        self.set_ignore_app_updates_checkbox.Bind(wx.EVT_CHECKBOX, self.set_ignore_app_updates_click)
        self.set_ignore_app_updates_checkbox.SetPosition(wx.Point(
            self.delete_unused_kdks_checkbox.GetPosition().x,
            self.delete_unused_kdks_checkbox.GetPosition().y + self.delete_unused_kdks_checkbox.GetSize().height))
        self.set_ignore_app_updates_checkbox.SetToolTip(wx.ToolTip("This will set whether OpenCore will ignore App Updates on launch.\nEnable this option if you do not want to be prompted for App Updates"))

        # Set Disable Analytics
        res = global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting")
        res = False if res is None else res
        self.set_disable_analytics_checkbox = wx.CheckBox(self.frame_modal, label="Disable Crash/Analytics")
        self.set_disable_analytics_checkbox.SetValue(res)
        self.set_disable_analytics_checkbox.Bind(wx.EVT_CHECKBOX, self.set_disable_analytics_click)
        self.set_disable_analytics_checkbox.SetPosition(wx.Point(
            self.set_ignore_app_updates_checkbox.GetPosition().x,
            self.set_ignore_app_updates_checkbox.GetPosition().y + self.set_ignore_app_updates_checkbox.GetSize().height))
        self.set_disable_analytics_checkbox.SetToolTip(wx.ToolTip("Sets whether anonymized analytics are sent to the Dortania team.\nThis is used to help improve the application and is completely optional."))

        # Button: Developer Debug Info
        self.debug_button = wx.Button(self.frame_modal, label="Developer Debug Info")
        self.debug_button.Bind(wx.EVT_BUTTON, self.additional_info_menu)
        self.debug_button.SetPosition(wx.Point(
            self.set_disable_analytics_checkbox.GetPosition().x,
            self.set_disable_analytics_checkbox.GetPosition().y + self.set_disable_analytics_checkbox.GetSize().height + 5))
        self.debug_button.Center(wx.HORIZONTAL)

        # Button: return to main menu
        self.return_to_main_menu_button = wx.Button(self.frame_modal, label="Return to Settings")
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.return_to_main_menu_button.SetPosition(wx.Point(
            self.debug_button.GetPosition().x,
            self.debug_button.GetPosition().y + self.debug_button.GetSize().height + 10))
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        # set frame_modal size below return to main menu button

        self.frame_modal.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()

    def timeout_spinner_click(self, event):
        self.constants.oc_timeout = self.timeout_spinner.GetValue()

    def delete_unused_kdks_click(self, event):
        if self.delete_unused_kdks_checkbox.GetValue() is True:
            logging.info("Nuke KDKs enabled")
            self.constants.should_nuke_kdks = True
        else:
            logging.info("Nuke KDKs disabled")
            self.constants.should_nuke_kdks = False
        global_settings.GlobalEnviromentSettings().write_property("ShouldNukeKDKs", self.constants.should_nuke_kdks)

    def disable_library_validation_click(self, event):
        if self.disable_library_validation_checkbox.GetValue():
            logging.info("Disable Library Validation")
            self.disable_amfi_checkbox.Enable()
            self.constants.disable_cs_lv = True
        else:
            logging.info("Enable Library Validation")
            self.disable_amfi_checkbox.Disable()
            self.constants.disable_cs_lv = False

    def disable_amfi_click(self, event):
        if self.disable_amfi_checkbox.GetValue():
            logging.info("Disable AMFI")
            self.constants.disable_amfi = True
        else:
            logging.info("Enable AMFI")
            self.constants.disable_amfi = False

    def set_ignore_app_updates_click(self, event):
        self.constants.ignore_updates = self.set_ignore_app_updates_checkbox.GetValue()
        if self.constants.ignore_updates is True:
            global_settings.GlobalEnviromentSettings().write_property("IgnoreAppUpdates", True)
        else:
            global_settings.GlobalEnviromentSettings().write_property("IgnoreAppUpdates", False)

    def set_disable_analytics_click(self, event):
        global_settings.GlobalEnviromentSettings().write_property("DisableCrashAndAnalyticsReporting", self.set_disable_analytics_checkbox.GetValue())

    def firewire_click(self, event=None):
        if self.firewire_boot_checkbox.GetValue():
            logging.info("Firewire Enabled")
            self.constants.firewire_boot = True
        else:
            logging.info("Firewire Disabled")
            self.constants.firewire_boot = False

    def nvme_click(self, event=None):
        if self.nvme_boot_checkbox.GetValue():
            logging.info("NVMe Enabled")
            self.constants.nvme_boot = True
        else:
            logging.info("NVMe Disabled")
            self.constants.nvme_boot = False

    def nvme_power_management_click(self, event=None):
        if self.nvme_power_management_checkbox.GetValue():
            logging.info("NVMe Power Management Enabled")
            self.constants.allow_nvme_fixing = True
        else:
            logging.info("NVMe Power Management Disabled")
            self.constants.allow_nvme_fixing = False

    def xhci_click(self, event=None):
        if self.xhci_boot_checkbox.GetValue():
            logging.info("XHCI Enabled")
            self.constants.xhci_boot = True
        else:
            logging.info("XHCI Disabled")
            self.constants.xhci_boot = False

    def wake_on_wlan_click(self, event=None):
        if self.wake_on_wlan_checkbox.GetValue():
            logging.info("Wake on WLAN Enabled")
            self.constants.enable_wake_on_wlan = True
        else:
            logging.info("Wake on WLAN Disabled")
            self.constants.enable_wake_on_wlan = False

    def apfs_trim_click(self, event=None):
        if self.apfs_trim_checkbox.GetValue():
            logging.info("APFS Trim Enabled")
            self.constants.apfs_trim_timeout = True
        else:
            logging.info("APFS Trim Disabled")
            self.constants.apfs_trim_timeout = False

    def content_caching_click(self, event=None):
        if self.content_caching_checkbox.GetValue():
            logging.info("Content Caching Enabled")
            self.constants.set_content_caching = True
        else:
            logging.info("Content Caching Disabled")
            self.constants.set_content_caching = False

    def amd_gop_injection_checkbox_click(self, event=None):
        if self.set_amd_gop_injection.GetValue():
            logging.info("AMD GOP Injection Enabled")
            self.constants.amd_gop_injection = True
        else:
            logging.info("AMD GOP Injection Disabled")
            self.constants.amd_gop_injection = False

    def nvidia_kepler_gop_injection_checkbox_click(self, event=None):
        if self.set_nvidia_kepler_gop_injection.GetValue():
            logging.info("Nvidia Kepler GOP Injection Enabled")
            self.constants.nvidia_kepler_gop_injection = True
        else:
            logging.info("Nvidia Kepler GOP Injection Disabled")
            self.constants.nvidia_kepler_gop_injection = False

    def disable_tb_click(self, event=None):
        if self.disable_thunderbolt_checkbox.GetValue():
            logging.info("Disable Thunderbolt Enabled")
            self.constants.disable_tb = True
        else:
            logging.info("Disable Thunderbolt Disabled")
            self.constants.disable_tb = False

    def ts2_accel_click(self, event=None):
        if self.set_terascale_accel_checkbox.GetValue():
            logging.info("TS2 Acceleration Enabled")
            global_settings.GlobalEnviromentSettings().write_property("MacBookPro_TeraScale_2_Accel", True)
            self.constants.allow_ts2_accel = True
        else:
            logging.info("TS2 Acceleration Disabled")
            global_settings.GlobalEnviromentSettings().write_property("MacBookPro_TeraScale_2_Accel", False)
            self.constants.allow_ts2_accel = False

    def force_web_drivers_click(self, event=None):
        if self.force_web_drivers_checkbox.GetValue():
            logging.info("Force Web Drivers Enabled")
            global_settings.GlobalEnviromentSettings().write_property("Force_Web_Drivers", True)
            self.constants.force_nv_web = True
        else:
            logging.info("Force Web Drivers Disabled")
            global_settings.GlobalEnviromentSettings().write_property("Force_Web_Drivers", False)
            self.constants.force_nv_web = False

    def windows_gmux_click(self, event=None):
        if self.windows_gmux_checkbox.GetValue():
            logging.info("Windows GMUX Enabled")
            self.constants.dGPU_switch = True
        else:
            logging.info("Windows GMUX Disabled")
            self.constants.dGPU_switch = False

    def hibernation_click(self, event=None):
        if self.hibernation_checkbox.GetValue():
            logging.info("Hibernation Enabled")
            self.constants.disable_connectdrivers = True
        else:
            logging.info("Hibernation Disabled")
            self.constants.disable_connectdrivers = False

    def disable_battery_throttling_click(self, event=None):
        if self.disable_battery_throttling_checkbox.GetValue():
            logging.info("Disable Battery Throttling Enabled")
            self.constants.disable_msr_power_ctl = True
        else:
            logging.info("Disable Battery Throttling Disabled")
            self.constants.disable_msr_power_ctl = False

    def disable_xcpm_click(self, event=None):
        if self.disable_xcpm_checkbox.GetValue():
            logging.info("Disable XCPM Enabled")
            self.constants.disable_xcpm = True
        else:
            logging.info("Disable XCPM Disabled")
            self.constants.disable_xcpm = False

    def software_demux_click(self, event=None):
        if self.software_demux_checkbox.GetValue():
            logging.info("Software Demux Enabled")
            self.constants.software_demux = True
        else:
            logging.info("Software Demux Disabled")
            self.constants.software_demux = False

    def disable_cpu_friend_click(self, event=None):
        if self.disable_cpu_friend_checkbox.GetValue():
            logging.info("Disable CPUFriend Enabled")
            self.constants.disallow_cpufriend = True
        else:
            logging.info("Disable CPUFriend Disabled")
            self.constants.disallow_cpufriend = False

    def apple_alc_click(self, event=None):
        if self.apple_alc_checkbox.GetValue():
            logging.info("AppleALC Usage Enabled")
            self.constants.set_alc_usage = True
        else:
            logging.info("AppleALC Usage Disabled")
            self.constants.set_alc_usage = False

    def set_enhanced_3rd_party_ssd_click(self, event=None):
        if self.set_enhanced_3rd_party_ssd_checkbox.GetValue():
            logging.info("Enhanced 3rd Party SSDs Enabled")
            self.constants.allow_3rd_party_drives = True
        else:
            logging.info("Enhanced 3rd Party SSDs Disabled")
            self.constants.allow_3rd_party_drives = False

    def gpu_selection_click(self, event=None):
        gpu_choice =  self.gpu_dropdown.GetStringSelection()
        logging.info(f"GPU Selection: {gpu_choice}")
        if "AMD" in gpu_choice:
            self.constants.imac_vendor = "AMD"
            self.constants.metal_build = True
            if "Polaris" in gpu_choice:
                self.constants.imac_model = "Polaris"
            elif "GCN" in gpu_choice:
                self.constants.imac_model = "Legacy GCN"
            elif "Lexa" in gpu_choice:
                self.constants.imac_model = "AMD Lexa"
            elif "Navi" in gpu_choice:
                self.constants.imac_model = "AMD Navi"
            else:
                raise Exception("Unknown GPU Model")
        elif "Nvidia" in gpu_choice:
            self.constants.imac_vendor = "Nvidia"
            self.constants.metal_build = True
            if "Kepler" in gpu_choice:
                self.constants.imac_model = "Kepler"
            elif "GT" in gpu_choice:
                self.constants.imac_model = "GT"
            else:
                raise Exception("Unknown GPU Model")
        else:
            self.constants.imac_vendor = "None"
            self.constants.metal_build = False

        logging.info(f"GPU Vendor: {self.constants.imac_vendor}")
        logging.info(f"GPU Model: {self.constants.imac_model}")

    def fu_selection_click(self, event=None):
        fu_choice =  self.feature_unlock_dropdown.GetStringSelection()
        if fu_choice == "Enabled":
            self.constants.fu_status = True
            self.constants.fu_arguments = None
        elif fu_choice == "Partially enabled (No AirPlay/SideCar)":
            self.constants.fu_status = True
            self.constants.fu_arguments = " -disable_sidecar_mac"
        else:
            self.constants.fu_status = False
            self.constants.fu_arguments = None

    def set_writeflash_click(self, event=None):
        if self.set_writeflash_checkbox.GetValue():
            logging.info("Write Flash Enabled")
            self.constants.nvram_write = True
        else:
            logging.info("Write Flash Disabled")
            self.constants.nvram_write = False

    def smbios_settings_menu(self, event=None):
        self.reset_frame_modal()

        # Header: SMBIOS Settings
        self.smbios_settings_header = wx.StaticText(self.frame_modal, label="SMBIOS Settings", pos=wx.Point(10, 10))
        self.smbios_settings_header.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.smbios_settings_header.Center(wx.HORIZONTAL)

        # Label: SMBIOS Spoof Level
        self.smbios_spoof_level_label = wx.StaticText(self.frame_modal, label="SMBIOS Spoof Level")
        self.smbios_spoof_level_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.smbios_spoof_level_label.SetPosition(
            wx.Point(self.smbios_settings_header.GetPosition().x, self.smbios_settings_header.GetPosition().y + self.smbios_settings_header.GetSize().height + 10)
        )
        self.smbios_spoof_level_label.Center(wx.HORIZONTAL)

        # Dropdown: SMBIOS Spoof Level
        self.smbios_dropdown = wx.Choice(self.frame_modal)
        self.smbios_dropdown.SetPosition(
            wx.Point(self.smbios_spoof_level_label.GetPosition().x, self.smbios_spoof_level_label.GetPosition().y + self.smbios_spoof_level_label.GetSize().height + 10)
        )
        self.smbios_dropdown.AppendItems(["None", "Minimal", "Moderate", "Advanced"])
        self.smbios_dropdown.SetStringSelection(self.constants.serial_settings)
        self.smbios_dropdown.Bind(wx.EVT_CHOICE, self.smbios_spoof_level_click)
        self.smbios_dropdown.Center(wx.HORIZONTAL)

        # Label: SMBIOS Spoof Model
        self.smbios_spoof_model_label = wx.StaticText(self.frame_modal, label="SMBIOS Spoof Model")
        self.smbios_spoof_model_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.smbios_spoof_model_label.SetPosition(
            wx.Point(self.smbios_dropdown.GetPosition().x, self.smbios_dropdown.GetPosition().y + self.smbios_dropdown.GetSize().height + 10)
        )
        self.smbios_spoof_model_label.Center(wx.HORIZONTAL)

        # Dropdown: SMBIOS Spoof Model
        self.smbios_model_dropdown = wx.Choice(self.frame_modal)
        self.smbios_model_dropdown.SetPosition(
            wx.Point(self.smbios_spoof_model_label.GetPosition().x, self.smbios_spoof_model_label.GetPosition().y + self.smbios_spoof_model_label.GetSize().height + 10)
        )
        for model in smbios_data.smbios_dictionary:
            if "_" not in model and " " not in model:
                if smbios_data.smbios_dictionary[model]["Board ID"] is not None:
                    self.smbios_model_dropdown.Append(model)
        self.smbios_model_dropdown.Append("Default")
        self.smbios_model_dropdown.SetStringSelection(self.constants.override_smbios)
        self.smbios_model_dropdown.Bind(wx.EVT_CHOICE, self.smbios_model_click)
        self.smbios_model_dropdown.Center(wx.HORIZONTAL)
        if self.smbios_dropdown.GetStringSelection() == "None":
            self.smbios_model_dropdown.Disable()

        # Label: Custom Serial Number
        self.smbios_serial_label = wx.StaticText(self.frame_modal, label="Custom Serial Number")
        self.smbios_serial_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.smbios_serial_label.SetPosition(
            wx.Point(self.smbios_model_dropdown.GetPosition().x, self.smbios_model_dropdown.GetPosition().y + self.smbios_model_dropdown.GetSize().height + 10)
        )
        self.smbios_serial_label.Center(wx.HORIZONTAL)

        # Textbox: Custom Serial Number
        self.smbios_serial_textbox = wx.TextCtrl(self.frame_modal, style=wx.TE_CENTRE)
        self.smbios_serial_textbox.SetPosition(
            wx.Point(self.smbios_serial_label.GetPosition().x, self.smbios_serial_label.GetPosition().y + self.smbios_serial_label.GetSize().height + 5)
        )
        self.smbios_serial_textbox.SetValue(self.constants.custom_serial_number)
        self.smbios_serial_textbox.SetSize(wx.Size(200, -1))
        self.smbios_serial_textbox.Bind(wx.EVT_TEXT, self.smbios_serial_click)
        self.smbios_serial_textbox.Center(wx.HORIZONTAL)

        # Label: Custom Board Serial Number
        self.smbios_board_serial_label = wx.StaticText(self.frame_modal, label="Custom Board Serial Number")
        self.smbios_board_serial_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.smbios_board_serial_label.SetPosition(
            wx.Point(self.smbios_serial_textbox.GetPosition().x, self.smbios_serial_textbox.GetPosition().y + self.smbios_serial_textbox.GetSize().height + 10)
        )
        self.smbios_board_serial_label.Center(wx.HORIZONTAL)

        # Textbox: Custom Board Serial Number
        self.smbios_board_serial_textbox = wx.TextCtrl(self.frame_modal, style=wx.TE_CENTRE)
        self.smbios_board_serial_textbox.SetPosition(
            wx.Point(self.smbios_board_serial_label.GetPosition().x, self.smbios_board_serial_label.GetPosition().y + self.smbios_board_serial_label.GetSize().height + 5)
        )
        self.smbios_board_serial_textbox.SetValue(self.constants.custom_board_serial_number)
        self.smbios_board_serial_textbox.SetSize(wx.Size(200, -1))
        self.smbios_board_serial_textbox.Bind(wx.EVT_TEXT, self.smbios_board_serial_click)
        self.smbios_board_serial_textbox.Center(wx.HORIZONTAL)

        # Button: Generate new serials
        self.smbios_generate_button = wx.Button(self.frame_modal, label=f"Generate S/N: {self.constants.custom_model or self.computer.real_model}")
        self.smbios_generate_button.SetPosition(
            wx.Point(self.smbios_board_serial_textbox.GetPosition().x, self.smbios_board_serial_textbox.GetPosition().y + self.smbios_board_serial_textbox.GetSize().height + 10)
        )
        self.smbios_generate_button.Center(wx.HORIZONTAL)
        self.smbios_generate_button.Bind(wx.EVT_BUTTON, self.generate_new_serials_clicked)

        if self.constants.allow_oc_everywhere is False and \
            self.constants.custom_model is None and \
            self.computer.real_model not in model_array.SupportedSMBIOS:
            self.smbios_board_serial_textbox.Disable()
            self.smbios_serial_textbox.Disable()
            self.smbios_generate_button.Disable()

        # Checkbox: Allow Native Spoofs
        self.native_spoof_checkbox = wx.CheckBox(self.frame_modal, label="Allow Native Spoofs")
        self.native_spoof_checkbox.SetValue(self.constants.allow_native_spoofs)
        self.native_spoof_checkbox.SetPosition(
            wx.Point(self.smbios_generate_button.GetPosition().x, self.smbios_generate_button.GetPosition().y + self.smbios_generate_button.GetSize().height + 10)
        )
        self.native_spoof_checkbox.Bind(wx.EVT_CHECKBOX, self.native_spoof_click)
        self.native_spoof_checkbox.Center(wx.HORIZONTAL)
        self.native_spoof_checkbox.SetToolTip(wx.ToolTip("For native systems that cannot update their firmware, this option will allow OCLP to spoof the SMBIOS."))
        if self.constants.allow_oc_everywhere is False:
            self.native_spoof_checkbox.Disable()

        # Button: Return to Main Menu
        self.return_to_main_menu_button = wx.Button(self.frame_modal, label="Return to Settings")
        self.return_to_main_menu_button.SetPosition(
            wx.Point(self.native_spoof_checkbox.GetPosition().x, self.native_spoof_checkbox.GetPosition().y + self.native_spoof_checkbox.GetSize().height + 10)
        )
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        self.frame_modal.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()

    def smbios_serial_click(self, event):
        self.constants.custom_serial_number = self.smbios_serial_textbox.GetValue()

    def smbios_board_serial_click(self, event):
        self.constants.custom_board_serial_number = self.smbios_board_serial_textbox.GetValue()

    def generate_new_serials_clicked(self, event):
        # Throw pop up warning about misusing this feature
        dlg = wx.MessageDialog(self.frame_modal, "Please take caution when using serial spoofing. This should only be used on machines that were legally obtained and require reserialization.\n\nNote: new serials are only overlayed through OpenCore and are not permanently installed into ROM.\n\nMisuse of this setting can break power management and other aspects of the OS if the system does not need spoofing\n\nDortania does not condone the use of our software on stolen devices.\n\nAre you certain you want to continue?", "Warning", wx.YES_NO | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_NO:
            return
        macserial_output = subprocess.run([self.constants.macserial_path] + f"-g -m {self.constants.custom_model or self.computer.real_model} -n 1".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        macserial_output = macserial_output.stdout.decode().strip().split(" | ")
        if len(macserial_output) == 2:
            self.smbios_serial_textbox.SetValue(macserial_output[0])
            self.smbios_board_serial_textbox.SetValue(macserial_output[1])
        else:
            self.smbios_serial_textbox.SetHint("Unable to generate serials")
            self.smbios_board_serial_textbox.SetHint("Unable to generate serials")

    def native_spoof_click(self, event):
        if self.native_spoof_checkbox.GetValue():
            logging.info("Allow Native Spoofs Enabled")
            self.constants.allow_native_spoofs = True
        else:
            logging.info("Allow Native Spoofs Disabled")
            self.constants.allow_native_spoofs = False

    def smbios_spoof_level_click(self, event=None):
        # Throw pop up warning about misusing this feature
        selection = self.smbios_dropdown.GetStringSelection()
        if selection != "None":
            dlg = wx.MessageDialog(self.frame_modal, "This option should only be used when you need to change the machine's SMBIOS data.\n\nMisuse of this option can break OS functionality. Only use if you absolutely understand the need for this setting\n\nAre you certain you want to continue?", "Warning", wx.YES_NO | wx.ICON_WARNING)
            if dlg.ShowModal() == wx.ID_NO:
                self.smbios_dropdown.SetStringSelection(self.constants.serial_settings)
                return
        logging.info(f"SMBIOS Spoof Level: {selection}")
        self.constants.serial_settings = selection
        if selection == "None":
            self.smbios_model_dropdown.Disable()
        else:
            self.smbios_model_dropdown.Enable()

    def smbios_model_click(self, event=None):
        selection = self.smbios_model_dropdown.GetStringSelection()
        logging.info(f"SMBIOS Spoof Model: {selection}")
        self.constants.override_smbios = selection

    def additional_info_menu(self, event=None):
        self.reset_frame_modal()
        self.frame_modal.SetSize(wx.Size(500, -1))

        # Header: Additional Info
        self.additional_info_header = wx.StaticText(self.frame_modal, label="Developer Debug Info", pos=wx.Point(10, 10))
        self.additional_info_header.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.additional_info_header.Center(wx.HORIZONTAL)

        # Label: Real User ID
        self.real_user_id_label = wx.StaticText(self.frame_modal, label=f"Current UID: {os.getuid()} - ({os.geteuid()})")
        self.real_user_id_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.real_user_id_label.SetPosition(
            wx.Point(self.additional_info_header.GetPosition().x, self.additional_info_header.GetPosition().y + self.additional_info_header.GetSize().height + 10)
        )
        self.real_user_id_label.Center(wx.HORIZONTAL)


        commit_dict = self.constants.commit_info
        # Label: Built from Branch:
        self.built_from_branch_label = wx.StaticText(self.frame_modal, label=f"Branch: {commit_dict[0]}")
        self.built_from_branch_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.built_from_branch_label.SetPosition(
            wx.Point(self.real_user_id_label.GetPosition().x, self.real_user_id_label.GetPosition().y + self.real_user_id_label.GetSize().height + 10)
        )
        self.built_from_branch_label.Center(wx.HORIZONTAL)

        # Label: Built on: (Date)
        self.built_on_label = wx.StaticText(self.frame_modal, label=f"Date: {commit_dict[1]}")
        self.built_on_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.built_on_label.SetPosition(
            wx.Point(self.built_from_branch_label.GetPosition().x, self.built_from_branch_label.GetPosition().y + self.built_from_branch_label.GetSize().height + 10)
        )

        # Label: Commit URL: (hyperlink)
        self.commit_url_label = wx.StaticText(self.frame_modal, label=f"URL:  ")
        self.commit_url_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.commit_url_label.SetPosition(
            wx.Point(self.built_on_label.GetPosition().x, self.built_on_label.GetPosition().y + self.built_on_label.GetSize().height + 10)
        )

        # Hyperlink to the right of commit_url_label
        if commit_dict[2] != "":
            self.commit_url_hyperlink = hyperlink.HyperLinkCtrl(self.frame_modal, id=wx.ID_ANY, label=f"Link", URL=f"{commit_dict[2]}")
            self.commit_url_hyperlink.SetPosition(
                wx.Point(self.commit_url_label.GetPosition().x + self.commit_url_label.GetSize().width, self.commit_url_label.GetPosition().y)
            )
            self.commit_url_hyperlink.SetForegroundColour(self.hyperlink_colour)
            self.commit_url_hyperlink.SetColours(
                link=self.hyperlink_colour,
                visited=self.hyperlink_colour,
                rollover=self.hyperlink_colour,
            )

        else:
            self.commit_url_label.Label = f"URL:  Not applicable"

        # Label: Model Dump
        self.model_dump_label = wx.StaticText(self.frame_modal, label="Model Dump")
        self.model_dump_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.model_dump_label.SetPosition(
            wx.Point(self.commit_url_label.GetPosition().x, self.commit_url_label.GetPosition().y + self.commit_url_label.GetSize().height + 10)
        )
        self.model_dump_label.Center(wx.HORIZONTAL)

        # Textbox: Model Dump
        self.model_dump_textbox = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE, pos=wx.Point(self.model_dump_label.GetPosition().x, self.model_dump_label.GetPosition().y + self.model_dump_label.GetSize().height + 10))
        self.model_dump_textbox.SetValue(str(self.constants.computer))
        self.model_dump_textbox.SetPosition(
            wx.Point(self.model_dump_label.GetPosition().x, self.model_dump_label.GetPosition().y + self.model_dump_label.GetSize().height + 10)
        )
        self.model_dump_textbox.SetSize(
            wx.Size(
                self.frame_modal.GetSize().width - 5,
                self.model_dump_textbox.GetSize().height + self.model_dump_textbox.GetSize().height
            )
        )
        self.model_dump_textbox.Center(wx.HORIZONTAL)
        self.model_dump_textbox.SetEditable(False)



        # Label: Launcher Binary
        self.launcher_binary_label = wx.StaticText(self.frame_modal, label="Launcher Binary")
        self.launcher_binary_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.launcher_binary_label.SetPosition(
            wx.Point(self.model_dump_textbox.GetPosition().x, self.model_dump_textbox.GetPosition().y + self.model_dump_textbox.GetSize().height + 10)
        )
        self.launcher_binary_label.Center(wx.HORIZONTAL)

        # Textbox: Launcher Binary
        self.launcher_binary_textbox = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE, pos=wx.Point(self.launcher_binary_label.GetPosition().x, self.launcher_binary_label.GetPosition().y + self.launcher_binary_label.GetSize().height + 10))
        self.launcher_binary_textbox.SetValue(self.constants.launcher_binary)
        self.launcher_binary_textbox.SetPosition(
            wx.Point(self.launcher_binary_label.GetPosition().x, self.launcher_binary_label.GetPosition().y + self.launcher_binary_label.GetSize().height + 10)
        )
        self.launcher_binary_textbox.SetSize(wx.Size(self.frame_modal.GetSize().width - 5, 50))
        self.launcher_binary_textbox.Center(wx.HORIZONTAL)
        self.launcher_binary_textbox.SetEditable(False)

        # Label: Launcher Script
        self.launcher_script_label = wx.StaticText(self.frame_modal, label="Payload Location")
        self.launcher_script_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.launcher_script_label.SetPosition(
            wx.Point(self.launcher_binary_textbox.GetPosition().x, self.launcher_binary_textbox.GetPosition().y + self.launcher_binary_textbox.GetSize().height + 10)
        )
        self.launcher_script_label.Center(wx.HORIZONTAL)

        # Textbox: Launcher Script
        self.launcher_script_textbox = wx.TextCtrl(self.frame_modal, style=wx.TE_MULTILINE, pos=wx.Point(self.launcher_script_label.GetPosition().x, self.launcher_script_label.GetPosition().y + self.launcher_script_label.GetSize().height + 10))
        self.launcher_script_textbox.SetValue(str(self.constants.payload_path))
        self.launcher_script_textbox.SetPosition(
            wx.Point(self.launcher_script_label.GetPosition().x, self.launcher_script_label.GetPosition().y + self.launcher_script_label.GetSize().height + 10)
        )
        self.launcher_script_textbox.SetSize(wx.Size(self.frame_modal.GetSize().width - 5, 60))
        self.launcher_script_textbox.Center(wx.HORIZONTAL)
        self.launcher_script_textbox.SetEditable(False)

        self.return_to_main_menu_button = wx.Button(self.frame_modal, label="Return to Settings")
        self.return_to_main_menu_button.SetPosition(
            wx.Point(self.launcher_script_textbox.GetPosition().x, self.launcher_script_textbox.GetPosition().y + self.launcher_script_textbox.GetSize().height + 10)
        )
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        # Set frame_modal below return to main menu button
        self.frame_modal.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()


    def sip_config_menu(self, event=None):
        self.reset_frame_modal()
        self.frame_modal.SetSize(wx.Size(400, 600))

        # Title: Configure SIP
        self.configure_sip_title = wx.StaticText(self.frame_modal, label="Configure SIP", pos=wx.Point(10, 10))
        self.configure_sip_title.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.configure_sip_title.Center(wx.HORIZONTAL)

        # Label: Flip individual bits corresponding to XNU's csr.h
        # If you're unfamiliar with how SIP works, do not touch this menu
        self.sip_label = wx.StaticText(self.frame_modal, label="Flip individual bits corresponding to")
        self.sip_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.sip_label.SetPosition(
            wx.Point(-1, self.configure_sip_title.GetPosition().y + self.configure_sip_title.GetSize().height + 10)
        )
        self.sip_label.Center(wx.HORIZONTAL)
        self.sip_label.SetPosition(
            wx.Point(self.sip_label.GetPosition().x - 25, -1)
        )

        hyperlink_label = hyperlink.HyperLinkCtrl(
            self.frame_modal,
            -1,
            "XNU's csr.h",
            pos=(self.sip_label.GetPosition().x + self.sip_label.GetSize().width, self.sip_label.GetPosition().y),
            URL="https://github.com/apple/darwin-xnu/blob/main/bsd/sys/csr.h",
        )
        hyperlink_label.SetForegroundColour(self.hyperlink_colour)
        hyperlink_label.SetColours(
            link=self.hyperlink_colour,
            visited=self.hyperlink_colour,
            rollover=self.hyperlink_colour,
        )

        if self.constants.custom_sip_value is not None:
            self.sip_value = int(self.constants.custom_sip_value, 16)
        elif self.constants.sip_status is True:
            self.sip_value = 0x00
        else:
            self.sip_value = 0x803

        self.sip_label_2 = wx.StaticText(self.frame_modal, label=f"Currently configured SIP: {hex(self.sip_value)}")
        self.sip_label_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.sip_label_2.SetPosition(
            wx.Point(self.sip_label.GetPosition().x, self.sip_label.GetPosition().y + self.sip_label.GetSize().height + 10)
        )
        self.sip_label_2.Center(wx.HORIZONTAL)

        self.sip_label_2_2 = wx.StaticText(self.frame_modal, label=f"Currently Booted SIP: {hex(py_sip_xnu.SipXnu().get_sip_status().value)}")
        self.sip_label_2_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.sip_label_2_2.SetPosition(
            wx.Point(self.sip_label_2.GetPosition().x, self.sip_label_2.GetPosition().y + self.sip_label_2.GetSize().height + 5)
        )
        self.sip_label_2_2.Center(wx.HORIZONTAL)

        self.sip_label_3 = wx.StaticText(self.frame_modal, label="For older Macs requiring root patching, we set SIP to\n be partially disabled (0x803) to allow root patching.")
        self.sip_label_3.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.sip_label_3.SetPosition(
            wx.Point(self.sip_label_2_2.GetPosition().x, self.sip_label_2_2.GetPosition().y + self.sip_label_2_2.GetSize().height + 10)
        )
        self.sip_label_3.Center(wx.HORIZONTAL)

        self.sip_label_4 = wx.StaticText(self.frame_modal, label="This value (0x803) corresponds to the following bits in csr.h:")
        self.sip_label_4.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.sip_label_4.SetPosition(
            wx.Point(self.sip_label_3.GetPosition().x, self.sip_label_3.GetPosition().y + self.sip_label_3.GetSize().height + 5)
        )
        self.sip_label_4.Center(wx.HORIZONTAL)

        self.sip_label_5 = wx.StaticText(self.frame_modal, label="      0x1  - CSR_ALLOW_UNTRUSTED_KEXTS\n      0x2  - CSR_ALLOW_UNRESTRICTED_FS\n   0x800 - CSR_ALLOW_UNAUTHENTICATED_ROOT")
        self.sip_label_5.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.sip_label_5.SetPosition(
            wx.Point(self.sip_label_4.GetPosition().x, self.sip_label_4.GetPosition().y + self.sip_label_4.GetSize().height + 7)
        )
        self.sip_label_5.Center(wx.HORIZONTAL)

        warning_string = """
OpenCore Legacy Patcher by default knows the most ideal
 SIP value for your system. Override this value only if you
     understand the consequences. Reckless usage of this
               menu can break your installation.
"""
        self.sip_label_6 = wx.StaticText(self.frame_modal, label=warning_string)
        self.sip_label_6.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.sip_label_6.SetPosition(
            wx.Point(self.sip_label_5.GetPosition().x, self.sip_label_5.GetPosition().y + self.sip_label_5.GetSize().height - 10)
        )
        self.sip_label_6.Center(wx.HORIZONTAL)

        i = -10
        for sip_bit in sip_data.system_integrity_protection.csr_values_extended:
            self.sip_checkbox = wx.CheckBox(self.frame_modal, label=sip_data.system_integrity_protection.csr_values_extended[sip_bit]["name"])
            self.sip_checkbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            self.sip_checkbox.SetToolTip(f'Description: {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["description"]}\nValue: {hex(sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"])}\nIntroduced in: macOS {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["introduced_friendly"]}')
            self.sip_checkbox.SetPosition(
                wx.Point(70, self.sip_label_6.GetPosition().y + self.sip_label_6.GetSize().height + i)
            )
            i = i + 20
            self.sip_checkbox.Bind(wx.EVT_CHECKBOX, self.update_sip_value)
            if self.sip_value & sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"] == sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"]:
                self.sip_checkbox.SetValue(True)

        # Button: returns to the main menu
        self.return_to_main_menu_button = wx.Button(self.frame_modal, label="Return to Settings")
        self.return_to_main_menu_button.SetPosition(
            wx.Point(self.sip_checkbox.GetPosition().x, self.sip_checkbox.GetPosition().y + self.sip_checkbox.GetSize().height + 15)
        )
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        # Set the frame_modal size
        self.frame_modal.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()

    def update_sip_value(self, event):
        dict = sip_data.system_integrity_protection.csr_values_extended[event.GetEventObject().GetLabel()]
        if event.GetEventObject().GetValue() is True:
            self.sip_value = self.sip_value + dict["value"]
        else:
            self.sip_value = self.sip_value - dict["value"]
        if hex(self.sip_value) == "0x0":
            self.constants.custom_sip_value = None
            self.constants.sip_status = True
        elif hex(self.sip_value) == "0x803":
            self.constants.custom_sip_value = None
            self.constants.sip_status = False
        else:
            self.constants.custom_sip_value = hex(self.sip_value)
        self.sip_label_2.SetLabel(f"Currently configured SIP: {hex(self.sip_value)}")
        self.sip_label_2.Center(wx.HORIZONTAL)

    def misc_settings_menu(self, event):
        self.reset_frame_modal()

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Misc Settings", style=wx.ALIGN_CENTRE, pos=wx.Point(10, 10))
        self.header.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header.SetPosition(wx.Point(0, 10))
        self.header.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: If unfamiliar with the following settings, please do not change them.
        self.subheader = wx.StaticText(self.frame_modal, label="Configure settings", style=wx.ALIGN_CENTRE)
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(wx.Point(0, self.header.GetPosition().y + self.header.GetSize().height))
        self.subheader.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.subheader.Centre(wx.HORIZONTAL)
        # Subheader: , hover over options more info
        self.subheader_2 = wx.StaticText(self.frame_modal, label="Hover over options for more info", style=wx.ALIGN_CENTRE)
        self.subheader_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader_2.SetPosition(wx.Point(0, self.subheader.GetPosition().y + self.subheader.GetSize().height - 15))
        self.subheader_2.SetSize(wx.Size(self.frame_modal.GetSize().width, 30))
        self.subheader_2.Centre(wx.HORIZONTAL)

        # Label: Set FeatureUnlock status
        self.feature_unlock_label = wx.StaticText(self.frame_modal, label="Feature Unlock Status:", style=wx.ALIGN_CENTRE)
        self.feature_unlock_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.feature_unlock_label.SetPosition(wx.Point(0, self.subheader_2.GetPosition().y + self.subheader_2.GetSize().height -5))
        self.feature_unlock_label.Centre(wx.HORIZONTAL)

        # Dropdown: Set Feature Unlock status
        self.feature_unlock_dropdown = wx.Choice(self.frame_modal)
        for entry in ["Enabled", "Partially enabled (No AirPlay/SideCar)", "Disabled"]:
            self.feature_unlock_dropdown.Append(entry)
        self.feature_unlock_dropdown.SetPosition(wx.Point(0, self.feature_unlock_label.GetPosition().y + self.feature_unlock_label.GetSize().height + 5))
        if self.constants.fu_status is True:
            if self.constants.fu_arguments is None:
                selection = 0
            else:
                selection = 1
        else:
            selection = 2
        self.feature_unlock_dropdown.SetSelection(selection)
        self.feature_unlock_dropdown.Bind(wx.EVT_CHOICE, self.fu_selection_click)
        self.feature_unlock_dropdown.Centre(wx.HORIZONTAL)
        self.feature_unlock_dropdown.SetToolTip(wx.ToolTip("Set FeatureUnlock support level\nFor systems experiencing memory instability, lowering this option to disable AirPlay/Sidecar patch sets is recommended.\nFully enabling this option will unlock AirPlay to Mac and Sidecar support"))

        # FireWire Boot
        self.firewire_boot_checkbox = wx.CheckBox(self.frame_modal, label="FireWire Boot")
        self.firewire_boot_checkbox.SetValue(self.constants.firewire_boot)
        self.firewire_boot_checkbox.Bind(wx.EVT_CHECKBOX, self.firewire_click)
        self.firewire_boot_checkbox.SetPosition(wx.Point(50, self.feature_unlock_dropdown.GetPosition().y + self.feature_unlock_dropdown.GetSize().height + 5))
        self.firewire_boot_checkbox.SetToolTip(wx.ToolTip("Enable FireWire Boot support in macOS 10.15 and newer.\nMainly applicable for Macs with FireWire or Thunderbolt to FireWire adapters"))
        if generate_smbios.check_firewire(self.computer.real_model) is False and not self.constants.custom_model:
            self.firewire_boot_checkbox.Disable()

        # XHCI Boot
        self.xhci_boot_checkbox = wx.CheckBox(self.frame_modal, label="XHCI Boot")
        self.xhci_boot_checkbox.SetValue(self.constants.xhci_boot)
        self.xhci_boot_checkbox.Bind(wx.EVT_CHECKBOX, self.xhci_click)
        self.xhci_boot_checkbox.SetPosition(wx.Point(self.firewire_boot_checkbox.GetPosition().x, self.firewire_boot_checkbox.GetPosition().y + self.firewire_boot_checkbox.GetSize().height))
        self.xhci_boot_checkbox.SetToolTip(wx.ToolTip("Enables XHCI/USB3.o support in UEFI for non-native systems (ie. pre-Ivy Bridge)\nRequires OpenCore to be stored on a natively bootable volume however"))

        # NVMe Boot
        self.nvme_boot_checkbox = wx.CheckBox(self.frame_modal, label="NVMe Boot")
        self.nvme_boot_checkbox.SetValue(self.constants.nvme_boot)
        self.nvme_boot_checkbox.Bind(wx.EVT_CHECKBOX, self.nvme_click)
        self.nvme_boot_checkbox.SetPosition(wx.Point(self.xhci_boot_checkbox.GetPosition().x, self.xhci_boot_checkbox.GetPosition().y + self.xhci_boot_checkbox.GetSize().height))
        self.nvme_boot_checkbox.SetToolTip(wx.ToolTip("Enables NVMe support in UEFI for non-native systems (ie. MacPro3,1)\nRequires OpenCore to be stored on a natively bootable volume however"))

        # NVMe Power Management
        self.nvme_power_management_checkbox = wx.CheckBox(self.frame_modal, label="NVMe Power Management")
        self.nvme_power_management_checkbox.SetValue(self.constants.allow_nvme_fixing)
        self.nvme_power_management_checkbox.Bind(wx.EVT_CHECKBOX, self.nvme_power_management_click)
        self.nvme_power_management_checkbox.SetPosition(wx.Point(self.nvme_boot_checkbox.GetPosition().x, self.nvme_boot_checkbox.GetPosition().y + self.nvme_boot_checkbox.GetSize().height))
        self.nvme_power_management_checkbox.SetToolTip(wx.ToolTip("For machines with upgraded NVMe drives, this option allows for better power management support within macOS.\nNote that some NVMe drives don't support macOS's power management settings, and can result in boot issues. Disable this option if you experience IONVMeFamily kernel panics. Mainly applicable for Skylake and newer Macs."))

        # Wake on WLAN
        self.wake_on_wlan_checkbox = wx.CheckBox(self.frame_modal, label="Wake on WLAN")
        self.wake_on_wlan_checkbox.SetValue(self.constants.enable_wake_on_wlan)
        self.wake_on_wlan_checkbox.Bind(wx.EVT_CHECKBOX, self.wake_on_wlan_click)
        self.wake_on_wlan_checkbox.SetPosition(wx.Point(self.nvme_power_management_checkbox.GetPosition().x, self.nvme_power_management_checkbox.GetPosition().y + self.nvme_power_management_checkbox.GetSize().height))
        self.wake_on_wlan_checkbox.SetToolTip(wx.ToolTip("Enables Wake on WLAN for Broadcom Wifi.\nBy default, Wake on WLAN is disabled to work around Apple's wake from sleep bug causing heavily degraded networking performance.\nNote: This option is only applicable for BCM943224, BCM94331, BCM94360 and BCM943602 chipsets"))

        # Content Caching
        self.content_caching_checkbox = wx.CheckBox(self.frame_modal, label="Content Caching")
        self.content_caching_checkbox.SetValue(self.constants.set_content_caching)
        self.content_caching_checkbox.Bind(wx.EVT_CHECKBOX, self.content_caching_click)
        self.content_caching_checkbox.SetPosition(wx.Point(self.wake_on_wlan_checkbox.GetPosition().x, self.wake_on_wlan_checkbox.GetPosition().y + self.wake_on_wlan_checkbox.GetSize().height))
        self.content_caching_checkbox.SetToolTip(wx.ToolTip("Enables content caching support in macOS"))

        # APFS Trim
        self.apfs_trim_checkbox = wx.CheckBox(self.frame_modal, label="APFS Trim")
        self.apfs_trim_checkbox.SetValue(self.constants.apfs_trim_timeout)
        self.apfs_trim_checkbox.Bind(wx.EVT_CHECKBOX, self.apfs_trim_click)
        self.apfs_trim_checkbox.SetPosition(wx.Point(self.content_caching_checkbox.GetPosition().x, self.content_caching_checkbox.GetPosition().y + self.content_caching_checkbox.GetSize().height))
        self.apfs_trim_checkbox.SetToolTip(wx.ToolTip("Enables APFS Trim support in macOS"))

        # Button: return to main menu
        self.return_to_main_menu_button = wx.Button(self.frame_modal, label="Return to Settings")
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.return_to_main_menu_button.SetPosition(wx.Point(
            self.apfs_trim_checkbox.GetPosition().x,
            self.apfs_trim_checkbox.GetPosition().y + self.apfs_trim_checkbox.GetSize().height + 10))
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        # set frame_modal size below return to main menu button
        self.frame_modal.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()

    def non_metal_config_menu(self, event=None):
        # Configures ASB's Blur settings
        # Check Dark Menu Bar:
        #   defaults read Moraea_DarkMenuBar
        #   defaults write -g Moraea_DarkMenuBar -bool true
        # Check Beta Blur:
        #   defaults read Moraea_BlurBeta
        #   defaults write -g Moraea_BlurBeta -bool true
        # Check Blur Radius:
        #   defaults read ASB_BlurOverride
        #   defaults write -g ASB_BlurOverride -float 30

        self.reset_frame_modal()
        self.frame_modal.SetSize(wx.Size(400, 300))

        # Header 1: Configure non-Metal Settings

        self.header_1 = wx.StaticText(self.frame_modal, label="Configure non-Metal Settings", pos=wx.Point(10, 10))
        self.header_1.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.header_1.Centre(wx.HORIZONTAL)

        self.subheader = wx.StaticText(self.frame_modal, label="Below settings apply to systems that have installed")
        self.subheader.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader.SetPosition(wx.Point(0, self.header_1.GetPosition().y + self.header_1.GetSize().height + 5))
        self.subheader.Centre(wx.HORIZONTAL)

        self.subheader_2 = wx.StaticText(self.frame_modal, label="non-metal acceleration patches.")
        self.subheader_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader_2.SetPosition(wx.Point(0, self.subheader.GetPosition().y + self.subheader.GetSize().height))
        self.subheader_2.Centre(wx.HORIZONTAL)

        # This menu will allow you to enable Beta Blur features resolving some of the UI distortions experienced with non-Metal
        self.subheader2_1 = wx.StaticText(self.frame_modal, label="This menu will allow you to enable Beta Blur features resolving")
        self.subheader2_1.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader2_1.SetPosition(wx.Point(0, self.subheader_2.GetPosition().y + self.subheader_2.GetSize().height + 5))
        self.subheader2_1.Centre(wx.HORIZONTAL)

        self.subheader2_2 = wx.StaticText(self.frame_modal, label="some of the UI distortions experienced with non-metal GPUs.")
        self.subheader2_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader2_2.SetPosition(wx.Point(0, self.subheader2_1.GetPosition().y + self.subheader2_1.GetSize().height))
        self.subheader2_2.Centre(wx.HORIZONTAL)


        self.subheader_4 = wx.StaticText(self.frame_modal, label="Note: Only logout and login is required to apply these settings")
        self.subheader_4.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        self.subheader_4.SetPosition(wx.Point(0, self.subheader2_2.GetPosition().y + self.subheader2_2.GetSize().height+ 5))
        self.subheader_4.Centre(wx.HORIZONTAL)

        is_dark_menu_bar = subprocess.run(["defaults", "read", "-g", "Moraea_DarkMenuBar"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode("utf-8").strip()
        if is_dark_menu_bar in ["1", "true"]:
            is_dark_menu_bar = True
        else:
            is_dark_menu_bar = False

        is_blur_enabled = subprocess.run(["defaults", "read", "-g", "Moraea_BlurBeta"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode("utf-8").strip()
        if is_blur_enabled in ["1", "true"]:
            is_blur_enabled = True
        else:
            is_blur_enabled = False

        is_rim_disabled = subprocess.run(["defaults", "read", "-g", "Moraea_RimBetaDisabled"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode("utf-8").strip()
        if is_rim_disabled in ["1", "true"]:
            is_rim_disabled = True
        else:
            is_rim_disabled = False

        # Checkbox: Dark Menu Bar
        self.dark_menu_bar_checkbox = wx.CheckBox(self.frame_modal, label="Dark Menu Bar")
        self.dark_menu_bar_checkbox.SetValue(is_dark_menu_bar)
        self.dark_menu_bar_checkbox.Bind(wx.EVT_CHECKBOX, self.enable_dark_menubar_click)
        self.dark_menu_bar_checkbox.SetPosition(wx.Point(0, self.subheader_4.GetPosition().y + self.subheader_4.GetSize().height + 10))
        self.dark_menu_bar_checkbox.Centre(wx.HORIZONTAL)

        # Checkbox: Enable Beta Blur
        self.enable_beta_blur_checkbox = wx.CheckBox(self.frame_modal, label="Enable Beta Blur")
        self.enable_beta_blur_checkbox.SetValue(is_blur_enabled)
        self.enable_beta_blur_checkbox.Bind(wx.EVT_CHECKBOX, self.enable_beta_blur_click)
        self.enable_beta_blur_checkbox.SetPosition(wx.Point(self.dark_menu_bar_checkbox.GetPosition().x, self.dark_menu_bar_checkbox.GetPosition().y + self.dark_menu_bar_checkbox.GetSize().height + 7))

        # Checkbox: Enable Beta Rim
        self.enable_beta_rim_checkbox = wx.CheckBox(self.frame_modal, label="Disable Beta Rim")
        self.enable_beta_rim_checkbox.SetValue(is_rim_disabled)
        self.enable_beta_rim_checkbox.Bind(wx.EVT_CHECKBOX, self.enable_beta_rim_click)
        self.enable_beta_rim_checkbox.SetPosition(wx.Point(self.enable_beta_blur_checkbox.GetPosition().x, self.enable_beta_blur_checkbox.GetPosition().y + self.enable_beta_blur_checkbox.GetSize().height + 7))

        # Button: Return to Settings
        self.return_to_settings_button = wx.Button(self.frame_modal, label="Return to Settings")
        self.return_to_settings_button.Bind(wx.EVT_BUTTON, self.settings_menu)
        self.return_to_settings_button.SetPosition(wx.Point(0, self.enable_beta_rim_checkbox.GetPosition().y + self.enable_beta_rim_checkbox.GetSize().height + 10))
        self.return_to_settings_button.Center(wx.HORIZONTAL)

        self.frame_modal.SetSize(wx.Size(-1, self.return_to_settings_button.GetPosition().y + self.return_to_settings_button.GetSize().height + 40))
        self.frame_modal.ShowWindowModal()

    def enable_beta_blur_click(self, event=None):
        if event.IsChecked():
            subprocess.run(["defaults", "write", "-g", "Moraea_BlurBeta", "-bool", "true"])
        else:
            subprocess.run(["defaults", "write", "-g", "Moraea_BlurBeta", "-bool", "false"])
        logging.info("Beta Blur Enabled:", event.IsChecked())

    def enable_dark_menubar_click(self, event=None):
        if event.IsChecked():
            subprocess.run(["defaults", "write", "-g", "Moraea_DarkMenuBar", "-bool", "true"])
        else:
            subprocess.run(["defaults", "write", "-g", "Moraea_DarkMenuBar", "-bool", "false"])
        logging.info("Dark Menu Bar Enabled:", event.IsChecked())

    def enable_beta_rim_click(self, event=None):
        if event.IsChecked():
            subprocess.run(["defaults", "write", "-g", "Moraea_RimBetaDisabled", "-bool", "true"])
        else:
            subprocess.run(["defaults", "write", "-g", "Moraea_RimBetaDisabled", "-bool", "false"])
        logging.info("Beta Rim Enabled:", event.IsChecked())
