"""
wireless.py: Class for handling Wireless Networking Patches, invocation from build.py
"""

import logging

from .. import support

from ... import constants

from ...datasets import smbios_data
from ...support import utilities
from ...detections import device_probe



class BuildWirelessNetworking:
    """
    Build Library for Wireless Networking Support

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
        Kick off Wireless Build Process
        """

        if not self.constants.custom_model and self.constants.computer.wifi:
            self._on_model()
        else:
            self._prebuilt_assumption()
        self._wowl_handling()


    def _on_model(self) -> None:
        """
        On-Model Hardware Detection Handling
        """

        logging.info(f"- Found Wireless Device {utilities.friendly_hex(self.computer.wifi.vendor_id)}:{utilities.friendly_hex(self.computer.wifi.device_id)}")
        self.config["#Revision"]["Hardware-Wifi"] = f"{utilities.friendly_hex(self.computer.wifi.vendor_id)}:{utilities.friendly_hex(self.computer.wifi.device_id)}"

        if isinstance(self.computer.wifi, device_probe.Broadcom):
            if self.computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirportBrcmNIC, device_probe.Broadcom.Chipsets.AirPortBrcm4360]:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("IOSkywalkFamily.kext", self.constants.ioskywalk_version, self.constants.ioskywalk_path)
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211FamilyLegacy.kext", self.constants.io80211legacy_version, self.constants.io80211legacy_path)
                support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211FamilyLegacy.kext/Contents/PlugIns/AirPortBrcmNIC.kext")["Enabled"] = True
                support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Block"], "Identifier", "com.apple.iokit.IOSkywalkFamily")["Enabled"] = True
            # This works around OCLP spoofing the Wifi card and therefore unable to actually detect the correct device
            if self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirportBrcmNIC and self.constants.validate is False and self.computer.wifi.country_code:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
                logging.info(f"- Setting Wireless Card's Country Code: {self.computer.wifi.country_code}")
                if self.computer.wifi.pci_path:
                    arpt_path = self.computer.wifi.pci_path
                    logging.info(f"- Found ARPT device at {arpt_path}")
                    self.config["DeviceProperties"]["Add"][arpt_path] = {"brcmfx-country": self.computer.wifi.country_code}
                else:
                    self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" brcmfx-country={self.computer.wifi.country_code}"
                if self.constants.enable_wake_on_wlan is True:
                    logging.info("- Enabling Wake on WLAN support")
                    self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"
            elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
                self._wifi_fake_id()
            elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4331:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
            elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
        elif isinstance(self.computer.wifi, device_probe.Atheros) and self.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True


    def _prebuilt_assumption(self) -> None:
        """
        Fall back to pre-built assumptions
        """

        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "Wireless Model" in smbios_data.smbios_dictionary[self.model]:
            return
        if smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
            logging.info("- Enabling BCM943224 and BCM94331 Networking Support")
            self._wifi_fake_id()
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm4331:
            logging.info("- Enabling BCM94328 Networking Support")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
            logging.info("- Enabling BCM94328 Networking Support")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Atheros.Chipsets.AirPortAtheros40:
            logging.info("- Enabling Atheros Networking Support")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirportBrcmNIC:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)

        if smbios_data.smbios_dictionary[self.model]["Wireless Model"] in [device_probe.Broadcom.Chipsets.AirportBrcmNIC, device_probe.Broadcom.Chipsets.AirPortBrcm4360]:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("IOSkywalkFamily.kext", self.constants.ioskywalk_version, self.constants.ioskywalk_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("IO80211FamilyLegacy.kext", self.constants.io80211legacy_version, self.constants.io80211legacy_path)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211FamilyLegacy.kext/Contents/PlugIns/AirPortBrcmNIC.kext")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Block"], "Identifier", "com.apple.iokit.IOSkywalkFamily")["Enabled"] = True


    def _wowl_handling(self) -> None:
        """
        Wake on WLAN handling

        To avoid reduced networking performance from wake, AirPortBrcmFixup is used to disable wake on WLAN by default.
        However some users may want to enable wake on WLAN, so enable if requested.
        """

        if self.constants.enable_wake_on_wlan is False:
            return
        if support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AirportBrcmFixup.kext")["Enabled"] is False:
            return

        logging.info("- Enabling Wake on WLAN support")
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"


    def _wifi_fake_id(self) -> None:
        """
        Fake Device ID Handler for BCM943224 and BCM94331 chipsets

        BCM94331 and BCM943224 are both partially supported within Big Sur's native AirPortBrcmNIC stack
        Simply adding the Device IDs and usage of AirPortBrcmFixup will restore full functionality
        """

        support.BuildSupport(self.model, self.constants, self.config).enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
        support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext")["Enabled"] = True
        if not self.constants.custom_model and self.computer.wifi and self.computer.wifi.pci_path:
            arpt_path = self.computer.wifi.pci_path
            logging.info(f"- Found ARPT device at {arpt_path}")
        else:
            if not self.model in smbios_data.smbios_dictionary:
                logging.info("No known PCI pathing for this model")
                return
            if "nForce Chipset" in smbios_data.smbios_dictionary[self.model]:
                # Nvidia chipsets all have the same path to ARPT
                arpt_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            else:
                if self.model in ("iMac7,1", "iMac8,1", "MacPro3,1", "MacBookPro4,1"):
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x0)"
                elif self.model in ("iMac13,1", "iMac13,2"):
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)"
                elif self.model in ("MacPro4,1", "MacPro5,1"):
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)"
                else:
                    # Assumes we have a laptop with Intel chipset
                    # iMac11,x-12,x also apply
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"
            logging.info(f"- Using known ARPT Path: {arpt_path}")

        if not self.constants.custom_model and self.computer.wifi and self.constants.validate is False and self.computer.wifi.country_code:
            logging.info(f"- Applying fake ID for WiFi, setting Country Code: {self.computer.wifi.country_code}")
            self.config["DeviceProperties"]["Add"][arpt_path] = {"brcmfx-country": self.computer.wifi.country_code}