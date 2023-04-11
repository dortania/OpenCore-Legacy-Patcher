# Generate Default Data
import subprocess

from resources import (
    utilities,
    device_probe,
    generate_smbios,
    global_settings,
    constants
)
from data import (
    smbios_data,
    cpu_data,
    os_data
)


class GenerateDefaults:

    def __init__(self, model: str, host_is_target: bool, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants

        self.model: str = model

        self.host_is_target: bool = host_is_target

        # Reset Variables
        self.constants.sip_status:    bool = True
        self.constants.secure_status: bool = False
        self.constants.disable_cs_lv: bool = False
        self.constants.disable_amfi:  bool = False
        self.constants.fu_status:     bool = True

        self.constants.fu_arguments: str = None

        self.constants.custom_serial_number:       str = ""
        self.constants.custom_board_serial_number: str = ""

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


    def _general_probe(self) -> None:
        """
        General probe for data
        """

        if "Book" in self.model:
            self.constants.set_content_caching = False
        else:
            self.constants.set_content_caching = True

        if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            # Users disabling TS2 most likely have a faulty dGPU
            # users can override this in settings
            ts2_status = global_settings.GlobalEnviromentSettings().read_property("MacBookPro_TeraScale_2_Accel")
            if ts2_status is True:
                self.constants.allow_ts2_accel = True
            else:
                global_settings.GlobalEnviromentSettings().write_property("MacBookPro_TeraScale_2_Accel", False)
                self.constants.allow_ts2_accel = False

        if self.model in smbios_data.smbios_dictionary:
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.cpu_data.skylake.value:
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

        if self.host_is_target:
            if not (
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
                return

        else:
            if not self.model in smbios_data.smbios_dictionary:
                return
            if (
                smbios_data.smbios_dictionary[self.model]["Wireless Model"] not in [
                    device_probe.Broadcom.Chipsets.AirPortBrcm4331,
                    device_probe.Broadcom.Chipsets.AirPortBrcm43224,
                    device_probe.Atheros.Chipsets.AirPortAtheros40
                ]
            ):
                return

        # 12.0: Legacy Wireless chipsets require root patching
        self.constants.sip_status = False
        self.constants.secure_status = False

        # 13.0: Enabling AirPlay to Mac patches breaks Control Center on legacy chipsets
        # AirPlay to Mac was unsupported regardless, so we can safely disable it
        self.constants.fu_status = True
        self.constants.fu_arguments = " -disable_sidecar_mac"


    def _misc_hardwares_probe(self) -> None:
        """
        Misc probe
        """
        if self.host_is_target:
            if self.constants.computer.usb_controllers:
                if self.model in smbios_data.smbios_dictionary:
                    if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
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

        gpu_dict = []
        if self.host_is_target:
            gpu_dict = self.constants.computer.gpus
        else:
            if self.model in smbios_data.smbios_dictionary:
                gpu_dict = smbios_data.smbios_dictionary[self.model]["Stock GPUs"]

        for gpu in gpu_dict:
            if self.host_is_target:
                if gpu.class_code:
                    if gpu.class_code == 0xFFFFFFFF:
                        continue
                gpu = gpu.arch

            # Legacy Metal Logic
            if gpu in [
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
                if gpu in [
                    device_probe.Intel.Archs.Ivy_Bridge,
                    device_probe.Intel.Archs.Haswell,
                    device_probe.NVIDIA.Archs.Kepler,
                ]:
                    self.constants.disable_amfi = True

                if gpu in [
                        device_probe.AMD.Archs.Legacy_GCN_7000,
                        device_probe.AMD.Archs.Legacy_GCN_8000,
                        device_probe.AMD.Archs.Legacy_GCN_9000,
                        device_probe.AMD.Archs.Polaris,
                        device_probe.AMD.Archs.Polaris_Spoof,
                        device_probe.AMD.Archs.Vega,
                        device_probe.AMD.Archs.Navi,
                ]:
                    if gpu == device_probe.AMD.Archs.Legacy_GCN_7000:
                        # Check if we're running in Rosetta
                        if self.host_is_target:
                            if self.constants.computer.rosetta_active is True:
                                continue

                    # Allow H.265 on AMD
                    if self.model in smbios_data.smbios_dictionary:
                        if "Socketed GPUs" in smbios_data.smbios_dictionary[self.model]:
                            self.constants.serial_settings = "Minimal"

                # See if system can use the native AMD stack in Ventura
                if gpu in [
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
                            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.cpu_data.haswell.value:
                                continue

                self.constants.sip_status = False
                self.constants.secure_status = False
                self.constants.disable_cs_lv = True

            # Non-Metal Logic
            elif gpu in [
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
                    is_key_enabled = subprocess.run(["defaults", "read", "-g", key], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
                    if is_key_enabled not in ["false", "0"]:
                        subprocess.run(["defaults", "write", "-g", key, "-bool", "true"])