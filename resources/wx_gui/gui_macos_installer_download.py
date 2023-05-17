import wx
import logging
import threading

from pathlib import Path

from resources.wx_gui import (
    gui_main_menu,
    gui_support,
    gui_download,
    gui_macos_installer_flash
)
from resources import (
    constants,
    macos_installer_handler,
    utilities,
    network_handler,
    integrity_verification
)


class macOSInstallerDownloadFrame(wx.Frame):
    """
    Create a frame for downloading and creating macOS installers
    Uses a Modal Dialog for smoother transition from other frames
    Note: Flashing installers is passed to gui_macos_installer_flash.py
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):

        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.parent: wx.Frame = parent

        self.available_installers = None
        self.available_installers_latest = None

        self.frame_modal = wx.Dialog(parent, title=title, size=(330, 200))

        self._generate_elements(self.frame_modal)
        self.frame_modal.ShowWindowModal()


    def _generate_elements(self, frame: wx.Frame = None) -> None:
        """
        Format:
        - Title:  Create macOS Installer
        - Button: Download macOS Installer
        - Button: Use existing macOS Installer
        - Button: Return to Main Menu
        """

        frame = self if not frame else frame

        title_label = wx.StaticText(frame, label="Create macOS Installer", pos=(-1,5))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Center(wx.HORIZONTAL)

        # Button: Download macOS Installer
        download_button = wx.Button(frame, label="Download macOS Installer", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5), size=(200, 30))
        download_button.Bind(wx.EVT_BUTTON, self.on_download)
        download_button.Center(wx.HORIZONTAL)

        # Button: Use existing macOS Installer
        existing_button = wx.Button(frame, label="Use existing macOS Installer", pos=(-1, download_button.GetPosition()[1] + download_button.GetSize()[1] - 5), size=(200, 30))
        existing_button.Bind(wx.EVT_BUTTON, self.on_existing)
        existing_button.Center(wx.HORIZONTAL)

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(-1, existing_button.GetPosition()[1] + existing_button.GetSize()[1] + 5), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return)
        return_button.Center(wx.HORIZONTAL)

        # Set size of frame
        frame.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))


    def _generate_catalog_frame(self) -> None:
        """
        Generate frame to display available installers
        """
        super(macOSInstallerDownloadFrame, self).__init__(None, title=self.title, size=(300, 200), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetPosition((self.parent.GetPosition()[0], self.parent.GetPosition()[1]))

        # Title: Pulling installer catalog
        title_label = wx.StaticText(self, label="Pulling installer catalog", pos=(-1,5))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Center(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(self, range=100, pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5), size=(250, 30))
        progress_bar.Center(wx.HORIZONTAL)
        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        # Set size of frame
        self.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 40))

        self.Show()

        # Grab installer catalog
        def _fetch_installers():
            remote_obj = macos_installer_handler.RemoteInstallerCatalog(seed_override=macos_installer_handler.SeedType.DeveloperSeed)
            self.available_installers        = remote_obj.available_apps
            self.available_installers_latest = remote_obj.available_apps_latest

        thread = threading.Thread(target=_fetch_installers)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        progress_bar_animation.stop_pulse()
        progress_bar.Hide()
        self._display_available_installers()


    def _display_available_installers(self, event: wx.Event = None, show_full: bool = False) -> None:
        """
        Display available installers in frame
        """
        self.frame_modal.Destroy()
        dialog = wx.Dialog(self, title="Select macOS Installer", size=(300, 200))

        # Title: Select macOS Installer
        title_label = wx.StaticText(dialog, label="Select macOS Installer", pos=(-1,5))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Center(wx.HORIZONTAL)

        # Subtitle: Installers currently available from Apple:
        subtitle_label = wx.StaticText(dialog, label="Installers currently available from Apple:", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
        subtitle_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        subtitle_label.Center(wx.HORIZONTAL)

        # List of installers
        installers = self.available_installers_latest if show_full is False else self.available_installers
        if installers:
            spacer = 0
            for app in installers:
                logging.info(f"macOS {installers[app]['Version']} ({installers[app]['Build']}):\n  - Size: {utilities.human_fmt(installers[app]['Size'])}\n  - Source: {installers[app]['Source']}\n  - Variant: {installers[app]['Variant']}\n  - Link: {installers[app]['Link']}\n")
                extra = " Beta" if installers[app]['Variant'] in ["DeveloperSeed" , "PublicSeed"] else ""

                installer_button = wx.Button(dialog, label=f"macOS {installers[app]['Version']}{extra} ({installers[app]['Build']} - {utilities.human_fmt(installers[app]['Size'])})", pos=(-1, subtitle_label.GetPosition()[1] + subtitle_label.GetSize()[1] + 5 + spacer), size=(270, 30))
                installer_button.Bind(wx.EVT_BUTTON, lambda event, temp=app: self.on_download_installer(installers[temp]))
                installer_button.Center(wx.HORIZONTAL)
                spacer += 25

                # Since installers are sorted by version, set the latest installer as the default button
                # Note that on full display, the last installer is generally a beta
                if show_full is False and app == list(installers.keys())[-1]:
                    installer_button.SetDefault()

        # Show all available installers
        show_all_button = wx.Button(dialog, label="Show all available installers" if show_full is False else "Show only latest installers", pos=(-1, installer_button.GetPosition()[1] + installer_button.GetSize()[1]), size=(200, 30))
        show_all_button.Bind(wx.EVT_BUTTON, lambda event: self._display_available_installers(event, not show_full))
        show_all_button.Center(wx.HORIZONTAL)

        # Return to Main Menu
        return_button = wx.Button(dialog, label="Return to Main Menu", pos=(-1, show_all_button.GetPosition()[1] + show_all_button.GetSize()[1] - 7), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.Center(wx.HORIZONTAL)

        # Set size of frame
        dialog.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))
        dialog.ShowWindowModal()
        self.frame_modal = dialog


    def on_download_installer(self, app: dict) -> None:
        """
        Download macOS installer
        """
        host_space = utilities.get_free_space()
        needed_space = app['Size'] * 2
        if host_space < needed_space:
            dlg = wx.MessageDialog(self.frame_modal, f"You do not have enough free space to download and extract this installer. Please free up some space and try again\n\n{utilities.human_fmt(host_space)} available vs {utilities.human_fmt(needed_space)} required", "Insufficient Space", wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            return

        self.frame_modal.Close()

        download_obj = network_handler.DownloadObject(app['Link'], self.constants.payload_path / "InstallAssistant.pkg")

        gui_download.DownloadFrame(
            self,
            title=self.title,
            global_constants=self.constants,
            download_obj=download_obj,
            item_name=f"macOS {app['Version']} ({app['Build']})",
        )

        if download_obj.download_complete is False:
            self.on_return_to_main_menu()
            return

        self._validate_installer(app['integrity'])


    def _validate_installer(self, chunklist_link: str) -> None:
        """
        Validate macOS installer
        """
        self.SetSize((300, 200))
        for child in self.GetChildren():
            child.Destroy()

        # Title: Validating macOS Installer
        title_label = wx.StaticText(self, label="Validating macOS Installer", pos=(-1,5))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Center(wx.HORIZONTAL)

        # Label: Validating chunk 0 of 0
        chunk_label = wx.StaticText(self, label="Validating chunk 0 of 0", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
        chunk_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        chunk_label.Center(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(self, range=100, pos=(-1, chunk_label.GetPosition()[1] + chunk_label.GetSize()[1] + 5), size=(270, 30))
        progress_bar.Center(wx.HORIZONTAL)

        # Set size of frame
        self.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 40))
        self.Show()

        chunklist_stream = network_handler.NetworkUtilities().get(chunklist_link).content
        if chunklist_stream:
            utilities.disable_sleep_while_running()
            chunk_obj = integrity_verification.ChunklistVerification(self.constants.payload_path / Path("InstallAssistant.pkg"), chunklist_stream)
            if chunk_obj.chunks:
                progress_bar.SetValue(chunk_obj.current_chunk)
                progress_bar.SetRange(chunk_obj.total_chunks)

                wx.App.Get().Yield()
                chunk_obj.validate()

                while chunk_obj.status == integrity_verification.ChunklistStatus.IN_PROGRESS:
                    progress_bar.SetValue(chunk_obj.current_chunk)
                    chunk_label.SetLabel(f"Validating chunk {chunk_obj.current_chunk} of {chunk_obj.total_chunks}")
                    chunk_label.Center(wx.HORIZONTAL)
                    wx.App.Get().Yield()

                if chunk_obj.status == integrity_verification.ChunklistStatus.FAILURE:
                    wx.MessageBox("Chunklist validation failed.\n\nThis generally happens when downloading on unstable connections such as WiFi or cellular.\n\nPlease try redownloading again on a stable connection (ie. Ethernet)", "Corrupted Installer!", wx.OK | wx.ICON_ERROR)
                    self.on_return_to_main_menu()
                    return

        # Extract installer
        title_label.SetLabel("Extracting macOS Installer")
        title_label.Center(wx.HORIZONTAL)

        chunk_label.SetLabel("May take a few minutes...")
        chunk_label.Center(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        # Start thread to extract installer
        self.result = False
        def extract_installer():
            self.result = macos_installer_handler.InstallerCreation().install_macOS_installer(self.constants.payload_path)

        thread = threading.Thread(target=extract_installer)
        thread.start()

        # Show frame
        self.Show()

        # Wait for thread to finish
        while thread.is_alive():
            wx.Yield()

        progress_bar_animation.stop_pulse()
        progress_bar.Hide()
        chunk_label.SetLabel("Successfully extracted macOS installer" if self.result is True else "Failed to extract macOS installer")
        chunk_label.Center(wx.HORIZONTAL)

        # Create macOS Installer button
        create_installer_button = wx.Button(self, label="Create macOS Installer", pos=(-1, progress_bar.GetPosition()[1]), size=(170, 30))
        create_installer_button.Bind(wx.EVT_BUTTON, self.on_existing)
        create_installer_button.Center(wx.HORIZONTAL)
        if self.result is False:
            create_installer_button.Disable()

        # Return to main menu button
        return_button = wx.Button(self, label="Return to Main Menu", pos=(-1, create_installer_button.GetPosition()[1] + create_installer_button.GetSize()[1]), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.Center(wx.HORIZONTAL)

        # Set size of frame
        self.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))

        # Show frame
        self.Show()

        if self.result is False:
            wx.MessageBox("An error occurred while extracting the macOS installer. Could be due to a corrupted installer", "Error", wx.OK | wx.ICON_ERROR)
            return

        user_input = wx.MessageBox("Finished extracting the installer, would you like to continue and create a macOS installer?", "Create macOS Installer?", wx.YES_NO | wx.ICON_QUESTION)
        if user_input == wx.YES:
            self.on_existing()


    def on_download(self, event: wx.Event) -> None:
        """
        Display available macOS versions to download
        """
        self.frame_modal.Close()
        self.parent.Hide()
        self._generate_catalog_frame()
        self.parent.Close()


    def on_existing(self, event: wx.Event = None) -> None:
        """
        Display local macOS installers
        """
        frames = [self, self.frame_modal, self.parent]
        for frame in frames:
            if frame:
                frame.Close()
        gui_macos_installer_flash.macOSInstallerFlashFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            **({"screen_location": self.GetScreenPosition()} if self else {})
        )
        for frame in frames:
            if frame:
                frame.Destroy()


    def on_return(self, event: wx.Event) -> None:
        """
        Return to main menu (dismiss frame)
        """
        self.frame_modal.Close()


    def on_return_to_main_menu(self, event: wx.Event = None) -> None:
        """
        Return to main menu
        """
        if self.frame_modal:
            self.frame_modal.Hide()
        main_menu_frame = gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        if self.frame_modal:
            self.frame_modal.Destroy()
        self.Destroy()