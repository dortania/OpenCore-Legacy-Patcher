"""
defaults.py: Generate default data for host/target
"""

import logging
import plistlib
import subprocess

from pathlib import Path

from .. import constants

from ..detections import device_probe

from . import (
    utilities,
    generate_smbios,
    global_settings
)
from ..datasets import (
    smbios_data,
    cpu_data,
    os_data
)


class GenerateDefaults:

    def __init__(self, model: str, host_is_target: bool, global_constants: constants.Constants, ignore_settings_file: bool = False) -> None:
        self.constants: constants.Constants = global_constants

        self.model: str = model

        self.host_is_target: bool = host_is_target
        self.ignore_settings_file: bool = ignore_settings_file

        # Reset Variables
        self.constants.sip_status = True
        self.constants.secure_status = False
        self.constants.disable_cs_lv = False
        self.constants.disable_amfi = False
        self.constants.fu_status = False

        # Reset Variables - GUI override
        # Match constants.py for model specific settings
        # TODO: Write a sane system for this...
        self.constants.firewire_boot = False
        self.constants.xhci_boot = False
        self.constants.nvme_boot = False
        self.constants.force_quad_thread = False
        self.constants.enable_wake_on_wlan = False
        self.constants.disable_tb = False
        self.constants.dGPU_switch = False
        self.constants.disallow_cpufriend = False
        self.constants.disable_mediaanalysisd = False
        self.constants.set_alc_usage = True
        self.constants.nvram_write = True
        self.constants.allow_nvme_fixing = True
        self.constants.allow_3rd_party_drives = True
        self.constants.disable_fw_throttle = False
        self.constants.software_demux = False
        self.constants.disable_connectdrivers = False
        self.constants.amd_gop_injection = False
        self.constants.nvidia_kepler_gop_injection = False
        self.constants.disable_cs_lv = False
        self.constants.disable_amfi = False
        self.constants.secure_status = False
        self.constants.serial_settings = "None"
        self.constants.override_smbios = "Default"
        self.constants.allow_native_spoofs = False
        self.constants.allow_oc_everywhere = False
        self.constants.sip_status = True
        self.constants.custom_sip_value = None


        self.constants.fu_arguments = None

        self.constants.custom_serial_number = ""
        self.constants.custom_board_serial_number = ""

        if self.host_is_target is True:
            for gpu in self.constants.computer.gpus:
                if gpu.device_id_unspoofed == -1:
                    gpu.device_id_unspoofed = gpu.device_id
                if gpu.vendor_id_unspoofed == -1:
                    gpu.vendor_id_unspoofed = gpu.vendor_id

        self._general_probe()
        self._nvram_probe()
        self._gpu_probe()
        self._networking_probe()
        self._misc_hardwares_probe()
        self._smbios_probe()
        self._check_amfipass_supported()
        self._load_gui_defaults()


    def _general_probe(self) -> None:
        """
        General probe for data
        """

        if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            # Users disabling TS2 most likely have a faulty dGPU
            # users can override this in settings
            ts2_status = global_settings.GlobalEnviromentSettings().read_property("MacBookPro_TeraScale_2_Accel")
            if ts2_status is True:
                self.constants.allow_ts2_accel = True
            else:
                global_settings.GlobalEnviromentSettings().write_property("MacBookPro_TeraScale_2_Accel", False)
                self.constants.allow_ts2_accel = False

        if self.model in ["MacPro3,1", "Xserve2,1"]:
            self.constants.force_quad_thread = True
        else:
            self.constants.force_quad_thread = False

        if self.model in smbios_data.smbios_dictionary:
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.CPUGen.skylake.value:
                # On 2016-2017 MacBook Pros, 15" devices used a stock Samsung SSD with IONVMeController
                # Technically this should be patched based on NVMeFix.kext logic,
                # however Apple deemed the SSD unsupported for enhanced performance
                # In addition, some upgraded NVMe drives still have issues with enhanced power management
                # Safest to disable by default, allow user to configure afterwards
                self.constants.allow_nvme_fixing = False
            else:
                self.constants.allow_nvme_fixing = True

        # Check if running in RecoveryOS
        self.constants.recovery_status = utilities.check_recovery()

        if global_settings.GlobalEnviromentSettings().read_property("Force_Web_Drivers") is True:
            self.constants.force_nv_web = True

        result = global_settings.GlobalEnviromentSettings().read_property("ShouldNukeKDKs")
        if result is False:
            self.constants.should_nuke_kdks = False


    def _smbios_probe(self) -> None:
        """
        SMBIOS specific probe
        """

        if not self.host_is_target:
            if self.model in ["MacPro4,1", "MacPro5,1"]:
                # Allow H.265 on AMD
                # Assume 2009+ machines have Polaris on pre-builts (internal testing)
                # Hardware Detection will never hit this
                self.constants.serial_settings = "Minimal"

        # Check if model uses T2 SMBIOS, if so see if it needs root patching (determined earlier on via SIP variable)
        # If not, allow SecureBootModel usage, otherwise force VMM patching
        # Needed for macOS Monterey to allow OTA updates
        try:
            spoof_model = generate_smbios.set_smbios_model_spoof(self.model)
        except:
            # Native Macs (mainly M1s) will error out as they don't know what SMBIOS to spoof to
            # As we don't spoof on native models, we can safely ignore this
            spoof_model = self.model

        if spoof_model in smbios_data.smbios_dictionary:
            if smbios_data.smbios_dictionary[spoof_model]["SecureBootModel"] is not None:
                if self.constants.sip_status is False:
                    # Force VMM as root patching breaks .im4m signature
                    self.constants.secure_status = False
                    self.constants.force_vmm = True
                else:
                    # Allow SecureBootModel
                    self.constants.secure_status = True
                    self.constants.force_vmm = False


    def _nvram_probe(self) -> None:
        """
        NVRAM specific probe
        """

        if not self.host_is_target:
            return

        if "-v" in (utilities.get_nvram("boot-args") or ""):
            self.constants.verbose_debug = True

        self.constants.custom_serial_number = utilities.get_nvram("OCLP-Spoofed-SN", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        self.constants.custom_board_serial_number = utilities.get_nvram("OCLP-Spoofed-MLB", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if self.constants.custom_serial_number is None or self.constants.custom_board_serial_number is None:
            # If either variables are missing, we assume something is wrong with the spoofed variables and reset
            self.constants.custom_serial_number = ""
            self.constants.custom_board_serial_number = ""


    def _networking_probe(self) -> None:
        """
        Networking specific probe
        """

        is_legacy_wifi = False
        is_modern_wifi = False

        if self.host_is_target:
            if (
                (
                    isinstance(self.constants.computer.wifi, device_probe.Broadcom) and
                    self.constants.computer.wifi.chipset in [
                        device_probe.Broadcom.Chipsets.AirPortBrcm4331,
                        device_probe.Broadcom.Chipsets.AirPortBrcm43224,
                    ]
                ) or (
                    isinstance(self.constants.computer.wifi, device_probe.Atheros) and
                    self.constants.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40
                )
            ):
                is_legacy_wifi = True
            elif (
                (
                    isinstance(self.constants.computer.wifi, device_probe.Broadcom) and
                    self.constants.computer.wifi.chipset in [
                        device_probe.Broadcom.Chipsets.AirPortBrcm4360,
                        device_probe.Broadcom.Chipsets.AirportBrcmNIC,
                    ]
                )
            ):
                is_modern_wifi = True

        else:
            if self.model not in smbios_data.smbios_dictionary:
                return
            if (
                smbios_data.smbios_dictionary[self.model]["Wireless Model"] in [
                    device_probe.Broadcom.Chipsets.AirPortBrcm4331,
                    device_probe.Broadcom.Chipsets.AirPortBrcm43224,
                    device_probe.Atheros.Chipsets.AirPortAtheros40,
                ]
            ):
                is_legacy_wifi = True
            elif (
                    smbios_data.smbios_dictionary[self.model]["Wireless Model"] in [
                    device_probe.Broadcom.Chipsets.AirPortBrcm4360,
                    device_probe.Broadcom.Chipsets.AirportBrcmNIC,
                ]
            ):
                is_modern_wifi = True

        if is_legacy_wifi is False and is_modern_wifi is False:
            return

        # 12.0: Legacy Wireless chipsets require root patching
        # 14.0: Modern Wireless chipsets require root patching
        if self.model in smbios_data.smbios_dictionary:
            if smbios_data.smbios_dictionary[self.model]["Max OS Supported"] < os_data.os_data.sonoma:
                self.constants.sip_status = True
                self.constants.sip_status = False
                self.constants.secure_status = False
                self.constants.disable_cs_lv = True
                self.constants.disable_amfi = True

        # if is_legacy_wifi is True:
        #     # 13.0: Enabling AirPlay to Mac patches breaks Control Center on legacy chipsets
        #     # AirPlay to Mac was unsupported regardless, so we can safely disable it
        #     self.constants.fu_arguments = " -disable_sidecar_mac"


    def _misc_hardwares_probe(self) -> None:
        """
        Misc probe
        """
        if self.host_is_target:
            if self.constants.computer.usb_controllers:
                if self.model in smbios_data.smbios_dictionary:
                    if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.ivy_bridge.value:
                        # Pre-Ivy do not natively support XHCI boot support
                        # If we detect XHCI on older model, enable
                        for controller in self.constants.computer.usb_controllers:
                            if isinstance(controller, device_probe.XHCIController):
                                self.constants.xhci_boot = True
                                break


    def _gpu_probe(self) -> None:
        """
        Graphics specific probe
        """

        gpu_archs = []
        if self.host_is_target:
            gpu_archs = [gpu.arch for gpu in self.constants.computer.gpus if gpu.class_code != 0xFFFFFFFF]
        else:
            if self.model in smbios_data.smbios_dictionary:
                gpu_archs = smbios_data.smbios_dictionary[self.model]["Stock GPUs"]

        for arch in gpu_archs:
            # Legacy Metal Logic
            if arch in [
                device_probe.Intel.Archs.Ivy_Bridge,
                device_probe.Intel.Archs.Haswell,
                device_probe.Intel.Archs.Broadwell,
                device_probe.Intel.Archs.Skylake,
                device_probe.NVIDIA.Archs.Kepler,
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000,
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Polaris_Spoof,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                if arch in [
                    device_probe.Intel.Archs.Ivy_Bridge,
                    device_probe.Intel.Archs.Haswell,
                    device_probe.NVIDIA.Archs.Kepler,
                ]:
                    self.constants.disable_amfi = True
                    self.constants.disable_mediaanalysisd = True

                if arch in [
                        device_probe.AMD.Archs.Legacy_GCN_7000,
                        device_probe.AMD.Archs.Legacy_GCN_8000,
                        device_probe.AMD.Archs.Legacy_GCN_9000,
                        device_probe.AMD.Archs.Polaris,
                        device_probe.AMD.Archs.Polaris_Spoof,
                        device_probe.AMD.Archs.Vega,
                        device_probe.AMD.Archs.Navi,
                ]:
                    if arch == device_probe.AMD.Archs.Legacy_GCN_7000:
                        # Check if we're running in Rosetta
                        if self.host_is_target:
                            if self.constants.computer.rosetta_active is True:
                                continue

                    # Allow H.265 on AMD
                    if self.model in smbios_data.smbios_dictionary:
                        if "Socketed GPUs" in smbios_data.smbios_dictionary[self.model]:
                            self.constants.serial_settings = "Minimal"

                # See if system can use the native AMD stack in Ventura
                if arch in [
                    device_probe.AMD.Archs.Polaris,
                    device_probe.AMD.Archs.Polaris_Spoof,
                    device_probe.AMD.Archs.Vega,
                    device_probe.AMD.Archs.Navi,
                ]:
                    if self.host_is_target:
                        if "AVX2" in self.constants.computer.cpu.leafs:
                            continue
                    else:
                        if self.model in smbios_data.smbios_dictionary:
                            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.CPUGen.haswell.value:
                                continue

                self.constants.sip_status = False
                self.constants.secure_status = False
                self.constants.disable_cs_lv = True

            # Non-Metal Logic
            elif arch in [
                device_probe.Intel.Archs.Iron_Lake,
                device_probe.Intel.Archs.Sandy_Bridge,
                device_probe.NVIDIA.Archs.Tesla,
                device_probe.NVIDIA.Archs.Fermi,
                device_probe.NVIDIA.Archs.Maxwell,
                device_probe.NVIDIA.Archs.Pascal,
                device_probe.AMD.Archs.TeraScale_1,
                device_probe.AMD.Archs.TeraScale_2,
            ]:
                self.constants.sip_status = False
                self.constants.secure_status = False
                self.constants.disable_cs_lv = True
                if os_data.os_data.ventura in self.constants.legacy_accel_support:
                    # Only disable AMFI if we officially support Ventura
                    self.constants.disable_amfi = True

                for key in ["Moraea_BlurBeta"]:
                    # Enable BetaBlur if user hasn't disabled it
                    is_key_enabled = subprocess.run(["/usr/bin/defaults", "read", "-globalDomain", key], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
                    if is_key_enabled not in ["false", "0"]:
                        subprocess.run(["/usr/bin/defaults", "write", "-globalDomain", key, "-bool", "true"])

    def _check_amfipass_supported(self) -> None:
        """
        Check if root volume supports AMFIPass

        The basic requirements of this function are:
        - The host is the target
        - Root volume doesn't have adhoc signed binaries

        If all of these conditions are met, it is safe to disable AMFI and CS_LV. Otherwise, for safety, leave it be.
        """

        if not self.host_is_target:
            # Unknown whether the host is using old binaries
            # Rebuild it once you are on the host
            return

        # Check for adhoc signed binaries
        if self.constants.computer.oclp_sys_signed is False:
            # Root patch with new binaries, then reboot
            return

        # Note: simply checking the authority is not enough, as the authority can be spoofed
        # (but do we really care? this is just a simple check)
        # Note: the cert will change

        self.constants.disable_amfi = False
        self.constants.disable_cs_lv = False


    def _load_gui_defaults(self) -> None:
        """
        Load GUI defaults from global settings
        """
        if not self.host_is_target:
            return
        if self.ignore_settings_file is True:
            return

        settings_plist = global_settings.GlobalEnviromentSettings().global_settings_plist
        if not Path(settings_plist).exists():
            return

        try:
            plist = plistlib.load(Path(settings_plist).open("rb"))
        except Exception as e:
            logging.error("Error: Unable to read global settings file")
            logging.error(e)
            return

        for key in plist:
            if not key.startswith("GUI:"):
                continue

            constants_key = key.replace("GUI:", "")

            if plist[key] == "PYTHON_NONE_VALUE":
                plist[key] = None

            if hasattr(self.constants, constants_key):
                # Check if type is different
                original_type = type(getattr(self.constants, constants_key))
                new_type = type(plist[key])
                if original_type != new_type:
                    logging.error(f"Global settings type mismatch for {constants_key}: {original_type} vs {new_type}")
                    logging.error(f"Removing {key} from global settings")
                    global_settings.GlobalEnviromentSettings().delete_property(key)
                    continue

                logging.info(f"Setting {constants_key} to {plist[key]}")
                setattr(self.constants, constants_key, plist[key])