# Class for handling Graphics and Audio Patches, invocation from build.py
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

from resources import constants, device_probe, utilities
from resources.build import support
from data import smbios_data, model_array, os_data

from pathlib import Path

import shutil, binascii

class build_graphics_audio:

    def __init__(self, model, versions, config):
        self.model = model
        self.constants: constants.Constants = versions
        self.config = config
        self.computer = self.constants.computer

        self.gfx0_path = None


    def build(self):
        self.graphics_handling()
        self.audio_handling()
        self.firmware_handling()
        self.spoof_handling()
        self.imac_mxm_patching()


    def graphics_handling(self):
        if self.constants.allow_oc_everywhere is False and self.constants.serial_settings != "None":
            support.build_support(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)

        # Mac Pro handling
        if self.model in model_array.MacPro:
            if not self.constants.custom_model:
                for i, device in enumerate(self.computer.gpus):
                    print(f"- Found dGPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                    self.config["#Revision"][f"Hardware-MacPro-dGPU-{i + 1}"] = f"{utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}"

                    if device.pci_path and device.acpi_path:
                        print(f"- Found dGPU ({i + 1}) at {device.pci_path}")
                        if isinstance(device, device_probe.AMD):
                            print("- Adding Mac Pro, Xserve DRM patches")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"shikigva": 128, "unfairgva": 1, "rebuild-device-tree": 1, "agdpmod": "pikera", "enable-gva-support": 1}
                        elif isinstance(device, device_probe.NVIDIA):
                            print("- Enabling Nvidia Output Patch")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"rebuild-device-tree": 1, "agdpmod": "vit9696"}
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                    else:
                        print(f"- Failed to find Device path for dGPU {i + 1}")
                        if isinstance(device, device_probe.AMD):
                            print("- Adding Mac Pro, Xserve DRM patches")
                            if "shikigva=128 unfairgva=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                print("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 agdpmod=pikera radgva=1" + (
                                    " -wegtree" if "-wegtree" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] else ""
                                )
                        elif isinstance(device, device_probe.NVIDIA):
                            print("- Enabling Nvidia Output Patch")
                            if "-wegtree agdpmod=vit9696" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                print("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -wegtree agdpmod=vit9696"
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                if not self.computer.gpus:
                    print("- No socketed dGPU found")

            else:
                print("- Adding Mac Pro, Xserve DRM patches")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 -wegtree"

            if not support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
                support.build_support(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)

        # Web Driver specific
        if not self.constants.custom_model:
            for i, device in enumerate(self.computer.gpus):
                if isinstance(device, device_probe.NVIDIA):
                    if (
                        device.arch in [device_probe.NVIDIA.Archs.Fermi, device_probe.NVIDIA.Archs.Maxwell, device_probe.NVIDIA.Archs.Pascal] or
                        (self.constants.force_nv_web is True and device.arch in [device_probe.NVIDIA.Archs.Tesla, device_probe.NVIDIA.Archs.Kepler])
                    ):
                        print(f"- Enabling Web Driver Patches for GPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                        if device.pci_path and device.acpi_path:
                            if device.pci_path in self.config["DeviceProperties"]["Add"]:
                                self.config["DeviceProperties"]["Add"][device.pci_path].update({"disable-metal": 1, "force-compat": 1})
                            else:
                                self.config["DeviceProperties"]["Add"][device.pci_path] = {"disable-metal": 1, "force-compat": 1}
                            support.build_support(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
                            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].update({"nvda_drv": binascii.unhexlify("31")})
                            if "nvda_drv" not in self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]:
                                self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["nvda_drv"]
                        else:
                            if "ngfxgl=1 ngfxcompat=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ngfxgl=1 ngfxcompat=1"
                            support.build_support(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
                            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].update({"nvda_drv": binascii.unhexlify("31")})
                            if "nvda_drv" not in self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]:
                                self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["nvda_drv"]


    def backlight_path_detection(self):
        if not self.constants.custom_model and self.computer.dgpu and self.computer.dgpu.pci_path:
            self.gfx0_path = self.computer.dgpu.pci_path
            print(f"- Found GFX0 Device Path: {self.gfx0_path}")
        else:
            if not self.constants.custom_model:
                print("- Failed to find GFX0 Device path, falling back on known logic")
            if self.model in ["iMac11,1", "iMac11,3"]:
                self.gfx0_path = "PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"
            elif self.model == "iMac10,1":
                self.gfx0_path = "PciRoot(0x0)/Pci(0xc,0x0)/Pci(0x0,0x0)"
            else:
                self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"


    def nvidia_mxm_patch(self, backlight_path):
        if not support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
            # Ensure WEG is enabled as we need if for Backlight patching
            support.build_support(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
        if self.model in ["iMac11,1", "iMac11,2", "iMac11,3", "iMac10,1"]:
            print("- Adding Nvidia Brightness Control and DRM patches")
            self.config["DeviceProperties"]["Add"][backlight_path] = {
                "applbkl": binascii.unhexlify("01000000"),
                "@0,backlight-control": binascii.unhexlify("01000000"),
                "@0,built-in": binascii.unhexlify("01000000"),
                "shikigva": 256,
                "agdpmod": "vit9696",
            }
            if self.constants.custom_model and self.model == "iMac11,2":
                # iMac11,2 can have either PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0) or PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
                # Set both properties when we cannot run hardware detection
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"] = {
                    "applbkl": binascii.unhexlify("01000000"),
                    "@0,backlight-control": binascii.unhexlify("01000000"),
                    "@0,built-in": binascii.unhexlify("01000000"),
                    "shikigva": 256,
                    "agdpmod": "vit9696",
                }
        elif self.model in ["iMac12,1", "iMac12,2"]:
            print("- Adding Nvidia Brightness Control and DRM patches")
            self.config["DeviceProperties"]["Add"][backlight_path] = {
                "applbkl": binascii.unhexlify("01000000"),
                "@0,backlight-control": binascii.unhexlify("01000000"),
                "@0,built-in": binascii.unhexlify("01000000"),
                "shikigva": 256,
                "agdpmod": "vit9696",
            }
            print("- Disabling unsupported iGPU")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                "name": binascii.unhexlify("23646973706C6179"),
                "IOName": "#display",
                "class-code": binascii.unhexlify("FFFFFFFF"),
            }
        shutil.copy(self.constants.backlight_injector_path, self.constants.kexts_path)
        support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("BacklightInjector.kext")["Enabled"] = True
        self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
        self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True


    def amd_mxm_patch(self, backlight_path):
        print("- Adding AMD DRM patches")
        if not support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
            # Ensure WEG is enabled as we need if for Backlight patching
            support.build_support(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
        self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}
        if self.constants.custom_model and self.model == "iMac11,2":
            # iMac11,2 can have either PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0) or PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
            # Set both properties when we cannot run hardware detection
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}
        if self.model in ["iMac12,1", "iMac12,2"]:
            print("- Disabling unsupported iGPU")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                "name": binascii.unhexlify("23646973706C6179"),
                "IOName": "#display",
                "class-code": binascii.unhexlify("FFFFFFFF"),
            }
        elif self.model == "iMac10,1":
            support.build_support(self.model, self.constants, self.config).enable_kext("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path)
        if self.computer and self.computer.dgpu:
            if self.computer.dgpu.arch == device_probe.AMD.Archs.Legacy_GCN_7000:
                print("- Adding Legacy GCN Power Gate Patches")
                self.config["DeviceProperties"]["Add"][backlight_path].update({
                    "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                    "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                    "CAIL,CAIL_DisableUVDPowerGating": 1,
                    "CAIL,CAIL_DisableVCEPowerGating": 1,
                })
        if self.constants.imac_model == "Legacy GCN":
            print("- Adding Legacy GCN Power Gate Patches")
            self.config["DeviceProperties"]["Add"][backlight_path].update({
                "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                "CAIL,CAIL_DisableUVDPowerGating": 1,
                "CAIL,CAIL_DisableVCEPowerGating": 1,
            })
            if self.model == "iMac11,2":
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"].update({
                    "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                    "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                    "CAIL,CAIL_DisableUVDPowerGating": 1,
                    "CAIL,CAIL_DisableVCEPowerGating": 1,
                })


    def audio_handling(self):
        if (self.model in model_array.LegacyAudio or self.model in model_array.MacPro) and self.constants.set_alc_usage is True:
            support.build_support(self.model, self.constants, self.config).enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)

        # Audio Patch
        if self.constants.set_alc_usage is True:
            if smbios_data.smbios_dictionary[self.model]["Max OS Supported"] <= os_data.os_data.high_sierra:
                # Models dropped in Mojave also lost Audio support
                # Xserves and MacPro4,1 are exceptions
                # iMac7,1 and iMac8,1 require AppleHDA/IOAudioFamily downgrade
                if not (self.model.startswith("Xserve") or self.model in ["MacPro4,1", "iMac7,1", "iMac8,1"]):
                    try:
                        smbios_data.smbios_dictionary[self.model]["nForce Chipset"]
                        hdef_path = "PciRoot(0x0)/Pci(0x8,0x0)"
                    except KeyError:
                        hdef_path = "PciRoot(0x0)/Pci(0x1b,0x0)"
                    # In AppleALC, MacPro3,1's original layout is already in use, forcing layout 13 instead
                    if self.model == "MacPro3,1":
                        self.config["DeviceProperties"]["Add"][hdef_path] = {
                            "apple-layout-id": 90,
                            "use-apple-layout-id": 1,
                            "alc-layout-id": 13,
                        }
                    else:
                        self.config["DeviceProperties"]["Add"][hdef_path] = {
                            "apple-layout-id": 90,
                            "use-apple-layout-id": 1,
                            "use-layout-id": 1,
                        }
                    support.build_support(self.model, self.constants, self.config).enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)
            elif (self.model.startswith("MacPro") and self.model != "MacPro6,1") or self.model.startswith("Xserve"):
                # Used to enable Audio support for non-standard dGPUs
                support.build_support(self.model, self.constants, self.config).enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)


    def firmware_handling(self):
        # Add UGA to GOP layer
        if "UGA Graphics" in smbios_data.smbios_dictionary[self.model]:
            print("- Adding UGA to GOP Patch")
            self.config["UEFI"]["Output"]["GopPassThrough"] = "Apple"

        # GMUX handling
        if self.constants.software_demux is True and self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            print("- Enabling software demux")
            # Add ACPI patches
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-DGPU.aml")["Enabled"] = True
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "_INI to XINI")["Enabled"] = True
            shutil.copy(self.constants.demux_ssdt_path, self.constants.acpi_path)
            # Disable dGPU
            # IOACPIPlane:/_SB/PCI0@0/P0P2@10000/GFX0@0
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {
                "class-code": binascii.unhexlify("FFFFFFFF"),
                "device-id": binascii.unhexlify("FFFF0000"),
                "IOName": "Dortania Disabled Card",
                "name": "Dortania Disabled Card"
            }
            self.config["DeviceProperties"]["Delete"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = ["class-code", "device-id", "IOName", "name"]
            # Add AMDGPUWakeHandler
            support.build_support(self.model, self.constants, self.config).enable_kext("AMDGPUWakeHandler.kext", self.constants.gpu_wake_version, self.constants.gpu_wake_path)

        if self.constants.dGPU_switch is True and "Switchable GPUs" in smbios_data.smbios_dictionary[self.model]:
            print("- Allowing GMUX switching in Windows")
            self.config["Booter"]["Quirks"]["SignalAppleOS"] = True

        # Force Output support PC VBIOS on Mac Pros
        if self.constants.force_output_support is True:
            print("- Forcing GOP Support")
            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

    def spoof_handling(self):
        if self.constants.serial_settings == "None":
            return

        # AppleMuxControl Override
        if self.model == "MacBookPro9,1":
            print("- Adding AppleMuxControl Override")
            amc_map_path = Path(self.constants.plist_folder_path) / Path("AppleMuxControl/Info.plist")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "vit9696"}
            Path(self.constants.amc_kext_folder).mkdir()
            Path(self.constants.amc_contents_folder).mkdir()
            shutil.copy(amc_map_path, self.constants.amc_contents_folder)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AMC-Override.kext")["Enabled"] = True

        if self.model not in model_array.NoAGPMSupport:
            print("- Adding AppleGraphicsPowerManagement Override")
            agpm_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsPowerManagement/Info.plist")
            Path(self.constants.agpm_kext_folder).mkdir()
            Path(self.constants.agpm_contents_folder).mkdir()
            shutil.copy(agpm_map_path, self.constants.agpm_contents_folder)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AGPM-Override.kext")["Enabled"] = True

        if self.model in model_array.AGDPSupport:
            print("- Adding AppleGraphicsDevicePolicy Override")
            agdp_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsDevicePolicy/Info.plist")
            Path(self.constants.agdp_kext_folder).mkdir()
            Path(self.constants.agdp_contents_folder).mkdir()
            shutil.copy(agdp_map_path, self.constants.agdp_contents_folder)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AGDP-Override.kext")["Enabled"] = True

        # AGPM Patch
        if self.model in model_array.DualGPUPatch:
            print("- Adding dual GPU patch")
            if not self.constants.custom_model and self.computer.dgpu and self.computer.dgpu.pci_path:
                self.gfx0_path = self.computer.dgpu.pci_path
                print(f"- Found GFX0 Device Path: {self.gfx0_path}")
            else:
                if not self.constants.custom_model:
                    print("- Failed to find GFX0 Device path, falling back on known logic")
                self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"

            if self.model in model_array.IntelNvidiaDRM and self.constants.drm_support is True:
                print("- Prioritizing DRM support over Intel QuickSync")
                self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696", "shikigva": 256}
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                    "name": binascii.unhexlify("23646973706C6179"),
                    "IOName": "#display",
                    "class-code": binascii.unhexlify("FFFFFFFF"),
                }
            elif self.constants.serial_settings != "None":
                self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696"}

        if self.model.startswith("iMac14,1"):
            # Ensure that agdpmod is applied to iMac14,x with iGPU only
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {"agdpmod": "vit9696"}


    def imac_mxm_patching(self):
        # Check GPU Vendor
        if self.constants.metal_build is True:
            self.backlight_path_detection()
            print("- Adding Metal GPU patches on request")
            if self.constants.imac_vendor == "AMD":
                self.amd_mxm_patch(self.gfx0_path)
            elif self.constants.imac_vendor == "Nvidia":
                self.nvidia_mxm_patch(self.gfx0_path)
            else:
                print("- Failed to find vendor")
        elif not self.constants.custom_model and self.model in model_array.LegacyGPU and self.computer.dgpu:
            print(f"- Detected dGPU: {utilities.friendly_hex(self.computer.dgpu.vendor_id)}:{utilities.friendly_hex(self.computer.dgpu.device_id)}")
            if self.computer.dgpu.arch in [
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000,
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                self.backlight_path_detection()
                self.amd_mxm_patch(self.gfx0_path)
            elif self.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                self.backlight_path_detection()
                self.nvidia_mxm_patch(self.gfx0_path)