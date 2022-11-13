from resources import constants, device_probe
from resources.build import support
from data import smbios_data, cpu_data

class build_wired:

    def __init__(self, model, versions, config):
        self.model = model
        self.constants: constants.Constants = versions
        self.config = config
        self.computer = self.constants.computer

    def build(self):
        # Check if Ethernet was detected, otherwise fall back to assumptions (mainly for 2011 MacBook Airs and TB Ethernet)
        if not self.constants.custom_model and self.constants.computer.ethernet:
            self.on_model()
        else:
            self.prebuilt_assumption()

    def on_model(self):
        # On-model hardware detection
        for controller in self.constants.computer.ethernet:
            if isinstance(controller, device_probe.BroadcomEthernet) and controller.chipset == device_probe.BroadcomEthernet.Chipsets.AppleBCM5701Ethernet:
                if not self.model in smbios_data.smbios_dictionary:
                    continue
                if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
                    # Required due to Big Sur's BCM5701 requiring VT-D support
                    # Applicable for pre-Ivy Bridge models
                    support.build_support(self.model, self.constants, self.config).enable_kext("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path)
            elif isinstance(controller, device_probe.IntelEthernet):
                if not self.model in smbios_data.smbios_dictionary:
                    continue
                if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
                    # Apple's IOSkywalkFamily in DriverKit requires VT-D support
                    # Applicable for pre-Ivy Bridge models
                    if controller.chipset == device_probe.IntelEthernet.Chipsets.AppleIntelI210Ethernet:
                        support.build_support(self.model, self.constants, self.config).enable_kext("CatalinaIntelI210Ethernet.kext", self.constants.i210_version, self.constants.i210_path)
                    elif controller.chipset == device_probe.IntelEthernet.Chipsets.AppleIntel8254XEthernet:
                        support.build_support(self.model, self.constants, self.config).enable_kext("AppleIntel8254XEthernet.kext", self.constants.intel_8254x_version, self.constants.intel_8254x_path)
                    elif controller.chipset == device_probe.IntelEthernet.Chipsets.Intel82574L:
                        support.build_support(self.model, self.constants, self.config).enable_kext("Intel82574L.kext", self.constants.intel_82574l_version, self.constants.intel_82574l_path)
            elif isinstance(controller, device_probe.NVIDIAEthernet):
                support.build_support(self.model, self.constants, self.config).enable_kext("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path)
            elif isinstance(controller, device_probe.Marvell) or isinstance(controller, device_probe.SysKonnect):
                support.build_support(self.model, self.constants, self.config).enable_kext("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path)

    def prebuilt_assumption(self):
        # Stock hardware assumptions
        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "Ethernet Chipset" in smbios_data.smbios_dictionary[self.model]:
            return

        if smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Broadcom":
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
                # Required due to Big Sur's BCM5701 requiring VT-D support
                # Applicable for pre-Ivy Bridge models
                support.build_support(self.model, self.constants, self.config).enable_kext("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Nvidia":
            support.build_support(self.model, self.constants, self.config).enable_kext("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Marvell":
            support.build_support(self.model, self.constants, self.config).enable_kext("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Intel 80003ES2LAN":
            support.build_support(self.model, self.constants, self.config).enable_kext("AppleIntel8254XEthernet.kext", self.constants.intel_8254x_version, self.constants.intel_8254x_path)
        elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Intel 82574L":
            support.build_support(self.model, self.constants, self.config).enable_kext("Intel82574L.kext", self.constants.intel_82574l_version, self.constants.intel_82574l_path)