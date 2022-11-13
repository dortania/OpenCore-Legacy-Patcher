from resources import constants, device_probe
from resources.build import support
from data import smbios_data, bluetooth_data

class build_bluetooth:

    def __init__(self, model, versions, config):
        self.model = model
        self.constants: constants.Constants = versions
        self.config = config
        self.computer = self.constants.computer


    def build(self):
        # Bluetooth patches
        if not self.constants.custom_model and self.computer.bluetooth_chipset:
            self.on_model()
        else:
            self.prebuilt_assumption()


    def on_model(self):
        if self.computer.bluetooth_chipset in ["BRCM2070 Hub", "BRCM2046 Hub"]:
            print("- Fixing Legacy Bluetooth for macOS Monterey")
            support.build_support(self.model, self.constants, self.config).enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("Bluetooth-Spoof.kext", self.constants.btspoof_version, self.constants.btspoof_path)
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -btlfxallowanyaddr"
        elif self.computer.bluetooth_chipset == "BRCM20702 Hub":
            # BCM94331 can include either BCM2070 or BRCM20702 v1 Bluetooth chipsets
            # Note Monterey only natively supports BRCM20702 v2 (found with BCM94360)
            # Due to this, BlueToolFixup is required to resolve Firmware Uploading on legacy chipsets
            if self.computer.wifi:
                if self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
                    print("- Fixing Legacy Bluetooth for macOS Monterey")
                    support.build_support(self.model, self.constants, self.config).enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
        elif self.computer.bluetooth_chipset == "3rd Party Bluetooth 4.0 Hub":
            print("- Detected 3rd Party Bluetooth Chipset")
            support.build_support(self.model, self.constants, self.config).enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
            print("- Enabling Bluetooth FeatureFlags")
            self.config["Kernel"]["Quirks"]["ExtendBTFeatureFlags"] = True


    def prebuilt_assumption(self):
        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "Bluetooth Model" in smbios_data.smbios_dictionary[self.model]:
            return

        if smbios_data.smbios_dictionary[self.model]["Bluetooth Model"] <= bluetooth_data.bluetooth_data.BRCM20702_v1.value:
            print("- Fixing Legacy Bluetooth for macOS Monterey")
            support.build_support(self.model, self.constants, self.config).enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
            if smbios_data.smbios_dictionary[self.model]["Bluetooth Model"] <= bluetooth_data.bluetooth_data.BRCM2070.value:
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -btlfxallowanyaddr"
                support.build_support(self.model, self.constants, self.config).enable_kext("Bluetooth-Spoof.kext", self.constants.btspoof_version, self.constants.btspoof_path)