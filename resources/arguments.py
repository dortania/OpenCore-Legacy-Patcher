import sys
import time
import logging
import plistlib
import threading
import subprocess

from pathlib import Path

from data import model_array, os_data
from resources.build import build
from resources.sys_patch import sys_patch, sys_patch_auto
from resources import defaults, utilities, validation, constants
from resources.wx_gui import gui_entry


# Generic building args
class arguments:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants

        self.args = utilities.check_cli_args()

        self._parse_arguments()


    def _parse_arguments(self) -> None:
        """
        Parses arguments passed to the patcher
        """

        if self.args.validate:
            self._validation_handler()
            return

        if self.args.build:
            self._build_handler()
            return

        if self.args.patch_sys_vol:
            self._sys_patch_handler()
            return

        if self.args.unpatch_sys_vol:
            self._sys_unpatch_handler()
            return

        if self.args.prepare_for_update:
            self._prepare_for_update_handler()
            return

        if self.args.cache_os:
            self._cache_os_handler()
            return

        if self.args.auto_patch:
            self._sys_patch_auto_handler()
            return


    def _validation_handler(self) -> None:
        """
        Enter validation mode
        """
        logging.info("Set Validation Mode")
        validation.PatcherValidation(self.constants)


    def _sys_patch_handler(self) -> None:
        """
        Start root volume patching
        """

        logging.info("Set System Volume patching")
        if "Library/InstallerSandboxes/" in str(self.constants.payload_path):
            logging.info("- Running from Installer Sandbox, blocking OS updaters")
            thread = threading.Thread(target=sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, None).start_patch)
            thread.start()
            while thread.is_alive():
                utilities.block_os_updaters()
                time.sleep(1)
        else:
            sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, None).start_patch()


    def _sys_unpatch_handler(self) -> None:
        """
        Start root volume unpatching
        """
        logging.info("Set System Volume unpatching")
        sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, None).start_unpatch()


    def _sys_patch_auto_handler(self) -> None:
        """
        Start root volume auto patching
        """

        logging.info("Set Auto patching")
        sys_patch_auto.AutomaticSysPatch(self.constants).start_auto_patch()


    def _prepare_for_update_handler(self) -> None:
        """
        Prepare host for macOS update
        """
        logging.info("Preparing host for macOS update")

        os_data = utilities.fetch_staged_update(variant="Update")
        if os_data[0] is None:
            logging.info("No update staged, skipping")
            return

        os_version = os_data[0]
        os_build   = os_data[1]

        logging.info(f"Preparing for update to {os_version} ({os_build})")

        self._clean_le_handler()


    def _cache_os_handler(self) -> None:
        """
        Fetch KDK for incoming OS
        """
        results = subprocess.run(["ps", "-ax"], stdout=subprocess.PIPE)
        if results.stdout.decode("utf-8").count("OpenCore-Patcher --cache_os") > 1:
            logging.info("Another instance of OS caching is running, exiting")
            return

        gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.OS_CACHE)


    def _clean_le_handler(self) -> None:
        """
        Clean /Library/Extensions of problematic kexts
        Note macOS Ventura and older do this automatically
        """

        if self.constants.detected_os < os_data.os_data.sonoma:
            return

        logging.info("Cleaning /Library/Extensions")

        for kext in Path("/Library/Extensions").glob("*.kext"):
            if not Path(f"{kext}/Contents/Info.plist").exists():
                continue
            try:
                kext_plist = plistlib.load(open(f"{kext}/Contents/Info.plist", "rb"))
            except Exception as e:
                logging.info(f"  - Failed to load plist for {kext.name}: {e}")
                continue
            if "GPUCompanionBundles" not in kext_plist:
                continue
            logging.info(f"  - Removing {kext.name}")
            subprocess.run(["rm", "-rf", kext])


    def _build_handler(self) -> None:
        """
        Start config building process
        """
        logging.info("Set OpenCore Build")

        if self.args.model:
            if self.args.model:
                logging.info(f"- Using custom model: {self.args.model}")
                self.constants.custom_model = self.args.model
                defaults.GenerateDefaults(self.constants.custom_model, False, self.constants)
            elif self.constants.computer.real_model not in model_array.SupportedSMBIOS and self.constants.allow_oc_everywhere is False:
                logging.info(
                    """Your model is not supported by this patcher for running unsupported OSes!"

If you plan to create the USB for another machine, please select the "Change Model" option in the menu."""
                )
                sys.exit(1)
            else:
                logging.info(f"- Using detected model: {self.constants.computer.real_model}")
                defaults.GenerateDefaults(self.constants.custom_model, True, self.constants)

        if self.args.verbose:
            logging.info("- Set verbose configuration")
            self.constants.verbose_debug = True
        else:
            self.constants.verbose_debug = False  # Override Defaults detected

        if self.args.debug_oc:
            logging.info("- Set OpenCore DEBUG configuration")
            self.constants.opencore_debug = True

        if self.args.debug_kext:
            logging.info("- Set kext DEBUG configuration")
            self.constants.kext_debug = True

        if self.args.hide_picker:
            logging.info("- Set HidePicker configuration")
            self.constants.showpicker = False

        if self.args.disable_sip:
            logging.info("- Set Disable SIP configuration")
            self.constants.sip_status = False
        else:
            self.constants.sip_status = True  # Override Defaults detected

        if self.args.disable_smb:
            logging.info("- Set Disable SecureBootModel configuration")
            self.constants.secure_status = False
        else:
            self.constants.secure_status = True  # Override Defaults detected

        if self.args.vault:
            logging.info("- Set Vault configuration")
            self.constants.vault = True

        if self.args.firewire:
            logging.info("- Set FireWire Boot configuration")
            self.constants.firewire_boot = True

        if self.args.nvme:
            logging.info("- Set NVMe Boot configuration")
            self.constants.nvme_boot = True

        if self.args.wlan:
            logging.info("- Set Wake on WLAN configuration")
            self.constants.enable_wake_on_wlan = True

        if self.args.disable_tb:
            logging.info("- Set Disable Thunderbolt configuration")
            self.constants.disable_tb = True

        if self.args.force_surplus:
            logging.info("- Forcing SurPlus override configuration")
            self.constants.force_surplus = True

        if self.args.moderate_smbios:
            logging.info("- Set Moderate SMBIOS Patching configuration")
            self.constants.serial_settings = "Moderate"

        if self.args.smbios_spoof:
            if self.args.smbios_spoof == "Minimal":
                self.constants.serial_settings = "Minimal"
            elif self.args.smbios_spoof == "Moderate":
                self.constants.serial_settings = "Moderate"
            elif self.args.smbios_spoof == "Advanced":
                self.constants.serial_settings = "Advanced"
            else:
                logging.info(f"- Unknown SMBIOS arg passed: {self.args.smbios_spoof}")

        if self.args.support_all:
            logging.info("- Building for natively supported model")
            self.constants.allow_oc_everywhere = True
            self.constants.serial_settings = "None"

        build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants)
