# Generate GUI for main menu
import wx
import sys
import logging
import threading

from resources.wx_gui import (
    gui_build,
    gui_macos_installer_download,
    gui_sys_patch,
    gui_support,
    gui_help,
    gui_settings,
    gui_update,
)
from resources import (
    constants,
    global_settings,
    updates
)
from data import os_data


class MainFrame(wx.Frame):
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        super(MainFrame, self).__init__(parent, title=title, size=(350, 300), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.constants: constants.Constants = global_constants
        self.title: str = title

        self.model_label: wx.StaticText = None
        self.build_button: wx.Button = None

        self.constants.update_stage = gui_support.AutoUpdateStages.INACTIVE

        self._generate_elements()

        self.SetPosition(screen_location) if screen_location else self.Centre()
        self.Show()

        self._preflight_checks()


    def _generate_elements(self) -> None:
        """
        Generate UI elements for the main menu

        Format:
          - Title label: OpenCore Legacy Patcher v{X.Y.Z}
          - Text:        Model: {Build or Host Model}
          - Buttons:
            - Build and Install OpenCore
            - Post-Install Root Patch
            - Create macOS Installer
            - Settings
            - Help
          - Text:        Copyright
        """

        # Title label: OpenCore Legacy Patcher v{X.Y.Z}
        title_label = wx.StaticText(self, label=f"OpenCore Legacy Patcher v{self.constants.patcher_version}", pos=(-1,1))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Centre(wx.HORIZONTAL)

        # Text: Model: {Build or Host Model}
        model_label = wx.StaticText(self, label=f"Model: {self.constants.custom_model or self.constants.computer.real_model}", pos=(-1,30))
        model_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        model_label.Centre(wx.HORIZONTAL)
        self.model_label = model_label

        # Buttons:
        menu_buttons = {
            "Build and Install OpenCore": self.on_build_and_install,
            "Post-Install Root Patch":    self.on_post_install_root_patch,
            "Create macOS Installer":     self.on_create_macos_installer,
            "Settings":                   self.on_settings,
            "Help":                       self.on_help
        }
        button_y = model_label.GetPosition()[1] + 20
        for button_name, button_function in menu_buttons.items():
            button = wx.Button(self, label=button_name, pos=(-1, button_y), size=(200, 30))
            button.Bind(wx.EVT_BUTTON, button_function)
            button.Centre(wx.HORIZONTAL)
            button_y += 30

            if button_name == "Build and Install OpenCore":
                self.build_button = button
                if gui_support.CheckProperties(self.constants).host_can_build() is False:
                    button.Disable()
            elif button_name == "Post-Install Root Patch":
                if self.constants.detected_os < os_data.os_data.big_sur:
                    button.Disable()

        # Text: Copyright
        copy_label = wx.StaticText(self, label=self.constants.copyright_date, pos=(-1, button_y + 10))
        copy_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        copy_label.Centre(wx.HORIZONTAL)

        # Set window size
        self.SetSize((350, copy_label.GetPosition()[1] + 50))


    def _preflight_checks(self):
        if (
                self.constants.computer.build_model != None and
                self.constants.computer.build_model != self.constants.computer.real_model and
                self.constants.host_is_hackintosh is False
            ):
            # Notify user they're booting an unsupported configuration
            pop_up = wx.MessageDialog(
                self,
                f"We found you are currently booting OpenCore built for a different unit: {self.constants.computer.build_model}\n\nWe builds configs to match individual units and cannot be mixed or reused with different Macs.\n\nPlease Build and Install a new OpenCore config, and reboot your Mac.",
                "Unsupported Configuration Detected!",
                style=wx.OK | wx.ICON_EXCLAMATION
            )
            pop_up.ShowModal()
            self.on_build_and_install()
            return

        if "--update_installed" in sys.argv and self.constants.has_checked_updates is False and gui_support.CheckProperties(self.constants).host_can_build():
            # Notify user that the update has been installed
            self.constants.has_checked_updates = True
            pop_up = wx.MessageDialog(
                self,
                f"OpenCore Legacy Patcher has been updated to the latest version: {self.constants.patcher_version}\n\nWould you like to update OpenCore and your root volume patches?",
                "Update successful!",
                style=wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
            )
            pop_up.ShowModal()

            if pop_up.GetReturnCode() != wx.ID_YES:
                print("- Skipping OpenCore and root volume patch update...")
                return


            print("- Updating OpenCore and root volume patches...")
            self.constants.update_stage = gui_support.AutoUpdateStages.CHECKING
            self.Hide()
            pos = self.GetPosition()
            gui_build.BuildFrame(
                parent=None,
                title=self.title,
                global_constants=self.constants,
                screen_location=pos
            )
            self.Close()

        threading.Thread(target=self._check_for_updates).start()


    def _check_for_updates(self):
        if self.constants.has_checked_updates is True:
            return

        ignore_updates = global_settings.GlobalEnviromentSettings().read_property("IgnoreAppUpdates")
        if ignore_updates is True:
            self.constants.ignore_updates = True
            return

        self.constants.ignore_updates = False
        self.constants.has_checked_updates = True
        dict = updates.CheckBinaryUpdates(self.constants).check_binary_updates()
        if not dict:
            return

        for entry in dict:
            version = dict[entry]["Version"]
            logging.info(f"New version: {version}")
            dialog = wx.MessageDialog(
                parent=self,
                message=f"Current Version: {self.constants.patcher_version}{' (Nightly)' if not self.constants.commit_info[0].startswith('refs/tags') else ''}\nNew version: {version}\nWould you like to update?",
                caption="Update Available for OpenCore Legacy Patcher!",
                style=wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )
            dialog.SetYesNoCancelLabels("Download and install", "Always Ignore", "Ignore Once")
            response = dialog.ShowModal()

            if response == wx.ID_YES:
                wx.CallAfter(self.on_update, dict[entry]["Link"], version)
            elif response == wx.ID_NO:
                logging.info("- Setting IgnoreAppUpdates to True")
                self.constants.ignore_updates = True
                global_settings.GlobalEnviromentSettings().write_property("IgnoreAppUpdates", True)


    def on_build_and_install(self, event: wx.Event = None):
        self.Hide()
        gui_build.BuildFrame(
            parent=None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition()
        )
        self.Destroy()


    def on_post_install_root_patch(self, event: wx.Event = None):
        self.Hide()
        gui_sys_patch.SysPatchFrame(
            parent=None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition()
        )
        self.Destroy()


    def on_create_macos_installer(self, event: wx.Event = None):
        gui_macos_installer_download.macOSInstallerDownloadFrame(
            parent=self,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition()
        )


    def on_settings(self, event: wx.Event = None):
        gui_settings.SettingsFrame(
            parent=self,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition()
        )

    def on_help(self, event: wx.Event = None):
        gui_help.HelpFrame(
            parent=self,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition()
        )

    def on_update(self, oclp_url: str, oclp_version: str):
        gui_update.UpdateFrame(
            parent=self,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition(),
            url=oclp_url,
            version_label=oclp_version
        )