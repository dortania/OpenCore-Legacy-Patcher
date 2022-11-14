# Class for handling Wireless Networking Patches, invocation from build.py
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

from resources import constants, device_probe, utilities
from resources.build import support
from data import smbios_data

class build_wireless:

    def __init__(self, model, versions, config):
        self.model = model
        self.constants: constants.Constants = versions
        self.config = config
        self.computer = self.constants.computer


    def build(self):
        # WiFi patches
        if not self.constants.custom_model and self.constants.computer.wifi:
            self.on_model()
        else:
            self.prebuilt_assumption()
        self.wowl_handling()


    def on_model(self):
        print(f"- Found Wireless Device {utilities.friendly_hex(self.computer.wifi.vendor_id)}:{utilities.friendly_hex(self.computer.wifi.device_id)}")
        self.config["#Revision"]["Hardware-Wifi"] = f"{utilities.friendly_hex(self.computer.wifi.vendor_id)}:{utilities.friendly_hex(self.computer.wifi.device_id)}"

        if isinstance(self.computer.wifi, device_probe.Broadcom):
            # This works around OCLP spoofing the Wifi card and therefore unable to actually detect the correct device
            if self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirportBrcmNIC and self.constants.validate is False and self.computer.wifi.country_code:
                support.build_support(self.model, self.constants, self.config).enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
                print(f"- Setting Wireless Card's Country Code: {self.computer.wifi.country_code}")
                if self.computer.wifi.pci_path:
                    arpt_path = self.computer.wifi.pci_path
                    print(f"- Found ARPT device at {arpt_path}")
                    self.config["DeviceProperties"]["Add"][arpt_path] = {"brcmfx-country": self.computer.wifi.country_code}
                else:
                    self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" brcmfx-country={self.computer.wifi.country_code}"
                if self.constants.enable_wake_on_wlan is True:
                    print("- Enabling Wake on WLAN support")
                    self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"
            elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
                self.wifi_fake_id()
            elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4331:
                support.build_support(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                support.build_support(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
            elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
                support.build_support(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                support.build_support(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
        elif isinstance(self.computer.wifi, device_probe.Atheros) and self.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40:
            support.build_support(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True


    def prebuilt_assumption(self):
        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "Wireless Model" in smbios_data.smbios_dictionary[self.model]:
            return
        if smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
            print("- Enabling BCM943224 and BCM94331 Networking Support")
            self.wifi_fake_id()
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm4331:
            print("- Enabling BCM94328 Networking Support")
            support.build_support(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
            print("- Enabling BCM94328 Networking Support")
            support.build_support(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Atheros.Chipsets.AirPortAtheros40:
            print("- Enabling Atheros Networking Support")
            support.build_support(self.model, self.constants, self.config).enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True
        elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirportBrcmNIC:
            support.build_support(self.model, self.constants, self.config).enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)


    def wowl_handling(self):
        # To avoid reduced networking performance from wake, AirPortBrcmFixup is used to disable wake on WLAN by default.
        # However some users may want to enable wake on WLAN, so enable if requested.
        if self.constants.enable_wake_on_wlan is False:
            return
        if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AirportBrcmFixup.kext")["Enabled"] is False:
            return

        print("- Enabling Wake on WLAN support")
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"


    def wifi_fake_id(self):
        # BCM94331 and BCM943224 are both partially supported within Big Sur's native AirPortBrcmNIC stack
        # Simply adding the Device IDs and usage of AirPortBrcmFixup will restore full functionality
        support.build_support(self.model, self.constants, self.config).enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
        support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext")["Enabled"] = True
        if not self.constants.custom_model and self.computer.wifi and self.computer.wifi.pci_path:
            arpt_path = self.computer.wifi.pci_path
            print(f"- Found ARPT device at {arpt_path}")
        else:
            if not self.model in smbios_data.smbios_dictionary:
                print("No known PCI pathing for this model")
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
            print(f"- Using known ARPT Path: {arpt_path}")

        if not self.constants.custom_model and self.computer.wifi and self.constants.validate is False and self.computer.wifi.country_code:
            print(f"- Applying fake ID for WiFi, setting Country Code: {self.computer.wifi.country_code}")
            self.config["DeviceProperties"]["Add"][arpt_path] = {"brcmfx-country": self.computer.wifi.country_code}