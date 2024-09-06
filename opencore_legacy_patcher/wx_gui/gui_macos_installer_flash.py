"""
gui_macos_installer_flash.py: macOS Installer Flash Frame
"""

import wx
import time
import logging
import plistlib
import tempfile
import threading
import subprocess

from pathlib import Path

from .. import constants

from ..datasets import os_data
from ..volume   import generate_copy_arguments

from ..wx_gui import (
    gui_main_menu,
    gui_build,
    gui_support
)
from ..support import (
    macos_installer_handler,
    utilities,
    network_handler,
    kdk_handler,
    metallib_handler,
    subprocess_wrapper
)


class macOSInstallerFlashFrame(wx.Frame):

    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        logging.info("Initializing macOS Installer Flash Frame")
        super(macOSInstallerFlashFrame, self).__init__(parent, title=title, size=(350, 200), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        gui_support.GenerateMenubar(self, global_constants).generate()

        self.constants: constants.Constants = global_constants
        self.title: str = title

        self.available_installers_local: dict = {}
        self.available_disks: dict = {}
        self.prepare_result: bool = False

        self.progress_bar_animation: gui_support.GaugePulseCallback = None

        self.frame_modal: wx.Dialog = None

        self._generate_elements()

        self.Centre()
        self.Show()

        self._populate_installers()


    def _generate_elements(self) -> None:
        """
        Fetches local macOS Installers for users to select from
        """

        # Title: Fetching local macOS Installers
        title_label = wx.StaticText(self, label="Fetching local macOS Installers", pos=(-1,1))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(self, range=100, pos=(-1, 30), size=(200, 30))
        progress_bar.Centre(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()
        self.progress_bar_animation = progress_bar_animation

        # Set size of frame
        self.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 40))


    def _populate_installers(self) -> None:
        # Grab installer catalog
        def fetch_installers():
            self.available_installers_local = macos_installer_handler.LocalInstallerCatalog().available_apps

        thread = threading.Thread(target=fetch_installers)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        frame_modal = wx.Dialog(self, title=self.title, size=(350, 200))

        # Title: Select macOS Installer
        title_label = wx.StaticText(frame_modal, label="Select local macOS Installer", pos=(-1,5))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # List of installers
        if self.available_installers_local:
            logging.info("Installer(s) found:")
            spacer = 10
            entries = len(self.available_installers_local)
            for app in self.available_installers_local:
                logging.info(f"- {self.available_installers_local[app]['Short Name']}: {self.available_installers_local[app]['Version']} ({self.available_installers_local[app]['Build']})")

                app_str = f"{self.available_installers_local[app]['Short Name']}"
                unsupported: bool = self.available_installers_local[app]['Minimum Host OS'] > self.constants.detected_os

                if unsupported:
                    min_str = os_data.os_conversion.convert_kernel_to_marketing_name(self.available_installers_local[app]['Minimum Host OS'])
                    app_str += f" (Requires {min_str})"
                else:
                    app_str += f": {self.available_installers_local[app]['Version']} ({self.available_installers_local[app]['Build']})"

                installer_button = wx.Button(frame_modal, label=app_str, pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + spacer), size=(300, 30))
                installer_button.Bind(wx.EVT_BUTTON, lambda event, temp=app: self.on_select(self.available_installers_local[temp]))
                installer_button.Centre(wx.HORIZONTAL)
                spacer += 25
                if unsupported:
                    installer_button.Disable()
                elif entries == 1:
                    installer_button.SetDefault()

        else:
            installer_button = wx.StaticText(frame_modal, label="No installers found in '/Applications'", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
            installer_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            installer_button.Centre(wx.HORIZONTAL)

        # Button: Return to Main Menu
        cancel_button = wx.Button(frame_modal, label="Return to Main Menu", pos=(-1, installer_button.GetPosition()[1] + installer_button.GetSize()[1]), size=(150, 30))
        cancel_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        cancel_button.Centre(wx.HORIZONTAL)

        # Set size of frame
        frame_modal.SetSize((-1, cancel_button.GetPosition()[1] + cancel_button.GetSize()[1] + 40))

        self.progress_bar_animation.stop_pulse()

        frame_modal.ShowWindowModal()
        self.frame_modal = frame_modal


    def on_select(self, installer: dict) -> None:
        logging.info(f"Selected installer: {installer['Short Name']} ({installer['Version']} ({installer['Build']}))")
        self.frame_modal.Destroy()

        for child in self.GetChildren():
            child.Destroy()

        # Fetching information on local disks
        title_label = wx.StaticText(self, label="Fetching information on local disks", pos=(-1,1))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(self, range=100, pos=(-1, 30), size=(200, 30))
        progress_bar.Centre(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        # Set size of frame
        self.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 40))

        # Fetch local disks
        def _fetch_disks():
            self.available_disks = macos_installer_handler.InstallerCreation().list_disk_to_format()

            # Need to clean up output on pre-Sierra
            # Disk images are mixed in with regular disks (ex. payloads.dmg)
            ignore = ["disk image", "read-only", "virtual"]
            for disk in self.available_disks.copy():
                if any(string in self.available_disks[disk]['name'].lower() for string in ignore):
                    del self.available_disks[disk]


        thread = threading.Thread(target=_fetch_disks)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        self.frame_modal = wx.Dialog(self, title=self.title, size=(350, 200))

        # Title: Select local disk
        title_label = wx.StaticText(self.frame_modal, label="Select local disk", pos=(-1,5))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Label: Selected USB will be erased, please backup any data
        warning_label = wx.StaticText(self.frame_modal, label="Selected USB will be erased, please backup any data", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
        warning_label.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
        warning_label.Centre(wx.HORIZONTAL)

        # List of disks
        if self.available_disks:
            spacer = 5
            entries = len(self.available_disks)
            logging.info("Available disks:")
            for disk in self.available_disks:
                logging.info(f" - {disk}: {self.available_disks[disk]['name']} - {utilities.human_fmt(self.available_disks[disk]['size'])}")
                disk_button = wx.Button(self.frame_modal, label=f"{disk}: {self.available_disks[disk]['name']} - {utilities.human_fmt(self.available_disks[disk]['size'])}", pos=(-1, warning_label.GetPosition()[1] + warning_label.GetSize()[1] + spacer), size=(300, 30))
                disk_button.Bind(wx.EVT_BUTTON, lambda event, temp=disk: self.on_select_disk(self.available_disks[temp], installer))
                disk_button.Centre(wx.HORIZONTAL)
                if entries == 1:
                    disk_button.SetDefault()
                spacer += 25
        else:
            disk_button = wx.StaticText(self.frame_modal, label="No disks found", pos=(-1, warning_label.GetPosition()[1] + warning_label.GetSize()[1] + 5))
            disk_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
            disk_button.Centre(wx.HORIZONTAL)

        # Search for disks again
        search_button = wx.Button(self.frame_modal, label="Search for disks again", pos=(-1, disk_button.GetPosition()[1] + disk_button.GetSize()[1]), size=(150, 30))
        search_button.Bind(wx.EVT_BUTTON, lambda event, temp=installer: self.on_select(temp))
        search_button.Centre(wx.HORIZONTAL)

        # Button: Return to Main Menu
        cancel_button = wx.Button(self.frame_modal, label="Return to Main Menu", pos=(-1, search_button.GetPosition()[1] + search_button.GetSize()[1] - 10), size=(150, 30))
        cancel_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        cancel_button.Centre(wx.HORIZONTAL)

        # Set size of frame
        self.frame_modal.SetSize((-1, cancel_button.GetPosition()[1] + cancel_button.GetSize()[1] + 40))

        progress_bar_animation.stop_pulse()

        self.frame_modal.ShowWindowModal()


    def on_select_disk(self, disk: dict, installer: dict) -> None:
        answer = wx.MessageBox(f"Are you sure you want to erase '{disk['name']}'?\nAll data will be lost, this cannot be undone.", "Confirmation", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if answer != wx.YES:
            return

        logging.info(f"Selected disk: {disk['name']}")

        self.frame_modal.Destroy()

        for child in self.GetChildren():
            child.Destroy()

        self.SetSize((450, -1))

        # Title: Creating Installer: {installer_name}
        title_label = wx.StaticText(self, label=f"Creating Installer: {installer['Short Name']}", pos=(-1,1))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Label: Creating macOS installers can take 30min+ on slower USB drives.
        warning_label = wx.StaticText(self, label="Creating macOS installers can take 30min+ on slower USB drives.", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
        warning_label.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
        warning_label.Centre(wx.HORIZONTAL)

        # Label: We will notify you when the installer is ready.
        warning_label = wx.StaticText(self, label="We will notify you when the installer is ready.", pos=(-1, warning_label.GetPosition()[1] + warning_label.GetSize()[1] + 5))
        warning_label.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
        warning_label.Centre(wx.HORIZONTAL)

        # Label: Bytes Written: 0 MB
        bytes_written_label = wx.StaticText(self, label="Bytes Written: 0.00 MB", pos=(-1, warning_label.GetPosition()[1] + warning_label.GetSize()[1] + 5))
        bytes_written_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        bytes_written_label.Centre(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(self, range=100, pos=(-1, bytes_written_label.GetPosition()[1] + bytes_written_label.GetSize()[1] + 5), size=(300, 30))
        progress_bar.Centre(wx.HORIZONTAL)

        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        # Set size of frame
        self.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 40))
        self.Show()

        # Prepare resources
        if self._prepare_resources(installer['Path'], disk['identifier']) is False:
            logging.error("Failed to prepare resources, cannot continue.")
            wx.MessageBox("Failed to prepare resources, cannot continue.", "Error", wx.OK | wx.ICON_ERROR)
            self.on_return_to_main_menu()
            return

        # Base Size
        estimated_size = 16000
        # AutoPkg (700MB~)
        estimated_size += 700 if installer['OS'] >= os_data.os_data.big_sur else 0
        # KDK (700MB~, and overhead for copying to installer)
        estimated_size += 700 * 2 if installer['OS'] >= os_data.os_data.ventura else 0

        progress_bar_animation.stop_pulse()
        progress_bar.SetRange(estimated_size)

        # /dev/diskX -> diskX
        root_disk = disk['identifier'][5:]
        initial_bytes_written = float(utilities.monitor_disk_output(root_disk))
        self.result = False
        def _flash():
            logging.info(f"Flashing {installer['Path']} to {root_disk}")
            self.result = self._flash_installer(root_disk)

        thread = threading.Thread(target=_flash)
        thread.start()

        # Wait for installer to be created
        while thread.is_alive():
            try:
                total_bytes_written = float(utilities.monitor_disk_output(root_disk))
            except:
                total_bytes_written = initial_bytes_written
            bytes_written = total_bytes_written - initial_bytes_written
            wx.CallAfter(bytes_written_label.SetLabel, f"Bytes Written: {bytes_written:.2f} MB")
            try:
                bytes_written = int(bytes_written)
            except:
                bytes_written = 0
            wx.CallAfter(progress_bar.SetValue, bytes_written)
            wx.Yield()

        if self.result is False:
            logging.error("Failed to flash installer, cannot continue.")
            self.on_return_to_main_menu()
            return

        # Next verify the installer
        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        bytes_written_label.SetLabel("Validating Installer Integrity...")
        error_message = self._validate_installer_pkg(disk['identifier'])

        progress_bar_animation.stop_pulse()

        if error_message != "":
            progress_bar.SetValue(0)
            wx.MessageBox(f"Failed to validate installer, cannot continue.\n This can generally happen due to a faulty USB drive, as flashing is an intensive process that can trigger hardware faults not normally seen. \n\n{error_message}", "Corrupted Installer!", wx.OK | wx.ICON_ERROR)
            self.on_return_to_main_menu()
            return

        progress_bar.SetValue(estimated_size)

        if gui_support.CheckProperties(self.constants).host_can_build() is False:
            wx.MessageBox("Installer created successfully! If you want to install OpenCore to this USB, you will need to change the Target Model in settings", "Successfully created the macOS installer!", wx.OK | wx.ICON_INFORMATION)
            self.on_return_to_main_menu()
            return

        answer = wx.MessageBox("Installer created successfully, would you like to continue and Install OpenCore to this disk?", "Successfully created the macOS installer!", wx.YES_NO | wx.ICON_QUESTION)
        if answer != wx.YES:
            self.on_return_to_main_menu()
            return

        # Install OpenCore
        self.Hide()
        gui_build.BuildFrame(
            parent=None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition()
        )
        self.Destroy()


    def _prepare_resources(self, installer_path: str, disk: str) -> None:

        def prepare_script(self, installer_path: str, disk: str, constants: constants.Constants):
            self.prepare_result = macos_installer_handler.InstallerCreation().generate_installer_creation_script(constants.payload_path, installer_path, disk)

        thread = threading.Thread(target=prepare_script, args=(self, installer_path, disk, self.constants))
        thread.start()

        while thread.is_alive():
            wx.Yield()

        return self.prepare_result


    def _flash_installer(self, disk) -> bool:
        utilities.disable_sleep_while_running()
        logging.info("Creating macOS installer")

        thread = threading.Thread(target=self._auto_package_handler)
        thread.start()

        # print contents of installer.sh
        with open(self.constants.installer_sh_path, "r") as f:
            logging.info(f"installer.sh contents:\n{f.read()}")

        args   = ["/bin/sh", self.constants.installer_sh_path]
        result = subprocess_wrapper.run_as_root(args, capture_output=True, text=True)
        output = result.stdout
        error  = result.stderr if result.stderr else ""

        if "Install media now available at" not in output:
            logging.info("Failed to create macOS installer")
            popup = wx.MessageDialog(self, f"Failed to create macOS installer\n\nOutput: {output}\n\nError: {error}", "Error", wx.OK | wx.ICON_ERROR)
            popup.ShowModal()
            return False

        logging.info("Successfully created macOS installer")
        while thread.is_alive():
            # wait for download_thread to finish
            # though highly unlikely this thread is still alive (flashing an Installer will take a while)
            time.sleep(0.1)
        logging.info("Installing Root Patcher to drive")
        self._install_installer_pkg(disk)

        utilities.enable_sleep_after_running()
        return True


    def _auto_package_handler(self):
        """
        Function's main goal is to grab the correct AutoPkg-Assets.pkg and unzip it
        Note the following:
            - When running a release build, pull from Github's release page with the same versioning
            - When running from source/unable to find on Github, use the nightly.link variant
            - If nightly also fails, fall back to the manually uploaded variant
        """
        link = self.constants.installer_pkg_url
        if network_handler.NetworkUtilities(link).validate_link() is False:
            logging.info("Stock Install.pkg is missing on Github, falling back to Nightly")
            link = self.constants.installer_pkg_url_nightly

        if link.endswith(".zip"):
            path = self.constants.installer_pkg_zip_path
        else:
            path = self.constants.installer_pkg_path

        autopkg_download = network_handler.DownloadObject(link, path)
        autopkg_download.download(spawn_thread=False)

        if autopkg_download.download_complete is False:
            logging.warning("Failed to download Install.pkg")
            logging.warning(autopkg_download.error_msg)
            return

        # Download thread will re-enable Idle Sleep after downloading
        utilities.disable_sleep_while_running()
        if not str(path).endswith(".zip"):
            return
        if Path(self.constants.installer_pkg_path).exists():
            subprocess.run(["/bin/rm", self.constants.installer_pkg_path])
        subprocess.run(["/usr/bin/ditto", "-V", "-x", "-k", "--sequesterRsrc", "--rsrc", self.constants.installer_pkg_zip_path, self.constants.payload_path])


    def _install_installer_pkg(self, disk):
        disk = disk + "s2" # ESP sits at 1, and we know macOS will have created the main partition at 2

        if not Path(self.constants.installer_pkg_path).exists():
            return

        path = utilities.grab_mount_point_from_disk(disk)
        if not Path(path + "/System/Library/CoreServices/SystemVersion.plist").exists():
            return

        os_version = plistlib.load(Path(path + "/System/Library/CoreServices/SystemVersion.plist").open("rb"))
        kernel_version = os_data.os_conversion.os_to_kernel(os_version["ProductVersion"])
        if int(kernel_version) < os_data.os_data.big_sur:
            logging.info("Installer unsupported, requires Big Sur or newer")
            return

        subprocess.run(["/bin/mkdir", "-p", f"{path}/Library/Packages/"])
        subprocess.run(generate_copy_arguments(self.constants.installer_pkg_path, f"{path}/Library/Packages/"))

        # Chainload KDK and Metallib
        self._chainload_metallib(os_version["ProductBuildVersion"], os_version["ProductVersion"], Path(path + "/Library/Packages/"))
        self._kdk_chainload(os_version["ProductBuildVersion"], os_version["ProductVersion"], Path(path + "/Library/Packages/"))


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

        logging.info("Initiating KDK download")
        logging.info(f"- Build: {build}")
        logging.info(f"- Version: {version}")
        logging.info(f"- Working Directory: {download_dir}")

        kdk_obj = kdk_handler.KernelDebugKitObject(self.constants, build, version, ignore_installed=True)
        if kdk_obj.success is False:
            logging.info("Failed to retrieve KDK")
            logging.info(kdk_obj.error_msg)
            return

        kdk_download_obj = kdk_obj.retrieve_download(override_path=kdk_dmg_path)
        if kdk_download_obj is None:
            logging.info("Failed to retrieve KDK")
            logging.info(kdk_obj.error_msg)

        # Check remaining disk space before downloading
        space = utilities.get_free_space(download_dir)
        if space < (kdk_obj.kdk_url_expected_size * 2):
            logging.info("Not enough disk space to download and install KDK")
            logging.info(f"Attempting to download locally first")
            if space < kdk_obj.kdk_url_expected_size:
                logging.info("Not enough disk space to install KDK, skipping")
                return
            # Ideally we'd download the KDK onto the disk to display progress in the UI
            # However we'll just download to our temp directory and move it to the target disk
            kdk_dmg_path = self.constants.kdk_download_path

        kdk_download_obj.download(spawn_thread=False)
        if kdk_download_obj.download_complete is False:
            logging.info("Failed to download KDK")
            logging.info(kdk_download_obj.error_msg)
            return

        if not kdk_dmg_path.exists():
            logging.info(f"KDK missing: {kdk_dmg_path}")
            return

        # Now that we have a KDK, extract it to get the pkg
        with tempfile.TemporaryDirectory() as mount_point:
            logging.info("Mounting KDK")
            result = subprocess.run(["/usr/bin/hdiutil", "attach", kdk_dmg_path, "-mountpoint", mount_point, "-nobrowse"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.info("Failed to mount KDK")
                subprocess_wrapper.log(result)
                return

            logging.info("Copying KDK")
            subprocess.run(generate_copy_arguments(f"{mount_point}/KernelDebugKit.pkg", kdk_pkg_path))

            logging.info("Unmounting KDK")
            result = subprocess.run(["/usr/bin/hdiutil", "detach", mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.info("Failed to unmount KDK")
                subprocess_wrapper.log(result)
                return

        logging.info("Removing KDK Disk Image")
        kdk_dmg_path.unlink()


    def _chainload_metallib(self, build: str, version: str, download_dir: str):
        """
        Download the correct Metallib to be chainloaded in the macOS installer
        """

        metallib_pkg_path = Path(download_dir) / "MetallibSupportPkg.pkg"

        if metallib_pkg_path.exists():
            metallib_pkg_path.unlink()

        logging.info("Initiating Metallib download")
        logging.info(f"- Build: {build}")
        logging.info(f"- Version: {version}")
        logging.info(f"- Working Directory: {download_dir}")

        metallib_obj = metallib_handler.MetalLibraryObject(self.constants, build, version, ignore_installed=True)
        if metallib_obj.success is False:
            logging.info("Failed to retrieve Metallib")
            logging.info(metallib_obj.error_msg)
            return

        metallib_download_obj = metallib_obj.retrieve_download(override_path=metallib_pkg_path)
        if metallib_download_obj is None:
            logging.info("Failed to retrieve Metallib")
            logging.info(metallib_obj.error_msg)

        # Check remaining disk space before downloading
        space = utilities.get_free_space(download_dir)
        size = 100 * 1024 * 1024
        if space < size:
            logging.info("Not enough disk space to download and install Metallib")
            return

        metallib_download_obj.download(spawn_thread=False)
        if metallib_download_obj.download_complete is False:
            logging.info("Failed to download Metallib")
            logging.info(metallib_download_obj.error_msg)
            return

        if not metallib_pkg_path.exists():
            logging.info(f"Metallib missing: {metallib_pkg_path}")
            return


    def _validate_installer_pkg(self, disk: str) -> bool:
        logging.info("Validating installer pkg")
        error_message = ""
        def _integrity_check():
            nonlocal error_message
            for folder in Path(utilities.grab_mount_point_from_disk(disk + "s2")).glob("*.app"):
                if folder.is_dir():
                    dmg_path = folder / "Contents" / "SharedSupport" / "SharedSupport.dmg"
                    break

            if not Path(dmg_path).exists():
                logging.error(f"Failed to find {dmg_path}")
                error_message = f"Failed to find {dmg_path}"
                return error_message
            result = subprocess.run(["/usr/bin/hdiutil", "verify", dmg_path],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                if result.stdout:
                    logging.error(result.stdout.decode("utf-8"))
                    error_message = "STDOUT: " + result.stdout.decode("utf-8")
                if result.stderr:
                    logging.error(result.stderr.decode("utf-8"))
                    error_message += "\n\nSTDERR: " + result.stderr.decode("utf-8")


        thread = threading.Thread(target=_integrity_check)
        thread.start()
        while thread.is_alive():
            wx.Yield()

        if error_message == "":
            logging.info("Installer pkg validated")
            return error_message

        return error_message


    def on_return_to_main_menu(self, event: wx.Event = None):
        if self.frame_modal:
            self.frame_modal.Hide()
        if self:
            if isinstance(self, wx.Frame):
                self.Hide()
        main_menu_frame = gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        if self.frame_modal:
            self.frame_modal.Destroy()
        if self:
            if isinstance(self, wx.Frame):
                self.Destroy()