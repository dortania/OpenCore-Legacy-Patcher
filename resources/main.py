# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

import subprocess
import sys
from pathlib import Path
import time
import threading

from resources import build, cli_menu, constants, utilities, device_probe, os_probe, defaults, arguments, install, tui_helpers, reroute_payloads, commit_info
from data import model_array

class OpenCoreLegacyPatcher:
    def __init__(self, launch_gui=False):
        print("- Loading...")
        self.constants = constants.Constants()
        self.constants.wxpython_variant = launch_gui
        self.generate_base_data()
        if utilities.check_cli_args() is None:
            if launch_gui is True:
                utilities.disable_cls()
                from gui import gui_main
                gui_main.wx_python_gui(self.constants).main_menu(None)
            else:
                self.main_menu()

    def generate_base_data(self):
        self.constants.detected_os = os_probe.detect_kernel_major()
        self.constants.detected_os_minor = os_probe.detect_kernel_minor()
        self.constants.detected_os_build = os_probe.detect_os_build()
        self.constants.detected_os_version = os_probe.detect_os_version()
        self.constants.computer = device_probe.Computer.probe()
        self.constants.recovery_status = utilities.check_recovery()
        self.computer = self.constants.computer
        self.constants.booted_oc_disk = utilities.find_disk_off_uuid(utilities.clean_device_path(self.computer.opencore_path))
        if self.constants.computer.firmware_vendor:
            if self.constants.computer.firmware_vendor != "Apple":
                self.constants.host_is_hackintosh = True
        launcher_script = None
        launcher_binary = sys.executable
        if "python" in launcher_binary:
            # We're running from source
            launcher_script =  __file__
            if "main.py" in launcher_script:
                launcher_script = launcher_script.replace("/resources/main.py", "/OpenCore-Patcher-GUI.command")
        self.constants.launcher_binary = launcher_binary
        self.constants.launcher_script = launcher_script
        self.constants.unpack_thread = threading.Thread(target=reroute_payloads.reroute_payloads(self.constants).setup_tmp_disk_image)
        self.constants.unpack_thread.start()
        self.constants.commit_info = commit_info.commit_info(self.constants.launcher_binary).generate_commit_info()

        # Now that we have commit info, update nightly link
        if self.constants.commit_info[0] not in ["Running from source", "Built from source"]:
            branch = self.constants.commit_info[0]
            branch = branch.replace("refs/heads/", "")
            self.constants.installer_pkg_url_nightly = self.constants.installer_pkg_url_nightly.replace("main", branch)

        defaults.generate_defaults(self.computer.real_model, True, self.constants)

        if utilities.check_cli_args() is not None:
            print("- Detected arguments, switching to CLI mode")
            self.constants.gui_mode = True  # Assumes no user interaction is required
            ignore_args = ["--auto_patch", "--gui_patch", "--gui_unpatch"]
            if not any(x in sys.argv for x in ignore_args):
                self.constants.current_path = Path.cwd()
                self.constants.cli_mode = True
                if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                    print("- Rerouting payloads location")
                    self.constants.payload_path = sys._MEIPASS / Path("payloads")
            ignore_args = ignore_args.pop(0)
            if not any(x in sys.argv for x in ignore_args):
                while self.constants.unpack_thread.is_alive():
                    time.sleep(0.1)
            arguments.arguments().parse_arguments(self.constants)
        else:
            print(f"- No arguments present, loading {'GUI' if self.constants.wxpython_variant is True else 'TUI'} mode")


    def main_menu(self):
        response = None
        while not (response and response == -1):
            title = [
                f"OpenCore Legacy Patcher v{self.constants.patcher_version}",
                f"Selected Model: {self.constants.custom_model or self.computer.real_model}",
            ]

            if (self.constants.custom_model or self.computer.real_model) not in model_array.SupportedSMBIOS and self.constants.allow_oc_everywhere is False:
                in_between = [
                    "Your model is not supported by this patcher for running unsupported OSes!",
                    "",
                    'If you plan to create the USB for another machine, please select the \n"Change Model" option in the menu.',
                    "",
                    'If you want to run OCLP on a native Mac, please toggle \n"Allow OpenCore on native Models" in settings',
                ]
            elif not self.constants.custom_model and self.computer.real_model == "iMac7,1" and "SSE4.1" not in self.computer.cpu.flags:
                in_between = [
                    "Your model requires a CPU upgrade to a CPU supporting SSE4.1+ to be supported by this patcher!",
                    "",
                    f'If you plan to create the USB for another {self.computer.real_model} with SSE4.1+, please select the "Change Model" option in the menu.',
                ]
            elif self.constants.custom_model == "iMac7,1":
                in_between = ["This model is supported", "However please ensure the CPU has been upgraded to support SSE4.1+"]
            else:
                in_between = ["This model is supported"]

            menu = tui_helpers.TUIMenu(title, "Please select an option: ", in_between=in_between, auto_number=True, top_level=True)

            options = (
                [["Build OpenCore", build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).build_opencore]]
                if ((self.constants.custom_model or self.computer.real_model) in model_array.SupportedSMBIOS) or self.constants.allow_oc_everywhere is True
                else []
            ) + [
                ["Install OpenCore to USB/internal drive", install.tui_disk_installation(self.constants).copy_efi],
                ["Post-Install Volume Patch", cli_menu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).PatchVolume],
                ["Change Model", cli_menu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_model],
                ["Patcher Settings", cli_menu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).patcher_settings],
                ["Installer Creation", cli_menu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).download_macOS],
                ["Credits", cli_menu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).credits],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

        if getattr(sys, "frozen", False) and self.constants.recovery_status is False:
            subprocess.run("""osascript -e 'tell application "Terminal" to close first window' & exit""", shell=True)