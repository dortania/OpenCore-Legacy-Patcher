# Class for handling Wired Networking Patches, invocation from build.py
# Copyright (C) 2020-2023, Dhinak G, Mykola Grymalyuk

from resources import constants, device_probe
from resources.build import support
from data import smbios_data, cpu_data


class BuildWiredNetworking:
    """
    Build Library for Wired Networking Support

    Invoke from build.py
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants
        self.computer: device_probe.Computer = self.constants.computer

        self._build()


    def _build(self) -> None:
        """
        Kick off Wired Build Process
        """

        # Check if Ethernet was detected, otherwise fall back to assumptions (mainly for 2011 MacBook Airs and TB Ethernet)
        if not self.constants.custom_model and self.constants.computer.ethernet:
            self._on_model()
        else:
            self._prebuilt_assumption()

        # Always enable due to chance of hot-plugging
        self._usb_ecm_dongles()
        self._i210_handling()


    def _usb_ecm_dongles(self) -> None:
        """
        USB ECM Dongle Handling
        """
        # With Sonoma, our WiFi patches require downgrading IOSkywalk
        # Unfortunately Apple's DriverKit stack uses IOSkywalk for ECM dongles, so we'll need force load
        # the kernel driver to prevent a kernel panic
        # - DriverKit: com.apple.DriverKit.AppleUserECM.dext
        # - Kext: AppleUSBECM.kext
        support.BuildSupport(self.model, self.constants, self.config).enable_kext("ECM-Override.kext", self.constants.ecm_override_version, self.constants.ecm_override_path)


    def _i210_handling(self) -> None:
        """
        PCIe i210 NIC Handling
        """
        # i210 NICs are broke in macOS 14 due to driver kit downgrades
        # See ECM logic for why it's always enabled
        if not self.model in smbios_data.smbios_dictionary:
            return
        support.BuildSupport(self.model, self.constants, self.config).enable_kext("CatalinaIntelI210Ethernet.kext", self.constants.i210_version, self.constants.i210_path)
        # Ivy Bridge and newer natively support DriverKit, so set MinKernel to 23.0.0
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.CPUGen.ivy_bridge.value:
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("CatalinaIntelI210Ethernet.kext")["MinKernel"] = "23.0.0"


    def _on_model(self) -> None:
        """
        On-Model Hardware Detection Handling
        """

        for controller in self.constants.computer.ethernet:
            if isinstance(controller, device_probe.BroadcomEthernet) and controller.chipset == device_probe.BroadcomEthernet.Chipsets.AppleBCM5701Ethernet:
                if not self.model in smbios_data.smbios_dictionary:
                    continue
                if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.ivy_bridge.value:
                    # Required due to Big Sur's BCM5701 requiring VT-D support
                    # Applicable for pre-Ivy Bridge models
                    support.BuildSupport(self.model, self.constants, self.config).enable_kext("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path)
            elif isinstance(controller, device_probe.IntelEthernet):
                if not self.model in smbios_data.smbios_dictionary:
                    continue
                if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.ivy_bridge.value:
                    # Apple's IOSkywalkFamily in DriverKit requires VT-D support
                    # Applicable for pre-Ivy Bridge models
                    if controller.chipset == device_probe.IntelEthernet.Chipsets.AppleIntelI210Ethernet:
                        support.BuildSupport(self.model, self.constants, self.config).enable_kext("CatalinaIntelI210Ethernet.kext", self.constants.i210_version, self.constants.i210_path)
                    elif controller.chipset == device_probe.IntelEthernet.Chipsets.AppleIntel8254XEthernet:
                        support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleIntel8254XEthernet.kext", self.constants.intel_8254x_version, self.constants.intel_8254x_path)
                    elif controller.chipset == device_probe.IntelEthernet.Chipsets.Intel82574L:
                        support.BuildSupport(self.model, self.constants, self.config).enable_kext("Intel82574L.kext", self.constants.intel_82574l_version, self.constants.intel_82574l_path)
            elif isinstance(controller, device_probe.NVIDIAEthernet):
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path)
            elif isinstance(controller, device_probe.Marvell) or isinstance(controller, device_probe.SysKonnect):
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path)

            # Pre-Ivy Bridge Aquantia Ethernet Patch
            if isinstance(controller, device_probe.Aquantia) and controller.chipset == device_probe.Aquantia.Chipsets.AppleEthernetAquantiaAqtion:
                if not self.model in smbios_data.smbios_dictionary:
                    continue
                if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.ivy_bridge.value:
                    support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleEthernetAbuantiaAqtion.kext", self.constants.aquantia_version, self.constants.aquantia_path)


    def _prebuilt_assumption(self) -> None:
        """
        Fall back to pre-built assumptions
        """

        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "Ethernet Chipset" in smbios_data.smbios_dictionary[self.model]:
            return

        if smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Broadcom":
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.ivy_bridge.value:
                # Required due to Big Sur's BCM5701 requiring VT-D support
                # Applicable for pre-Ivy Bridge models
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Nvidia":
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Marvell":
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Intel 80003ES2LAN":
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleIntel8254XEthernet.kext", self.constants.intel_8254x_version, self.constants.intel_8254x_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Intel 82574L":
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("Intel82574L.kext", self.constants.intel_82574l_version, self.constants.intel_82574l_path)