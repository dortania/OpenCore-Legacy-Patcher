# Setup GUI
# Implemented using wxPython
# Currently Work in Progress

import wx
import sys
import webbrowser
import subprocess
import time
import os
import wx.adv
from wx.lib.agw import hyperlink

from resources import constants, defaults, build, install, installer, utilities, sys_patch_detect, sys_patch, run, generate_smbios
from data import model_array, os_data, smbios_data, sip_data
from gui import menu_redirect

class wx_python_gui:
    def __init__(self, versions):
        self.constants: constants.Constants = versions
        self.computer = self.constants.computer
        self.constants.gui_mode = True
        self.walkthrough_mode = False

        # Backup stdout for usage with wxPython
        self.stock_stdout = sys.stdout
        self.stock_stderr = sys.stderr

        # Define Window Size
        self.WINDOW_WIDTH_MAIN = 350
        self.WINDOW_HEIGHT_MAIN = 220
        self.WINDOW_WIDTH_BUILD = 400
        self.WINDOW_HEIGHT_BUILD = 500
        self.WINDOW_SETTINGS_WIDTH = 230
        self.WINDOW_SETTINGS_HEIGHT = 320

        # Create Application
        self.app = wx.App()
        self.frame = wx.Frame(
            None, title="OpenCore Legacy Patcher", 
            size=(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN),
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        )
        self.frame.Centre(~wx.MAXIMIZE_BOX)
        self.frame.Show()
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        self.main_menu(None)

        wx.CallAfter(self.frame.Close)
    
    def OnCloseFrame(self, event):
        print("Cleaning up on close")
        self.frame.DestroyChildren()
        self.frame.Destroy()
        self.app.ExitMainLoop()
        sys.exit()
    
    def reset_window(self):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)
        sys.stdout = self.stock_stdout
        sys.stderr = self.stock_stderr
    
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
            print("Relaunching as root")
            if self.constants.launcher_script is None:
                args_string = f"{self.constants.launcher_binary}"""
            else:
                args_string = f"{self.constants.launcher_binary} {self.constants.launcher_script}"

            args = [
                "osascript",
                "-e",
                f'''do shell script "'{args_string}'"'''
                ' with prompt "OpenCore Legacy Patcher needs administrator privileges to mount your EFI."'
                " with administrator privileges"
                " without altering line endings",
            ]

            self.frame.DestroyChildren()
            self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)

            # Header
            self.header = wx.StaticText(self.frame, label="Relaunching as root")
            self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.header.Centre(wx.HORIZONTAL)

            # Add count down label
            self.countdown_label = wx.StaticText(self.frame, label="Closing old process in 15 seconds")
            self.countdown_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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
            self.countdown_label2.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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
            timer_val = 15
            while True:
                wx.GetApp().Yield()
                self.countdown_label.SetLabel(f"Closing old process in {timer_val} seconds")
                time.sleep(1)
                timer_val -= 1
                if timer_val == 0:
                    break
            # Close Current Application
            self.frame.Close()
    
    def not_yet_implemented_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)

        # Header
        self.header = wx.StaticText(self.frame, label="🚧 Not Yet Implemented")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
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
        self.frame.SetTitle(f"OpenCore Legacy Patcher v{self.constants.patcher_version}")
        # Header
        self.header = wx.StaticText(self.frame, label=f"OpenCore Legacy Patcher v{self.constants.patcher_version}")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label=f"Model: {self.constants.custom_model or self.computer.real_model}")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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
        if self.constants.allow_oc_everywhere is False and \
            self.constants.custom_model is None and \
            self.computer.real_model not in model_array.SupportedSMBIOS:
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
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina] and self.constants.moj_cat_accel == False:
            self.post_install.SetToolTip(wx.ToolTip("""Graphics Acceleration fro Mojave and Catalina is currently experimental. \nIf you require this feature, enable '10.14/15 Accel' in Settings."""))
            self.post_install.Disable()
        elif self.constants.detected_os < os_data.os_data.mojave:
            self.post_install.SetToolTip(wx.ToolTip("""Root Patching is only available for Mojave and newer."""))
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
        self.help_button.Bind(wx.EVT_BUTTON, self.help_menu)
        self.help_button.Centre(wx.HORIZONTAL)


        # Copyright Label
        self.copyright = wx.StaticText(self.frame, label="Copyright © 2020-2022 Dortania")
        self.copyright.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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

        if self.app.MainLoop() is None:
            self.app.MainLoop() 
    
    def help_menu(self, event=None):
        # Define Menu
        # Header: Get help with OpenCore Legacy Patcher
        # Subheader: Following resources are available:
        # Button: Official Guide
        # Button: Offical Discord Server

        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label="Patcher Resources")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label="Following resources are available:")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)


        # Official Guide
        self.guide = wx.Button(self.frame, label="Official Guide", size=(200,30))
        self.guide.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 5

            )
        )
        self.guide.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(self.constants.guide_link))
        self.guide.Centre(wx.HORIZONTAL)

        # Official Discord Server
        self.discord = wx.Button(self.frame, label="Official Discord Server", size=(200,30))
        self.discord.SetPosition(
            wx.Point(
                self.guide.GetPosition().x,
                self.guide.GetPosition().y + self.guide.GetSize().height
            )
        )
        self.discord.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(self.constants.discord_link))
        self.discord.Centre(wx.HORIZONTAL)

        # Overclock Button
        self.overclock = wx.Button(self.frame, label="Offical Support Phone", size=(200,30))
        self.overclock.SetPosition(
            wx.Point(
                self.discord.GetPosition().x,
                self.discord.GetPosition().y + self.discord.GetSize().height
            )
        )
        self.overclock.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.overclock.Centre(wx.HORIZONTAL)


        self.return_to_main = wx.Button(self.frame, label="Return to Main Menu", size=(150,30))
        self.return_to_main.SetPosition(
            wx.Point(
                self.overclock.GetPosition().x,
                self.overclock.GetPosition().y + self.overclock.GetSize().height + 5
            )
        )
        self.return_to_main.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main.Centre(wx.HORIZONTAL)

        # Set Window Size to below Copyright Label
        self.frame.SetSize(
            (
                -1,
                self.return_to_main.GetPosition().y + self.return_to_main.GetSize().height + 40
            )
        )
    
    def build_install_menu(self, event=None):
        # Define Menu
        # - Header: Build and Install OpenCore
        # - Subheader: Model: {self.constants.custom_model or self.computer.real_model}
        # - Button: Build OpenCore
        # - Textbox: stdout
        # - Button: Return to Main Menu

        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.WINDOW_HEIGHT_BUILD)

        # Header
        self.header = wx.StaticText(self.frame, label="Build and Install OpenCore")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label=f"Model: {self.constants.custom_model or self.computer.real_model}")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Build OpenCore
        self.build_opencore = wx.Button(self.frame, label="🔨 Build OpenCore", size=(150,30))
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
        self.stdout_text = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.stdout_text.SetPosition(wx.Point(self.build_opencore.GetPosition().x, self.build_opencore.GetPosition().y + self.build_opencore.GetSize().height + 10))
        self.stdout_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        # Set width to same as frame
        self.stdout_text.SetSize(self.WINDOW_WIDTH_BUILD, 340)
        # Centre the text box to top of window
        self.stdout_text.Centre(wx.HORIZONTAL)
        self.stdout_text.SetValue("")
        sys.stdout=menu_redirect.RedirectText(self.stdout_text, False)
        sys.stderr=menu_redirect.RedirectText(self.stdout_text, False)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.stdout_text.GetPosition().x,
                self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
    
    def build_start(self, event=None):
        build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).build_opencore()
        # Once finished, change build_opencore button to "Install OpenCore"
        self.build_opencore.SetLabel("🔩 Install OpenCore")
        self.build_opencore.Bind(wx.EVT_BUTTON, self.install_menu)
        
        # Reset stdout
        sys.stdout = self.stock_stdout
        sys.stderr = self.stock_stderr
    
    def install_menu(self, event=None):
        self.frame.DestroyChildren()
        i = 0
        
        # Header
        self.header = wx.StaticText(self.frame, label="Install OpenCore")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: Select Disk to install OpenCore onto
        self.subheader = wx.StaticText(self.frame, label="Select Disk to install OpenCore onto")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Label: If you're missing disks, ensure they're either FAT32 or formatted as GUI/GPT
        self.missing_disks = wx.StaticText(self.frame, label="Missing disks? Ensure they're FAT32 or formatted as GUID/GPT")
        self.missing_disks.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.missing_disks.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 5
            )
        )
        self.missing_disks.Centre(wx.HORIZONTAL)

        # Request Disks Present
        list_disks = install.tui_disk_installation(self.constants).list_disks()
        if list_disks:
            for disk in list_disks:
                # Create a button for each disk
                print(f"{list_disks[disk]['disk']} - {list_disks[disk]['name']} - {list_disks[disk]['size']}")
                self.install_button = wx.Button(self.frame, label=disk, size=(300,30))
                self.install_button.SetLabel(f"{list_disks[disk]['disk']} - {list_disks[disk]['name']} - {list_disks[disk]['size']}")
                self.install_button.SetPosition(
                    wx.Point(
                        self.missing_disks.GetPosition().x,
                        self.missing_disks.GetPosition().y + self.missing_disks.GetSize().height + 3 + i
                    )
                )
                self.install_button.Bind(wx.EVT_BUTTON, lambda event, temp=disk: self.install_oc_disk_select(temp, list_disks))
                self.install_button.Centre(wx.HORIZONTAL)
                i += self.install_button.GetSize().height + 3
        else:
            # Label: No disks found
            self.install_button = wx.StaticText(self.frame, label="Failed to find any applicable disks")
            self.install_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.install_button.SetPosition(
                wx.Point(
                    self.missing_disks.GetPosition().x,
                    self.missing_disks.GetPosition().y + self.missing_disks.GetSize().height + 3
                )
            )
            self.install_button.Centre(wx.HORIZONTAL)
            

        
        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.install_button.GetPosition().x,
                self.install_button.GetPosition().y + self.install_button.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
    
    def install_oc_disk_select(self, disk, disk_data):
        self.frame.DestroyChildren()
        i = 0

        # Header
        self.header = wx.StaticText(self.frame, label="Install OpenCore")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: Select Partition to install OpenCore onto
        self.subheader = wx.StaticText(self.frame, label="Select Partition to install OpenCore onto")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        list_partitions = install.tui_disk_installation(self.constants).list_partitions(disk, disk_data)
        for partition in list_partitions:
            print(f"{list_partitions[partition]['partition']} - {list_partitions[partition]['name']} - {list_partitions[partition]['size']}")
            self.install_button = wx.Button(self.frame, label=partition, size=(300,30))
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
        
        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.install_button.GetPosition().x,
                self.install_button.GetPosition().y + self.install_button.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def install_oc_process(self, partition):
        print(f"Installing OpenCore to {partition}")
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.WINDOW_HEIGHT_BUILD)

        # Header
        self.header = wx.StaticText(self.frame, label="Install OpenCore")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Textbox
        # Redirect stdout to a text box
        self.stdout_text = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.stdout_text.SetPosition(wx.Point(self.header.GetPosition().x, self.header.GetPosition().y + self.header.GetSize().height + 10))
        self.stdout_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        # Set width to same as frame
        self.stdout_text.SetSize(self.WINDOW_WIDTH_BUILD, 340)
        # Centre the text box to top of window
        self.stdout_text.Centre(wx.HORIZONTAL)
        self.stdout_text.SetValue("")
        sys.stdout=menu_redirect.RedirectText(self.stdout_text, False)
        sys.stderr=menu_redirect.RedirectText(self.stdout_text, False)

        # Update frame height to right below
        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 40)

        self.frame.Show()

        install.tui_disk_installation(self.constants).install_opencore(partition)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.stdout_text.GetPosition().x,
                self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 10

            )   
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def root_patch_menu(self, event=None):
        # Define Menu
        # Header: Post-Install Menu
        # Subheader: Available patches for system:
        # Label: Placeholder for patch name
        # Button: Start Root Patching
        # Button: Revert Root Patches
        # Button: Return to Main Menu
        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label=f"Post-Install Menu")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label="Available patches for system:")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        patches = sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).detect_patch_set()
        if not any(not patch.startswith("Settings") and patches[patch] is True for patch in patches):
            print("- No applicable patches available")
            patches = []

        i = 0
        if patches:
            for patch in patches:
                # Add Label for each patch
                if (not patch.startswith("Settings") and patches[patch] is True):
                    print(f"- Adding patch: {patch} - {patches[patch]}")
                    self.patch_label = wx.StaticText(self.frame, label=f"- {patch}")
                    self.patch_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                    self.patch_label.SetPosition(
                        wx.Point(
                            self.subheader.GetPosition().x,
                            self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                        )
                    )
                    i = i + self.patch_label.GetSize().height + 3
        else:
            # Prompt user with no patches found
            self.patch_label = wx.StaticText(self.frame, label="No patches found")
            self.patch_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            self.patch_label.SetPosition(
                wx.Point(
                    self.subheader.GetPosition().x,
                    self.subheader.GetPosition().y + self.subheader.GetSize().height + 3 + i
                )
            )
            self.patch_label.Centre(wx.HORIZONTAL)
        
        # Start Root Patching
        self.start_root_patching = wx.Button(self.frame, label="Start Root Patching", size=(170, -1))
        self.start_root_patching.SetPosition(
            wx.Point(
                self.patch_label.GetPosition().x,
                self.patch_label.GetPosition().y + self.patch_label.GetSize().height + 10
            )
        )
        uid = os.geteuid()
        print(f"Effective UID: {uid}")
        if uid == 0:
            self.start_root_patching.Bind(wx.EVT_BUTTON, self.root_patch_start)
        else:
            self.start_root_patching.Bind(wx.EVT_BUTTON, self.relaunch_as_root)
        self.start_root_patching.Centre(wx.HORIZONTAL)
        if not patches:
            self.start_root_patching.Disable()

        # Revert Root Patches
        self.revert_root_patches = wx.Button(self.frame, label="Revert Root Patches", size=(170, -1))
        self.revert_root_patches.SetPosition(
            wx.Point(
                self.start_root_patching.GetPosition().x,
                self.start_root_patching.GetPosition().y + self.start_root_patching.GetSize().height + 3
            )
        )
        if uid == 0:
            self.revert_root_patches.Bind(wx.EVT_BUTTON, self.root_patch_revert)
        else:
            self.revert_root_patches.Bind(wx.EVT_BUTTON, self.relaunch_as_root)
        self.revert_root_patches.Centre(wx.HORIZONTAL)
        if self.constants.detected_os < os_data.os_data.big_sur:
            self.revert_root_patches.Disable()

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.revert_root_patches.GetPosition().x,
                self.revert_root_patches.GetPosition().y + self.revert_root_patches.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
    
    def root_patch_start(self, event=None):
        self.frame.DestroyChildren()

        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, -1)

        # Header
        self.header = wx.StaticText(self.frame, label="Root Patching")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame, label="Starting root volume patching")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        self.developer_note = wx.StaticText(self.frame, label="Starting shortly")
        self.developer_note.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.developer_note.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.developer_note.Centre(wx.HORIZONTAL)

        # Text Box
        self.text_box = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.text_box.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.text_box.SetPosition(
            wx.Point(
                self.developer_note.GetPosition().x,
                self.developer_note.GetPosition().y + self.developer_note.GetSize().height + 3
            )
        )
        self.text_box.SetSize(
            wx.Size(
                self.frame.GetSize().width - 10,
                self.frame.GetSize().height + self.text_box.GetPosition().y + 80
            )
        )
        self.text_box.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.text_box.GetPosition().x,
                self.text_box.GetPosition().y + self.text_box.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

        wx.GetApp().Yield()

        sys.stdout = menu_redirect.RedirectText(self.text_box, True)
        sys.stderr = menu_redirect.RedirectText(self.text_box, True)
        wx.GetApp().Yield()
        self.frame.Show()
        sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants).start_patch()
        sys.stdout = self.stock_stdout
        sys.stderr = self.stock_stderr

        wx.GetApp().Yield()
    
    def root_patch_revert(self, event=None):
        self.frame.DestroyChildren()

        self.frame.SetSize(self.WINDOW_WIDTH_BUILD, -1)

        # Header
        self.header = wx.StaticText(self.frame, label="Revert Root Patches")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        if self.constants.detected_os == os_data.os_data.big_sur:
            self.subheader = wx.StaticText(self.frame, label="Currently experimental in Big Sur")
        else:
            self.subheader = wx.StaticText(self.frame, label="Reverting to last sealed snapshot")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        self.developer_note = wx.StaticText(self.frame, label="Starting shortly")
        self.developer_note.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.developer_note.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 3
            )
        )
        self.developer_note.Centre(wx.HORIZONTAL)

        # Text Box
        self.text_box = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.text_box.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.text_box.SetPosition(
            wx.Point(
                self.developer_note.GetPosition().x,
                self.developer_note.GetPosition().y + self.developer_note.GetSize().height + 3
            )
        )
        self.text_box.SetSize(
            wx.Size(
                self.frame.GetSize().width - 10,
                self.frame.GetSize().height + self.text_box.GetPosition().y + 80
            )
        )
        self.text_box.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.text_box.GetPosition().x,
                self.text_box.GetPosition().y + self.text_box.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

        # Start reverting root patches
        sys.stdout = menu_redirect.RedirectText(self.text_box, True)
        sys.stderr = menu_redirect.RedirectText(self.text_box, True)
        wx.GetApp().Yield()
        sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants).start_unpatch()
        sys.stdout = self.stock_stdout
        sys.stderr = self.stock_stderr

        wx.GetApp().Yield()

    def create_macos_menu(self, event=None):
        # Define Menu
        # Header: Create macOS Installer
        # Options:
        #   - Download macOS Installer
        #   - Use existing macOS Installer
        #   - Return to Main Menu

        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label="Create macOS Installer")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Button: Download macOS Installer
        self.download_macos_installer = wx.Button(self.frame, label="Download macOS Installer", size=(200, 30))
        self.download_macos_installer.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.download_macos_installer.Bind(wx.EVT_BUTTON, self.grab_installer_data)
        self.download_macos_installer.Centre(wx.HORIZONTAL)

        # Button: Use existing macOS Installer
        self.use_existing_macos_installer = wx.Button(self.frame, label="Use existing macOS Installer", size=(200, 30))
        self.use_existing_macos_installer.SetPosition(
            wx.Point(
                self.download_macos_installer.GetPosition().x,
                self.download_macos_installer.GetPosition().y + self.download_macos_installer.GetSize().height
            )
        )
        self.use_existing_macos_installer.Bind(wx.EVT_BUTTON, self.flash_installer_menu)
        self.use_existing_macos_installer.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.use_existing_macos_installer.GetPosition().x,
                self.use_existing_macos_installer.GetPosition().y + self.use_existing_macos_installer.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def grab_installer_data(self, event=None):
        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label="Pulling installer catalog")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Label: Download...
        self.download_label = wx.StaticText(self.frame, label="Downloading installer catalog...")
        self.download_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.download_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.download_label.Centre(wx.HORIZONTAL)
        # Redirect stdout to label
        sys.stdout=menu_redirect.RedirectLabel(self.download_label)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.download_label.GetPosition().x,
                self.download_label.GetPosition().y + self.download_label.GetSize().height + 30
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.Show()

        # Download installer catalog
        avalible_installers = installer.list_downloadable_macOS_installers(self.constants.payload_path, "PublicSeed")

        self.frame.DestroyChildren()
        sys.stdout = self.stock_stdout

        # Header
        self.header = wx.StaticText(self.frame, label="Download macOS Installer")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader:
        self.subheader = wx.StaticText(self.frame, label="Installers currently available from Apple:")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)


        # Sort Installers by 'Version'
        # By default Apple adds new builds to the end of the list, so we need to sort them by version
        avalible_installers = {k: v for k, v in sorted(avalible_installers.items(), key=lambda x: x[1]['Version'])}

        i = -20
        if avalible_installers:
            for app in avalible_installers:
                print(f"macOS {avalible_installers[app]['Version']} ({avalible_installers[app]['Build']} - {utilities.human_fmt(avalible_installers[app]['Size'])} - {avalible_installers[app]['Source']})")
                self.install_selection = wx.Button(self.frame, label=f"macOS {avalible_installers[app]['Version']} ({avalible_installers[app]['Build']} - {utilities.human_fmt(avalible_installers[app]['Size'])})", size=(250, 30))
                i = i + 25
                self.install_selection.SetPosition(
                    wx.Point(
                        self.subheader.GetPosition().x,
                        self.subheader.GetPosition().y + self.subheader.GetSize().height + i
                    )
                )
                self.install_selection.Bind(wx.EVT_BUTTON, lambda event, temp=app: self.download_macos_click(f"macOS {avalible_installers[temp]['Version']} ({avalible_installers[temp]['Build']})", avalible_installers[temp]['Link']))
                self.install_selection.Centre(wx.HORIZONTAL)
        else:
            self.install_selection = wx.StaticText(self.frame, label="No installers available")
            i = i + 25
            self.install_selection.SetPosition(
                wx.Point(
                    self.subheader.GetPosition().x,
                    self.subheader.GetPosition().y + self.subheader.GetSize().height + i
                )
            )
            self.install_selection.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
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

        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

    def download_macos_click(self, installer_name, installer_link):
        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label=f"Downloading {installer_name}")
        self.frame.SetSize(self.header.GetSize().width + 200, -1)
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)
        
        # Label: Download...
        self.download_label = wx.StaticText(self.frame, label="Downloading...")
        self.download_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.download_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.download_label.Centre(wx.HORIZONTAL)
        # Redirect stdout to label
        sys.stdout=menu_redirect.RedirectLabel(self.download_label)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.download_label.GetPosition().x,
                self.download_label.GetPosition().y + self.download_label.GetSize().height + 30
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)
        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)

        # Download macOS install data
        if installer.download_install_assistant(self.constants.payload_path, installer_link):
            # Fix stdout
            sys.stdout = self.stock_stdout
            self.download_label.SetLabel(f"Finished Downloading {installer_name}")
            self.download_label.Centre(wx.HORIZONTAL)

            # Update Label: 
            sys.stdout=menu_redirect.RedirectLabelAll(self.download_label)
            sys.stderr=menu_redirect.RedirectLabelAll(self.download_label)
            installer.install_macOS_installer(self.constants.payload_path)
            sys.stdout = self.stock_stdout
            sys.stderr = self.stock_stderr
            # Update Label:
            self.download_label.SetLabel(f"Finished Installing {installer_name}")
            self.download_label.Centre(wx.HORIZONTAL)

            # Set Return to Main Menu into flash_installer_menu
            self.return_to_main_menu.SetLabel("Flash Installer")
            self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.flash_installer_menu)
            self.return_to_main_menu.Centre(wx.HORIZONTAL)
        else:
            sys.stdout = self.stock_stdout
            self.download_label.SetLabel(f"Failed to download {installer_name}")
            self.download_label.Centre(wx.HORIZONTAL)

    def flash_installer_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_WIDTH_MAIN, self.WINDOW_HEIGHT_MAIN)
        # Header
        self.header = wx.StaticText(self.frame, label="Select macOS Installer")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)
        # Subheader: Installers found in /Applications
        self.subheader = wx.StaticText(self.frame, label="Installers found in Applications folder")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        i = -7
        avalible_installers = installer.list_local_macOS_installers()
        if avalible_installers:
            print("Installer found")
            for app in avalible_installers:
                print(f"{avalible_installers[app]['Short Name']}: {avalible_installers[app]['Version']} ({avalible_installers[app]['Build']})")
                self.install_selection = wx.Button(self.frame, label=f"{avalible_installers[app]['Short Name']}: {avalible_installers[app]['Version']} ({avalible_installers[app]['Build']})", size=(300, 30))
                i = i + 25
                self.install_selection.SetPosition(
                    wx.Point(
                        self.header.GetPosition().x,
                        self.header.GetPosition().y + self.header.GetSize().height + i
                    )
                )
                self.install_selection.Bind(wx.EVT_BUTTON, lambda event, temp=app: self.format_usb_menu(avalible_installers[temp]['Path']))
                self.install_selection.Centre(wx.HORIZONTAL)
        else:
            print("No installers found")
            # Label: No Installers Found
            self.install_selection = wx.StaticText(self.frame, label="No Installers Found in Applications folder")
            self.install_selection.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.install_selection.SetPosition(
                # Set Position below header
                wx.Point(
                    self.header.GetPosition().x,
                    self.header.GetPosition().y + self.header.GetSize().height + 10
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
    
    def format_usb_menu(self, installer_path):
        self.frame.DestroyChildren()
        print(installer_path)

        # Header
        self.header = wx.StaticText(self.frame, label="Format USB")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: Selected USB will be erased, please backup your data
        self.subheader = wx.StaticText(self.frame, label="Selected USB will be erased, please backup your data")
        self.subheader.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)

        # Label: Select USB
        self.usb_selection_label = wx.StaticText(self.frame, label="Missing drives? Ensure they're 14GB+ and removable")
        self.usb_selection_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.usb_selection_label.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 10
            )
        )
        self.usb_selection_label.Centre(wx.HORIZONTAL)

        i = -15
        availible_disks = installer.list_disk_to_format()
        if availible_disks:
            print("Disks found")
            for disk in availible_disks:
                print(f"{disk}: {availible_disks[disk]['name']} - {availible_disks[disk]['size']}")
                self.usb_selection = wx.Button(self.frame, label=f"{disk} - {availible_disks[disk]['name']} - {utilities.human_fmt(availible_disks[disk]['size'])}", size=(300, 30))
                i = i + 25
                self.usb_selection.SetPosition(
                    wx.Point(
                        self.usb_selection_label.GetPosition().x,
                        self.usb_selection_label.GetPosition().y + self.usb_selection_label.GetSize().height + i
                    )
                )
                self.usb_selection.Bind(wx.EVT_BUTTON, lambda event, temp=disk: self.format_usb_progress(availible_disks[temp]['identifier'], installer_path))
                self.usb_selection.Centre(wx.HORIZONTAL)
        else:
            print("No disks found")
            # Label: No Disks Found
            self.usb_selection = wx.StaticText(self.frame, label="No Disks Found")
            self.usb_selection.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
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

    def format_usb_progress(self, disk, installer_path):
        self.frame.DestroyChildren()
        self.frame.SetSize(500, -1)
        # Header
        self.header = wx.StaticText(self.frame, label="Creating macOS Installer")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Label: Creating macOS Installer
        self.creating_macos_installer_label = wx.StaticText(self.frame, label="Formatting and flashing installer to drive")
        self.creating_macos_installer_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.creating_macos_installer_label.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
            )
        )
        self.creating_macos_installer_label.Centre(wx.HORIZONTAL)

        # Label: Developer Note: createinstallmedia output currently not implemented
        self.developer_note_label = wx.StaticText(self.frame, label="\tDeveloper Note: createinstallmedia output will print after finishing\nIf Application becomes unresponsive, this is due to slow USB flash drives.\n\tPlease do not close this window until the process is complete.")
        self.developer_note_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.developer_note_label.SetPosition(
            wx.Point(
                self.creating_macos_installer_label.GetPosition().x,
                self.creating_macos_installer_label.GetPosition().y + self.creating_macos_installer_label.GetSize().height + 10
            )
        )
        self.developer_note_label.Centre(wx.HORIZONTAL)

        # Textbox
        # Redirect stdout to a text box
        self.stdout_text = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.stdout_text.SetPosition(
            wx.Point(
                self.developer_note_label.GetPosition().x,
                self.developer_note_label.GetPosition().y + self.developer_note_label.GetSize().height + 10
            )
        )
        self.stdout_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        # Set width to same as frame
        self.stdout_text.SetSize(
            self.frame.GetSize().width,
            340)
        # Centre the text box to top of window
        self.stdout_text.Centre(wx.HORIZONTAL)
        self.stdout_text.SetValue("")

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.stdout_text.GetPosition().x,
                self.stdout_text.GetPosition().y + self.stdout_text.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        self.frame.Show()

        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
        wx.GetApp().Yield()
        # Create installer.sh script
        print("- Creating installer.sh script")
        print(f"- Disk: {disk}")
        print(f"- Installer: {installer_path}")
        if installer.generate_installer_creation_script(self.constants.installer_sh_path, installer_path, disk):
            print("- Sucessfully generated creation script")
            print("- Starting creation script as admin")
            wx.GetApp().Yield()
            time.sleep(1)
            args = [self.constants.oclp_helper_path, "/bin/sh", self.constants.installer_sh_path]
            sys.stdout = menu_redirect.RedirectText(self.stdout_text, True)
            sys.stderr = menu_redirect.RedirectText(self.stdout_text, True)
            run.Run()._stream_output(comm=args)
        else:
            print("- Failed to create installer script")
        sys.stdout = self.stock_stdout
        sys.stderr = self.stock_stderr

    
    def settings_menu(self, event=None):
        # Define Menu
        # - Header: Settings
        # - Dropdown: Model
        # - Chechboxes:
        #   - Verbose
        #   - Kext Debug
        #   - OpenCore Debug
        #   - SIP
        #   - SecureBootModel
        #   - Show Boot Picker
        # - Buttons:
        #   - Developer Settings
        # - Return to Main Menu

        self.frame.DestroyChildren()
        self.frame.SetSize(self.WINDOW_SETTINGS_WIDTH, self.WINDOW_SETTINGS_HEIGHT)
        self.frame.SetTitle("Settings")

        # Header
        self.header = wx.StaticText(self.frame, label="Settings")
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Dropdown
        self.dropdown_model = wx.Choice(self.frame)
        for model in model_array.SupportedSMBIOS:
            self.dropdown_model.Append(model)
        if self.computer.real_model not in self.dropdown_model.GetItems():
            # In the event an unsupported model is loaded, add it to the dropdown
            # Supported situation: If user wants to run on native model
            self.dropdown_model.Append(self.computer.real_model)
        self.dropdown_model.SetSelection(self.dropdown_model.GetItems().index(self.constants.custom_model or self.computer.real_model))
        self.dropdown_model.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 10
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
        self.checkbox_allow_native_models = wx.CheckBox(self.frame, label="Allow native models")
        self.checkbox_allow_native_models.SetValue(self.constants.allow_oc_everywhere)
        self.checkbox_allow_native_models.SetPosition(wx.Point(self.dropdown_model.GetPosition().x, self.dropdown_model.GetPosition().y + self.dropdown_model.GetSize().height + 10))
        self.checkbox_allow_native_models.Bind(wx.EVT_CHECKBOX, self.allow_native_models_click)
        self.checkbox_allow_native_models.ToolTip = wx.ToolTip("""Select to allow OpenCore to be installed on native models\nGenerally used for enabling OS features Apple locks out of native Macs\nie. AirPlay to Mac, Sidecar.""")

        # Checkbox: Verbose
        self.verbose_checkbox = wx.CheckBox(self.frame, label="Verbose")
        self.verbose_checkbox.SetValue(self.constants.verbose_debug)
        self.verbose_checkbox.SetPosition(wx.Point(self.checkbox_allow_native_models.GetPosition().x, self.checkbox_allow_native_models.GetPosition().y + self.checkbox_allow_native_models.GetSize().height))
        self.verbose_checkbox.Bind(wx.EVT_CHECKBOX, self.verbose_checkbox_click)
        self.verbose_checkbox.ToolTip = wx.ToolTip("""Add -v (verbose) to boot-args during build""")

        # Checkbox: Kext Debug
        self.kext_checkbox = wx.CheckBox(self.frame, label="Kext Debug")
        self.kext_checkbox.SetValue(self.constants.kext_debug)
        self.kext_checkbox.SetPosition(wx.Point(self.verbose_checkbox.GetPosition().x , self.verbose_checkbox.GetPosition().y + self.verbose_checkbox.GetSize().height))
        self.kext_checkbox.Bind(wx.EVT_CHECKBOX, self.kext_checkbox_click)
        self.kext_checkbox.ToolTip = wx.ToolTip("""Enables additional kext logging, including expanded message buffer""")

        # Checkbox: OpenCore Debug
        self.opencore_checkbox = wx.CheckBox(self.frame, label="OpenCore Debug")
        self.opencore_checkbox.SetValue(self.constants.opencore_debug)
        self.opencore_checkbox.SetPosition(wx.Point(self.kext_checkbox.GetPosition().x , self.kext_checkbox.GetPosition().y + self.kext_checkbox.GetSize().height))
        self.opencore_checkbox.Bind(wx.EVT_CHECKBOX, self.oc_checkbox_click)
        self.opencore_checkbox.ToolTip = wx.ToolTip("""Enables OpenCore logging, can heavily impact boot times""")

        # Checkbox: SecureBootModel
        self.secureboot_checkbox = wx.CheckBox(self.frame, label="SecureBootModel")
        self.secureboot_checkbox.SetValue(self.constants.secure_status)
        self.secureboot_checkbox.SetPosition(wx.Point(self.opencore_checkbox.GetPosition().x , self.opencore_checkbox.GetPosition().y + self.opencore_checkbox.GetSize().height))
        self.secureboot_checkbox.Bind(wx.EVT_CHECKBOX, self.secureboot_checkbox_click)
        self.secureboot_checkbox.ToolTip = wx.ToolTip("""Sets SecureBootModel, useful for models spoofing T2 Macs to get OTA updates""")

        # Checkbox: Show Boot Picker
        self.bootpicker_checkbox = wx.CheckBox(self.frame, label="Show Boot Picker")
        self.bootpicker_checkbox.SetValue(self.constants.showpicker)
        self.bootpicker_checkbox.SetPosition(wx.Point(self.secureboot_checkbox.GetPosition().x , self.secureboot_checkbox.GetPosition().y + self.secureboot_checkbox.GetSize().height))
        self.bootpicker_checkbox.Bind(wx.EVT_CHECKBOX, self.show_picker_checkbox_click)
        self.bootpicker_checkbox.ToolTip = wx.ToolTip("""Shows OpenCore's Boot Picker on machine start\nToggling this off will hide the picker, and only load when holding either Option or Escape""")

        # Checkbox: Allow Accel on Mojave/Catalina
        self.accel_checkbox = wx.CheckBox(self.frame, label="Allow Accel on 10.14/15")
        self.accel_checkbox.SetValue(self.constants.moj_cat_accel)
        self.accel_checkbox.SetPosition(wx.Point(self.bootpicker_checkbox.GetPosition().x , self.bootpicker_checkbox.GetPosition().y + self.bootpicker_checkbox.GetSize().height))
        self.accel_checkbox.Bind(wx.EVT_CHECKBOX, self.accel_checkbox_click)
        self.accel_checkbox.ToolTip = wx.ToolTip("""Allows Root Patching on Mojave/Catalina\nUseful for enabling TeraScale 2 Acceleration when not provided by dosdude1's patcher""")

        # Buttons
        
        # Button: SIP Settings
        if self.constants.custom_sip_value:
            sip_string = "Custom"
        elif self.constants.sip_status:
            sip_string = "Enabled"
        else:
            sip_string = "Lowered"
        self.sip_button = wx.Button(self.frame, label=f"SIP Settings ({sip_string})",  size=(155,30))
        self.sip_button.SetPosition(wx.Point(self.accel_checkbox.GetPosition().x , self.accel_checkbox.GetPosition().y + self.accel_checkbox.GetSize().height + 10))
        self.sip_button.Bind(wx.EVT_BUTTON, self.sip_config_menu)
        self.sip_button.Center(wx.HORIZONTAL)

        # Button: SMBIOS Settings
        self.smbios_button = wx.Button(self.frame, label="SMBIOS Settings",  size=(155,30))
        self.smbios_button.SetPosition(wx.Point(self.sip_button.GetPosition().x , self.sip_button.GetPosition().y + self.sip_button.GetSize().height))
        self.smbios_button.Bind(wx.EVT_BUTTON, self.smbios_settings_menu)
        self.smbios_button.Center(wx.HORIZONTAL)

        # Button: Developer Settings
        self.miscellaneous_button = wx.Button(self.frame, label="Developer Settings",  size=(155,30))
        self.miscellaneous_button.SetPosition(wx.Point(self.smbios_button.GetPosition().x , self.smbios_button.GetPosition().y + self.smbios_button.GetSize().height))
        self.miscellaneous_button.Bind(wx.EVT_BUTTON, self.misc_settings_menu)
        self.miscellaneous_button.Centre(wx.HORIZONTAL)

        self.return_to_main_menu = wx.Button(self.frame, label="Return to Main Menu", size=(155,30))
        self.return_to_main_menu.SetPosition(
            wx.Point(
                self.miscellaneous_button.GetPosition().x,
                self.miscellaneous_button.GetPosition().y + self.miscellaneous_button.GetSize().height + 10
            )
        )
        self.return_to_main_menu.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu.Centre(wx.HORIZONTAL)

        # Set frame size to below return_to_main_menu button
        self.frame.SetSize(-1, self.return_to_main_menu.GetPosition().y + self.return_to_main_menu.GetSize().height + 40)
    
    def model_choice_click(self, event=None):
        user_choice = self.dropdown_model.GetStringSelection()
        if user_choice == self.computer.real_model:
            print(f"Using Real Model: {user_choice}")
            self.constants.custom_model = None
            defaults.generate_defaults.probe(self.computer.real_model, True, self.constants)
        else:
            print(f"Using Custom Model: {user_choice}")
            self.constants.custom_model = user_choice
            defaults.generate_defaults.probe(self.constants.custom_model, False, self.constants)
        # Reload Settings
        self.settings_menu(None)

    def allow_native_models_click(self, event=None):
        if self.checkbox_allow_native_models.GetValue():
            print("Allow Native Models")
            self.constants.allow_oc_everywhere = True
            self.constants.serial_settings = "None"
        else:
            print("Disallow Native Models")
            self.constants.allow_oc_everywhere = False
            self.constants.serial_settings = "Minimal"
  
    def verbose_checkbox_click(self, event=None):
        if self.verbose_checkbox.GetValue():
            print("Verbose mode enabled")
            self.constants.verbose_debug = True
        else:
            print("Verbose mode disabled")
            self.constants.verbose_debug = False
    
    def kext_checkbox_click(self, event=None):
        if self.kext_checkbox.GetValue():
            print("Kext mode enabled")
            self.constants.kext_debug = True
        else:
            print("Kext mode disabled")
            self.constants.kext_debug = False
    
    def oc_checkbox_click(self, event=None):
        if self.opencore_checkbox.GetValue():
            print("OC mode enabled")
            self.constants.opencore_debug = True
            self.constants.opencore_build = "DEBUG"
        else:
            print("OC mode disabled")
            self.constants.opencore_debug = False
            self.constants.opencore_build = "RELEASE"
    
    def sip_checkbox_click(self, event=None):
        if self.sip_checkbox.GetValue():
            print("SIP mode enabled")
            self.constants.sip_status = True
        else:
            print("SIP mode disabled")
            self.constants.sip_status = False
    
    def secureboot_checkbox_click(self, event=None):
        if self.secureboot_checkbox.GetValue():
            print("SecureBoot mode enabled")
            self.constants.secure_status = True
        else:
            print("SecureBoot mode disabled")
            self.constants.secure_status = False
    
    def show_picker_checkbox_click(self, event=None):
        if self.bootpicker_checkbox.GetValue():
            print("Show Picker mode enabled")
            self.constants.showpicker = True
        else:
            print("Show Picker mode disabled")
            self.constants.showpicker = False
    
    def accel_checkbox_click(self, event=None):
        if self.accel_checkbox.GetValue():
            print("Legacy Accel mode enabled")
            self.constants.moj_cat_accel = True
        else:
            print("Legacy Accel mode disabled")
            self.constants.moj_cat_accel = False
    
    def misc_settings_menu(self, event=None):
        self.frame.DestroyChildren()

        # Header
        self.header = wx.StaticText(self.frame, label="Developer Settings", style=wx.ALIGN_CENTRE)
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.SetPosition(wx.Point(0, 10))
        self.header.SetSize(wx.Size(self.frame.GetSize().width, 30))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader: If unfamiliar with the following settings, please do not change them.
        self.subheader = wx.StaticText(self.frame, label="Do not change if unfamiliar", style=wx.ALIGN_CENTRE)
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subheader.SetPosition(wx.Point(0, self.header.GetPosition().y + self.header.GetSize().height))
        self.subheader.SetSize(wx.Size(self.frame.GetSize().width, 30))
        self.subheader.Centre(wx.HORIZONTAL)

        # Label: Set FeatreUnlock status
        self.feature_unlock_label = wx.StaticText(self.frame, label="Feature Unlock Status:", style=wx.ALIGN_CENTRE)
        self.feature_unlock_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.feature_unlock_label.SetPosition(wx.Point(0, self.subheader.GetPosition().y + self.subheader.GetSize().height -5))
        self.feature_unlock_label.Centre(wx.HORIZONTAL)

        # Dropdown: Set Feature Unlock status
        self.feature_unlock_dropdown = wx.Choice(self.frame)
        for entry in ["Enabled", "Paritally enabled (No AirPlay/SideCar)", "Disabled"]:
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
        self.feature_unlock_dropdown.SetToolTip(wx.ToolTip("Set whether FeatureUnlock support level\nBy default, full functionality is enabled. For systems experiencing memory instability, lowering this option to disable AirPlay/Sidecar patch sets is recommended."))

        # Label: Set GPU Model for MXM iMacs
        self.label_model = wx.StaticText(self.frame, label="Set GPU Model for MXM iMacs:", style=wx.ALIGN_CENTRE)
        self.label_model.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.label_model.SetPosition(wx.Point(0, self.feature_unlock_dropdown.GetPosition().y + self.feature_unlock_dropdown.GetSize().height + 2))
        self.label_model.SetSize(wx.Size(self.frame.GetSize().width, 30))
        self.label_model.Centre(wx.HORIZONTAL)

        # Dropdown: GPU Model
        self.gpu_dropdown = wx.Choice(self.frame)
        for gpu in ["None", "Nvidia Kepler", "AMD GCN", "AMD Polaris"]:
            self.gpu_dropdown.Append(gpu)
        self.gpu_dropdown.SetSelection(0)
        self.gpu_dropdown.SetPosition(wx.Point(
            self.label_model.GetPosition().x, 
            self.label_model.GetPosition().y + self.label_model.GetSize().height / 1.5))
        self.gpu_dropdown.Bind(wx.EVT_CHOICE, self.gpu_selection_click)
        self.gpu_dropdown.Centre(wx.HORIZONTAL)
        self.gpu_dropdown.SetToolTip(wx.ToolTip("Configures MXM GPU Vendor logic on pre-built models\nIf you are not using MXM iMacs, please leave this setting as is."))
        if self.computer.real_model not in ["iMac10,1", "iMac11,1", "iMac11,2", "iMac11,3", "iMac12,1", "iMac12,2"]:
            self.gpu_dropdown.Disable()

        # Checkbox List:
        # FireWire Boot
        # NVMe Boot
        # Wake on WLAN
        # Disable Thunderbolt
        # Set TeraScale 2 Accel
        # Windows GMUX
        # Hibernation Workaround
        # Disable Battery Throttling
        # Software Demux

        # FireWire Boot
        self.firewire_boot_checkbox = wx.CheckBox(self.frame, label="FireWire Boot")
        self.firewire_boot_checkbox.SetValue(self.constants.firewire_boot)
        self.firewire_boot_checkbox.Bind(wx.EVT_CHECKBOX, self.firewire_click)
        self.firewire_boot_checkbox.SetPosition(wx.Point(30, self.gpu_dropdown.GetPosition().y + self.gpu_dropdown.GetSize().height + 5))
        self.firewire_boot_checkbox.SetToolTip(wx.ToolTip("Enable FireWire Boot support in macOS 10.15 and newer.\nMainly applicable for Macs with FireWire or Thunderbolt to FireWire adapters"))
        if generate_smbios.check_firewire(self.computer.real_model) is False and not self.constants.custom_model:
            self.firewire_boot_checkbox.Disable()

        # NVMe Boot
        self.nvme_boot_checkbox = wx.CheckBox(self.frame, label="NVMe Boot")
        self.nvme_boot_checkbox.SetValue(self.constants.nvme_boot)
        self.nvme_boot_checkbox.Bind(wx.EVT_CHECKBOX, self.nvme_click)
        self.nvme_boot_checkbox.SetPosition(wx.Point(self.firewire_boot_checkbox.GetPosition().x, self.firewire_boot_checkbox.GetPosition().y + self.firewire_boot_checkbox.GetSize().height))
        self.nvme_boot_checkbox.SetToolTip(wx.ToolTip("Enables NVMe support in UEFI for non-native systems (ie. MacPro3,1)\nRequires OpenCore to be stored on a natively bootable volume however"))

        # Wake on WLAN
        self.wake_on_wlan_checkbox = wx.CheckBox(self.frame, label="Wake on WLAN")
        self.wake_on_wlan_checkbox.SetValue(self.constants.enable_wake_on_wlan)
        self.wake_on_wlan_checkbox.Bind(wx.EVT_CHECKBOX, self.wake_on_wlan_click)
        self.wake_on_wlan_checkbox.SetPosition(wx.Point(
            self.nvme_boot_checkbox.GetPosition().x,
            self.nvme_boot_checkbox.GetPosition().y + self.nvme_boot_checkbox.GetSize().height))
        self.wake_on_wlan_checkbox.SetToolTip(wx.ToolTip("Enables Wake on WLAN for Broadcom Wifi.\nBy default, Wake on WLAN is disabled to work around Apple's wake from sleep bug causing heavily degraded networking performance."))

        # Disable Thunderbolt
        self.disable_thunderbolt_checkbox = wx.CheckBox(self.frame, label="Disable Thunderbolt")
        self.disable_thunderbolt_checkbox.SetValue(self.constants.disable_tb)
        self.disable_thunderbolt_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_tb_click)
        self.disable_thunderbolt_checkbox.SetPosition(wx.Point(
            self.wake_on_wlan_checkbox.GetPosition().x,
            self.wake_on_wlan_checkbox.GetPosition().y + self.wake_on_wlan_checkbox.GetSize().height))
        self.disable_thunderbolt_checkbox.SetToolTip(wx.ToolTip("Disables Thunderbolt support on MacBookPro11,x\nMainly applicable for systems that cannot boot with Thunderbolt enabled"))
        if not self.constants.custom_model and not self.computer.real_model.startswith("MacBookPro11"):
            self.disable_thunderbolt_checkbox.Disable()
        # Set TeraScale 2 Accel
        self.set_terascale_accel_checkbox = wx.CheckBox(self.frame, label="Set TeraScale 2 Accel")
        self.set_terascale_accel_checkbox.SetValue(self.constants.allow_ts2_accel)
        self.set_terascale_accel_checkbox.Bind(wx.EVT_CHECKBOX, self.ts2_accel_click)
        self.set_terascale_accel_checkbox.SetPosition(wx.Point(
            self.disable_thunderbolt_checkbox.GetPosition().x,
            self.disable_thunderbolt_checkbox.GetPosition().y + self.disable_thunderbolt_checkbox.GetSize().height))
        self.set_terascale_accel_checkbox.SetToolTip(wx.ToolTip("This option will determine whether TeraScale 2 acceleration is avalible during Root Volume patching.\nOnly applicable if your system has a AMD TeraScale 2 GPU (ie. MacBookPro8,2/3)"))
        if self.computer.real_model not in ["MacBookPro8,2", "MacBookPro8,3"]:
            self.set_terascale_accel_checkbox.Disable()

        # Windows GMUX
        self.windows_gmux_checkbox = wx.CheckBox(self.frame, label="Windows GMUX")
        self.windows_gmux_checkbox.SetValue(self.constants.dGPU_switch)
        self.windows_gmux_checkbox.Bind(wx.EVT_CHECKBOX, self.windows_gmux_click)
        self.windows_gmux_checkbox.SetPosition(wx.Point(
            self.set_terascale_accel_checkbox.GetPosition().x,
            self.set_terascale_accel_checkbox.GetPosition().y + self.set_terascale_accel_checkbox.GetSize().height))
        self.windows_gmux_checkbox.SetToolTip(wx.ToolTip("Enable this option to allow usage of the hardware GMUX to switch between Intel and Nvidia/AMD GPUs in Windows."))

        # Hibernation Workaround
        self.hibernation_checkbox = wx.CheckBox(self.frame, label="Hibernation Workaround")
        self.hibernation_checkbox.SetValue(self.constants.disable_connectdrivers)
        self.hibernation_checkbox.Bind(wx.EVT_CHECKBOX, self.hibernation_click)
        self.hibernation_checkbox.SetPosition(wx.Point(
            self.windows_gmux_checkbox.GetPosition().x, 
            self.windows_gmux_checkbox.GetPosition().y + self.windows_gmux_checkbox.GetSize().height))
        self.hibernation_checkbox.SetToolTip(wx.ToolTip("This will disable the ConnectDrivers in OpenCore\nRecommended to toggle if your machine is having issues with hibernation.\nMainly applicable for MacBookPro9,1 and MacBookPro10,1"))

        # Disable Battery Throttling
        self.disable_battery_throttling_checkbox = wx.CheckBox(self.frame, label="Disable Battery Throttling")
        self.disable_battery_throttling_checkbox.SetValue(self.constants.disable_msr_power_ctl)
        self.disable_battery_throttling_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_battery_throttling_click)
        self.disable_battery_throttling_checkbox.SetPosition(wx.Point(
            self.hibernation_checkbox.GetPosition().x, 
            self.hibernation_checkbox.GetPosition().y + self.hibernation_checkbox.GetSize().height))
        self.disable_battery_throttling_checkbox.SetToolTip(wx.ToolTip("This will forcefully disable MSR Power Control on Arrendale and newer Laptops\nMainly applicable for systems with severe battery throttling"))

        # Software Demux
        self.software_demux_checkbox = wx.CheckBox(self.frame, label="Software Demux")
        self.software_demux_checkbox.SetValue(self.constants.software_demux)
        self.software_demux_checkbox.Bind(wx.EVT_CHECKBOX, self.software_demux_click)
        self.software_demux_checkbox.SetPosition(wx.Point(
            self.disable_battery_throttling_checkbox.GetPosition().x,
            self.disable_battery_throttling_checkbox.GetPosition().y + self.disable_battery_throttling_checkbox.GetSize().height))
        self.software_demux_checkbox.SetToolTip(wx.ToolTip("This will force a software based demux on MacBookPro8,2/3 aiding for better battery life\nThis will require the dGPU to be disabled via NVRAM"))
        if not self.constants.custom_model and self.computer.real_model not in ["MacBookPro8,2", "MacBookPro8,3"]:
            self.software_demux_checkbox.Disable()

        # Disable CPUFriend
        self.disable_cpu_friend_checkbox = wx.CheckBox(self.frame, label="Disable CPUFriend")
        self.disable_cpu_friend_checkbox.SetValue(self.constants.disallow_cpufriend)
        self.disable_cpu_friend_checkbox.Bind(wx.EVT_CHECKBOX, self.disable_cpu_friend_click)
        self.disable_cpu_friend_checkbox.SetPosition(wx.Point(
            self.software_demux_checkbox.GetPosition().x,
            self.software_demux_checkbox.GetPosition().y + self.software_demux_checkbox.GetSize().height))
        self.disable_cpu_friend_checkbox.SetToolTip(wx.ToolTip("This will disable CPUFriend on your system when using Minimal or higher SMBIOS spoofing.\nMainly applicable for older iMacs (2007-9) that wish to disable CPU throttling"))
        if self.constants.serial_settings == "None":
            self.disable_cpu_friend_checkbox.Disable()

        # AppleALC Usage
        self.apple_alc_checkbox = wx.CheckBox(self.frame, label="AppleALC Usage")
        self.apple_alc_checkbox.SetValue(self.constants.set_alc_usage)
        self.apple_alc_checkbox.Bind(wx.EVT_CHECKBOX, self.apple_alc_click)
        self.apple_alc_checkbox.SetPosition(wx.Point(
            self.disable_cpu_friend_checkbox.GetPosition().x, 
            self.disable_cpu_friend_checkbox.GetPosition().y + self.disable_cpu_friend_checkbox.GetSize().height))
        self.apple_alc_checkbox.SetToolTip(wx.ToolTip("This will set whether AppleALC is allowed to be used during config building.\nMainly applicable for MacPro3,1s that do not have boot screen support, thus preventing AppleALC from working."))

        # Set WriteFlash
        self.set_writeflash_checkbox = wx.CheckBox(self.frame, label="Set NVRAM WriteFlash")
        self.set_writeflash_checkbox.SetValue(self.constants.nvram_write)
        self.set_writeflash_checkbox.Bind(wx.EVT_CHECKBOX, self.set_writeflash_click)
        self.set_writeflash_checkbox.SetPosition(wx.Point(
            self.apple_alc_checkbox.GetPosition().x,
            self.apple_alc_checkbox.GetPosition().y + self.apple_alc_checkbox.GetSize().height))
        self.set_writeflash_checkbox.SetToolTip(wx.ToolTip("This will set whether OpenCore is allowed to write to hardware NVRAM.\nDisable this option if your system has degraded or fragile NVRAM."))
        # Set Enhanced 3rd Party SSD
        self.set_enhanced_3rd_party_ssd_checkbox = wx.CheckBox(self.frame, label="Enhanced SSD Support")
        self.set_enhanced_3rd_party_ssd_checkbox.SetValue(self.constants.allow_3rd_party_drives)
        self.set_enhanced_3rd_party_ssd_checkbox.Bind(wx.EVT_CHECKBOX, self.set_enhanced_3rd_party_ssd_click)
        self.set_enhanced_3rd_party_ssd_checkbox.SetPosition(wx.Point(
            self.set_writeflash_checkbox.GetPosition().x,
            self.set_writeflash_checkbox.GetPosition().y + self.set_writeflash_checkbox.GetSize().height))
        self.set_enhanced_3rd_party_ssd_checkbox.SetToolTip(wx.ToolTip("This will set whether OpenCore is allowed to force Apple Vendor on 3rd Party SATA SSDs\nSome benefits from this patch include better SSD performance, TRIM support and hibernation support.\nDisable this option if your SSD does not support TRIM correctly"))
        if self.computer.third_party_sata_ssd is False and not self.constants.custom_model:
            self.set_enhanced_3rd_party_ssd_checkbox.Disable()

        
        # Button: Developer Debug Info
        self.debug_button = wx.Button(self.frame, label="Developer Debug Info")
        self.debug_button.Bind(wx.EVT_BUTTON, self.additional_info_menu)
        self.debug_button.SetPosition(wx.Point(
            self.set_enhanced_3rd_party_ssd_checkbox.GetPosition().x,
            self.set_enhanced_3rd_party_ssd_checkbox.GetPosition().y + self.set_enhanced_3rd_party_ssd_checkbox.GetSize().height + 5))
        self.debug_button.Center(wx.HORIZONTAL)
        
        # Button: return to main menu
        self.return_to_main_menu_button = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu_button.SetPosition(wx.Point(
            self.debug_button.GetPosition().x,
            self.debug_button.GetPosition().y + self.debug_button.GetSize().height + 10))
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        # set frame size below return to main menu button
        self.frame.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
    
    def firewire_click(self, event=None):
        if self.firewire_boot_checkbox.GetValue():
            print("Firewire Enabled")
            self.constants.firewire_boot = True
        else:
            print("Firewire Disabled")
            self.constants.firewire_boot = False
    
    def nvme_click(self, event=None):
        if self.nvme_boot_checkbox.GetValue():
            print("NVMe Enabled")
            self.constants.nvme_boot = True
        else:
            print("NVMe Disabled")
            self.constants.nvme_boot = False
    
    def wake_on_wlan_click(self, event=None):
        if self.wake_on_wlan_checkbox.GetValue():
            print("Wake on WLAN Enabled")
            self.constants.enable_wake_on_wlan = True
        else:
            print("Wake on WLAN Disabled")
            self.constants.enable_wake_on_wlan = False
    
    def disable_tb_click(self, event=None):
        if self.disable_thunderbolt_checkbox.GetValue():
            print("Disable Thunderbolt Enabled")
            self.constants.disable_tb = True
        else:
            print("Disable Thunderbolt Disabled")
            self.constants.disable_tb = False
    
    def ts2_accel_click(self, event=None):
        if self.set_terascale_accel_checkbox.GetValue():
            print("TS2 Acceleration Enabled")
            self.constants.allow_ts2_accel = True
        else:
            print("TS2 Acceleration Disabled")
            self.constants.allow_ts2_accel = False
    
    def windows_gmux_click(self, event=None):    
        if self.windows_gmux_checkbox.GetValue():
            print("Windows GMUX Enabled")
            self.constants.dGPU_switch = True
        else:
            print("Windows GMUX Disabled")
            self.constants.dGPU_switch = False
    
    def hibernation_click(self, event=None):    
        if self.hibernation_checkbox.GetValue():
            print("Hibernation Enabled")
            self.constants.disable_connectdrivers = True
        else:
            print("Hibernation Disabled")
            self.constants.disable_connectdrivers = False
    
    def disable_battery_throttling_click(self, event=None):
        if self.disable_battery_throttling_checkbox.GetValue():
            print("Disable Battery Throttling Enabled")
            self.constants.disable_msr_power_ctl = True
        else:
            print("Disable Battery Throttling Disabled")
            self.constants.disable_msr_power_ctl = False

    def software_demux_click(self, event=None):
        if self.software_demux_checkbox.GetValue():
            print("Software Demux Enabled")
            self.constants.software_demux = True
        else:
            print("Software Demux Disabled")
            self.constants.software_demux = False

    def disable_cpu_friend_click(self, event=None):
        if self.disable_cpu_friend_checkbox.GetValue():
            print("Disable CPUFriend Enabled")
            self.constants.disallow_cpufriend = True
        else:
            print("Disable CPUFriend Disabled")
            self.constants.disallow_cpufriend = False
    
    def apple_alc_click(self, event=None):
        if self.apple_alc_checkbox.GetValue():
            print("AppleALC Usage Enabled")
            self.constants.set_alc_usage = True
        else:
            print("AppleALC Usage Disabled")
            self.constants.set_alc_usage = False
    
    def set_enhanced_3rd_party_ssd_click(self, event=None):
        if self.set_enhanced_3rd_party_ssd_checkbox.GetValue():
            print("Enhanced 3rd Party SSDs Enabled")
            self.constants.allow_3rd_party_drives = True
        else:
            print("Enhanced 3rd Party SSDs Disabled")
            self.constants.allow_3rd_party_drives = False

    def gpu_selection_click(self, event=None):
        gpu_choice =  self.gpu_dropdown.GetStringSelection()
        print(f"GPU Selection: {gpu_choice}")
        if "AMD" in gpu_choice:
            self.constants.imac_vendor = "AMD"
            self.constants.metal_build = True
            if "Polaris" in gpu_choice:
                self.constants.imac_model = "Polaris"
            elif "GCN" in gpu_choice:
                self.constants.imac_model = "Legacy GCN"
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
        
        print(f"GPU Vendor: {self.constants.imac_vendor}")
        print(f"GPU Model: {self.constants.imac_model}")
    
    def fu_selection_click(self, event=None):
        fu_choice =  self.feature_unlock_dropdown.GetStringSelection()
        if fu_choice == "Enabled":
            self.constants.fu_status = True
            self.constants.fu_arguments = None
        elif fu_choice == "Paritally enabled (No AirPlay/SideCar)":
            self.constants.fu_status = True
            self.constants.fu_arguments = " -disable_sidecar_mac"
        else:
            self.constants.fu_status = False
            self.constants.fu_arguments = None
    
    def set_writeflash_click(self, event=None):
        if self.set_writeflash_checkbox.GetValue():
            print("Write Flash Enabled")
            self.constants.nvram_write = True
        else:
            print("Write Flash Disabled")
            self.constants.nvram_write = False

    def smbios_settings_menu(self, event=None):
        self.frame.DestroyChildren()

        # Header: SMBIOS Settings
        self.smbios_settings_header = wx.StaticText(self.frame, label="SMBIOS Settings", pos=wx.Point(10, 10))
        self.smbios_settings_header.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.smbios_settings_header.Center(wx.HORIZONTAL)

        # Label: SMBIOS Spoof Level
        self.smbios_spoof_level_label = wx.StaticText(self.frame, label="SMBIOS Spoof Level")
        self.smbios_spoof_level_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.smbios_spoof_level_label.SetPosition(
            wx.Point(self.smbios_settings_header.GetPosition().x, self.smbios_settings_header.GetPosition().y + self.smbios_settings_header.GetSize().height + 10)
        )
        self.smbios_spoof_level_label.Center(wx.HORIZONTAL)

        # Dropdown: SMBIOS Spoof Level
        self.smbios_dropdown = wx.Choice(self.frame)
        self.smbios_dropdown.SetPosition(
            wx.Point(self.smbios_spoof_level_label.GetPosition().x, self.smbios_spoof_level_label.GetPosition().y + self.smbios_spoof_level_label.GetSize().height + 10)
        )
        self.smbios_dropdown.AppendItems(["None", "Minimal", "Moderate", "Advanced"])
        self.smbios_dropdown.SetStringSelection(self.constants.serial_settings)
        self.smbios_dropdown.Bind(wx.EVT_CHOICE, self.smbios_spoof_level_click)
        self.smbios_dropdown.Center(wx.HORIZONTAL)

        # Label: SMBIOS Spoof Model
        self.smbios_spoof_model_label = wx.StaticText(self.frame, label="SMBIOS Spoof Model")
        self.smbios_spoof_model_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.smbios_spoof_model_label.SetPosition(
            wx.Point(self.smbios_dropdown.GetPosition().x, self.smbios_dropdown.GetPosition().y + self.smbios_dropdown.GetSize().height + 10)
        )
        self.smbios_spoof_model_label.Center(wx.HORIZONTAL)

        # Dropdown: SMBIOS Spoof Model
        self.smbios_model_dropdown = wx.Choice(self.frame)
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

        # Button: Return to Main Menu
        self.return_to_main_menu_button = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu_button.SetPosition(
            wx.Point(self.smbios_model_dropdown.GetPosition().x, self.smbios_model_dropdown.GetPosition().y + self.smbios_model_dropdown.GetSize().height + 10)
        )
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        self.frame.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))


    
    def smbios_spoof_level_click(self, event=None):
        selection = self.smbios_dropdown.GetStringSelection()
        print(f"SMBIOS Spoof Level: {selection}")
        self.constants.serial_settings = selection
    
    def smbios_model_click(self, event=None):
        selection = self.smbios_model_dropdown.GetStringSelection()
        print(f"SMBIOS Spoof Model: {selection}")
        self.constants.override_smbios = selection
    
    def additional_info_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(wx.Size(500, -1))

        # Header: Additional Info
        self.additional_info_header = wx.StaticText(self.frame, label="Developer Debug Info", pos=wx.Point(10, 10))
        self.additional_info_header.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.additional_info_header.Center(wx.HORIZONTAL)

        # Label: Real User ID
        self.real_user_id_label = wx.StaticText(self.frame, label=f"Current UID: {os.getuid()} - ({os.geteuid()})")
        self.real_user_id_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.real_user_id_label.SetPosition(
            wx.Point(self.additional_info_header.GetPosition().x, self.additional_info_header.GetPosition().y + self.additional_info_header.GetSize().height + 10)
        )
        self.real_user_id_label.Center(wx.HORIZONTAL)

        # Label: Model Dump
        self.model_dump_label = wx.StaticText(self.frame, label="Model Dump")
        self.model_dump_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.model_dump_label.SetPosition(
            wx.Point(self.real_user_id_label.GetPosition().x, self.real_user_id_label.GetPosition().y + self.real_user_id_label.GetSize().height + 10)
        )
        self.model_dump_label.Center(wx.HORIZONTAL)

        # Textbox: Model Dump
        self.model_dump_textbox = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE, pos=wx.Point(self.model_dump_label.GetPosition().x, self.model_dump_label.GetPosition().y + self.model_dump_label.GetSize().height + 10))
        self.model_dump_textbox.SetValue(str(self.constants.computer))
        self.model_dump_textbox.SetPosition(
            wx.Point(self.model_dump_label.GetPosition().x, self.model_dump_label.GetPosition().y + self.model_dump_label.GetSize().height + 10)
        )
        self.model_dump_textbox.SetSize(
            wx.Size(
                self.frame.GetSize().width - 5, 
                self.model_dump_textbox.GetSize().height + self.model_dump_textbox.GetSize().height
            )
        )
        self.model_dump_textbox.Center(wx.HORIZONTAL)
        self.model_dump_textbox.SetEditable(False)
        
        

        # Label: Launcher Binary
        self.launcher_binary_label = wx.StaticText(self.frame, label="Launcher Binary")
        self.launcher_binary_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.launcher_binary_label.SetPosition(
            wx.Point(self.model_dump_textbox.GetPosition().x, self.model_dump_textbox.GetPosition().y + self.model_dump_textbox.GetSize().height + 10)
        )
        self.launcher_binary_label.Center(wx.HORIZONTAL)

        # Textbox: Launcher Binary
        self.launcher_binary_textbox = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE, pos=wx.Point(self.launcher_binary_label.GetPosition().x, self.launcher_binary_label.GetPosition().y + self.launcher_binary_label.GetSize().height + 10))
        self.launcher_binary_textbox.SetValue(self.constants.launcher_binary)
        self.launcher_binary_textbox.SetPosition(
            wx.Point(self.launcher_binary_label.GetPosition().x, self.launcher_binary_label.GetPosition().y + self.launcher_binary_label.GetSize().height + 10)
        )
        self.launcher_binary_textbox.SetSize(wx.Size(self.frame.GetSize().width - 5, 50))
        self.launcher_binary_textbox.Center(wx.HORIZONTAL)
        self.launcher_binary_textbox.SetEditable(False)

        # Label: Launcher Script
        self.launcher_script_label = wx.StaticText(self.frame, label="Launcher Script")
        self.launcher_script_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.launcher_script_label.SetPosition(
            wx.Point(self.launcher_binary_textbox.GetPosition().x, self.launcher_binary_textbox.GetPosition().y + self.launcher_binary_textbox.GetSize().height + 10)
        )
        self.launcher_script_label.Center(wx.HORIZONTAL)

        # Textbox: Launcher Script
        self.launcher_script_textbox = wx.TextCtrl(self.frame, style=wx.TE_MULTILINE, pos=wx.Point(self.launcher_script_label.GetPosition().x, self.launcher_script_label.GetPosition().y + self.launcher_script_label.GetSize().height + 10))
        self.launcher_script_textbox.SetValue(str(self.constants.launcher_script))
        self.launcher_script_textbox.SetPosition(
            wx.Point(self.launcher_script_label.GetPosition().x, self.launcher_script_label.GetPosition().y + self.launcher_script_label.GetSize().height + 10)
        )
        self.launcher_script_textbox.SetSize(wx.Size(self.frame.GetSize().width - 5, 60))
        self.launcher_script_textbox.Center(wx.HORIZONTAL)
        self.launcher_script_textbox.SetEditable(False)

        self.return_to_main_menu_button = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu_button.SetPosition(
            wx.Point(self.launcher_script_textbox.GetPosition().x, self.launcher_script_textbox.GetPosition().y + self.launcher_script_textbox.GetSize().height + 10)
        )
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)
        
        # Set frame below return to main menu button
        self.frame.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))

    
    def sip_config_menu(self, event=None):
        self.frame.DestroyChildren()
        self.frame.SetSize(wx.Size(400, 600))

        # Title: Configure SIP
        self.configure_sip_title = wx.StaticText(self.frame, label="Configure SIP")
        self.configure_sip_title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.configure_sip_title.Center(wx.HORIZONTAL)

        # Label: Flip indivdual bits corresponding to XNU's csr.h
        # If you're unfamiliar with how SIP works, do not touch this menu
        self.sip_label = wx.StaticText(self.frame, label="Flip indivdual bits corresponding to")
        self.sip_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.sip_label.SetPosition(
            wx.Point(-1, self.configure_sip_title.GetPosition().y + self.configure_sip_title.GetSize().height + 10)
        )
        self.sip_label.Center(wx.HORIZONTAL)
        self.sip_label.SetPosition(
            wx.Point(self.sip_label.GetPosition().x - 25, -1)
        )
        
        hyperlink_label = hyperlink.HyperLinkCtrl(
            self.frame,
            -1, 
            "XNU's csr.h", 
            pos=(self.sip_label.GetPosition().x + self.sip_label.GetSize().width, self.sip_label.GetPosition().y), 
            URL="https://github.com/apple/darwin-xnu/blob/main/bsd/sys/csr.h",
        )
        hyperlink_label.SetForegroundColour((25, 179, 231))

        if self.constants.custom_sip_value is not None:
            self.sip_value = int(self.constants.custom_sip_value, 16)
        elif self.constants.sip_status is True:
            self.sip_value = 0x00
        else:
            self.sip_value = 0xa03
        
        self.sip_label_2 = wx.StaticText(self.frame, label=f"Currently configured SIP: {hex(self.sip_value)}")
        self.sip_label_2.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sip_label_2.SetPosition(
            wx.Point(self.sip_label.GetPosition().x, self.sip_label.GetPosition().y + self.sip_label.GetSize().height + 10)
        )
        self.sip_label_2.Center(wx.HORIZONTAL)

        self.sip_label_3 = wx.StaticText(self.frame, label="For older Macs requiring root patching, we set SIP to\n be partially disabled (0xa03) to allow root patching.")
        self.sip_label_3.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.sip_label_3.SetPosition(
            wx.Point(self.sip_label_2.GetPosition().x, self.sip_label_2.GetPosition().y + self.sip_label_2.GetSize().height + 10)
        )
        self.sip_label_3.Center(wx.HORIZONTAL)

        self.sip_label_4 = wx.StaticText(self.frame, label="This value (0xa03) corresponds to the following bits in csr.h:")
        self.sip_label_4.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.sip_label_4.SetPosition(
            wx.Point(self.sip_label_3.GetPosition().x, self.sip_label_3.GetPosition().y + self.sip_label_3.GetSize().height + 5)
        )
        self.sip_label_4.Center(wx.HORIZONTAL)

        self.sip_label_5 = wx.StaticText(self.frame, label="   0x1     - CSR_ALLOW_UNTRUSTED_KEXTS\n   0x2     - CSR_ALLOW_UNRESTRICTED_FS\n   0x200 - CSR_ALLOW_UNAPPROVED_KEXTS\n   0x800 - CSR_ALLOW_UNAUTHENTICATED_ROOT")
        self.sip_label_5.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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
        self.sip_label_6 = wx.StaticText(self.frame, label=warning_string)
        self.sip_label_6.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.sip_label_6.SetPosition(
            wx.Point(self.sip_label_5.GetPosition().x, self.sip_label_5.GetPosition().y + self.sip_label_5.GetSize().height - 10)
        )
        self.sip_label_6.Center(wx.HORIZONTAL)

        i = -10
        for sip_bit in sip_data.system_integrity_protection.csr_values_extended:
            self.sip_checkbox = wx.CheckBox(self.frame, label=sip_data.system_integrity_protection.csr_values_extended[sip_bit]["name"])
            self.sip_checkbox.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            self.sip_checkbox.SetToolTip(f'Description: {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["description"]}\nValue: {hex(sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"])}\nIntroduced in: macOS {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["introduced_friendly"]}')
            self.sip_checkbox.SetPosition(
                wx.Point(70, self.sip_label_6.GetPosition().y + self.sip_label_6.GetSize().height + i)
            )
            i = i + 20
            self.sip_checkbox.Bind(wx.EVT_CHECKBOX, self.update_sip_value)
            if self.sip_value & sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"] == sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"]:
                self.sip_checkbox.SetValue(True)
        
        # Button: returns to the main menu
        self.return_to_main_menu_button = wx.Button(self.frame, label="Return to Main Menu")
        self.return_to_main_menu_button.SetPosition(
            wx.Point(self.sip_checkbox.GetPosition().x, self.sip_checkbox.GetPosition().y + self.sip_checkbox.GetSize().height + 15)
        )
        self.return_to_main_menu_button.Bind(wx.EVT_BUTTON, self.main_menu)
        self.return_to_main_menu_button.Center(wx.HORIZONTAL)

        # Set the frame size
        self.frame.SetSize(wx.Size(-1, self.return_to_main_menu_button.GetPosition().y + self.return_to_main_menu_button.GetSize().height + 40))
    
    def update_sip_value(self, event):
        dict = sip_data.system_integrity_protection.csr_values_extended[event.GetEventObject().GetLabel()]
        if event.GetEventObject().GetValue() is True:
            self.sip_value = self.sip_value + dict["value"]
        else:
            self.sip_value = self.sip_value - dict["value"]
        if hex(self.sip_value) == "0x0":
            self.constants.custom_sip_value = None
            self.constants.sip_status = True
        elif hex(self.sip_value) == "0xa03":
            self.constants.custom_sip_value = None
            self.constants.sip_status = False
        else:
            self.constants.custom_sip_value = hex(self.sip_value)
        self.sip_label_2.SetLabel(f"Currently configured SIP: {hex(self.sip_value)}")
        self.sip_label_2.Center(wx.HORIZONTAL)