"""
graphics_audio.py: Class for handling Graphics and Audio Patches, invocation from build.py
"""

import shutil
import logging
import binascii

from pathlib import Path

from . import support

from .. import constants

from ..support import utilities
from ..detections import device_probe

from ..datasets import (
    smbios_data,
    model_array,
    os_data,
    cpu_data,
    video_bios_data
)


class BuildGraphicsAudio:
    """
    Build Library for Graphics and Audio Support

    Invoke from build.py
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants
        self.computer: device_probe.Computer = self.constants.computer

        self.gfx0_path = None

        self._build()


    def _build(self) -> None:
        """
        Kick off Graphics and Audio Build Process
        """

        self._imac_mxm_patching()
        self._graphics_handling()
        self._audio_handling()
        self._firmware_handling()
        self._spoof_handling()
        self._ioaccel_workaround()


    def _graphics_handling(self) -> None:
        """
        Graphics Handling

        Primarily for Mac Pros and systems with Nvidia Maxwell/Pascal GPUs
        """

        if self.constants.allow_oc_everywhere is False and self.constants.serial_settings != "None":
            if not support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)

        # Mac Pro handling
        if self.model in model_array.MacPro:
            if not self.constants.custom_model:
                for i, device in enumerate(self.computer.gpus):
                    logging.info(f"- Found dGPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                    self.config["#Revision"][f"Hardware-MacPro-dGPU-{i + 1}"] = f"{utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}"

                    if device.pci_path and device.acpi_path:
                        logging.info(f"- Found dGPU ({i + 1}) at {device.pci_path}")
                        if isinstance(device, device_probe.AMD):
                            logging.info("- Adding Mac Pro, Xserve DRM patches")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"shikigva": 128, "unfairgva": 1, "rebuild-device-tree": 1, "agdpmod": "pikera", "enable-gva-support": 1}
                        elif isinstance(device, device_probe.NVIDIA):
                            logging.info("- Enabling Nvidia Output Patch")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"rebuild-device-tree": 1, "agdpmod": "vit9696"}
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                    else:
                        logging.info(f"- Failed to find Device path for dGPU {i + 1}")
                        if isinstance(device, device_probe.AMD):
                            logging.info("- Adding Mac Pro, Xserve DRM patches")
                            if "shikigva=128 unfairgva=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                logging.info("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 agdpmod=pikera radgva=1" + (
                                    " -wegtree" if "-wegtree" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] else ""
                                )
                        elif isinstance(device, device_probe.NVIDIA):
                            logging.info("- Enabling Nvidia Output Patch")
                            if "-wegtree agdpmod=vit9696" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                logging.info("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -wegtree agdpmod=vit9696"
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                if not self.computer.gpus:
                    logging.info("- No socketed dGPU found")

            else:
                logging.info("- Adding Mac Pro, Xserve DRM patches")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 -wegtree"

            if not support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)

        # Web Driver specific
        if not self.constants.custom_model:
            for i, device in enumerate(self.computer.gpus):
                if isinstance(device, device_probe.NVIDIA):
                    if (
                        device.arch in [device_probe.NVIDIA.Archs.Fermi, device_probe.NVIDIA.Archs.Maxwell, device_probe.NVIDIA.Archs.Pascal] or
                        (self.constants.force_nv_web is True and device.arch in [device_probe.NVIDIA.Archs.Tesla, device_probe.NVIDIA.Archs.Kepler])
                    ):
                        logging.info(f"- Enabling Web Driver Patches for GPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                        if device.pci_path and device.acpi_path:
                            if device.pci_path in self.config["DeviceProperties"]["Add"]:
                                self.config["DeviceProperties"]["Add"][device.pci_path].update({"disable-metal": 1, "force-compat": 1})
                            else:
                                self.config["DeviceProperties"]["Add"][device.pci_path] = {"disable-metal": 1, "force-compat": 1}
                            support.BuildSupport(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
                            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].update({"nvda_drv": binascii.unhexlify("31")})
                            if "nvda_drv" not in self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]:
                                self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["nvda_drv"]
                        else:
                            if "ngfxgl=1 ngfxcompat=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ngfxgl=1 ngfxcompat=1"
                            support.BuildSupport(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
                            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].update({"nvda_drv": binascii.unhexlify("31")})
                            if "nvda_drv" not in self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]:
                                self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["nvda_drv"]

    def _backlight_path_detection(self) -> None:
        """
        iMac MXM dGPU Backlight DevicePath Detection
        """

        if not self.constants.custom_model:
            for i, device in enumerate(self.computer.gpus):
                    logging.info(f"- Found dGPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                    self.config["#Revision"][f"Hardware-iMac-dGPU-{i + 1}"] = f"{utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}"

                    # Work-around for AMD Navi MXM cards with PCIe bridge
                    if not self.computer.dgpu:
                        self.computer.dgpu=self.computer.gpus[i]

                    if device.pci_path != self.computer.dgpu.pci_path:
                        logging.info("- device path and GFX0 Device path are different")
                        self.gfx0_path = device.pci_path
                        logging.info(f"- Set GFX0 Device Path: {self.gfx0_path}")
                        self.computer.dgpu.device_id = device.device_id
                        self.device_id = device.device_id
                        logging.info(f"- Found GPU Arch: {device.arch}")
                        if device.arch in [device_probe.AMD.Archs.Navi]:
                            self.computer.dgpu.arch = device.arch

                        # self.computer.dgpu.vendor_id = device.vendor_id
                        # self.vendor_id = device.vendor_id
                    else:
                        self.gfx0_path = self.computer.dgpu.pci_path
                        logging.info(f"- Found GFX0 Device Path: {self.gfx0_path}")
                        logging.info(f"- Found GPU Arch: {self.computer.dgpu.arch}")

        else:
            if not self.constants.custom_model:
                logging.info("- Failed to find GFX0 Device path, falling back on known logic")
            if self.model in ["iMac11,1", "iMac11,3"]:
                self.gfx0_path = "PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"
            elif self.model in ["iMac9,1", "iMac10,1"]:
                self.gfx0_path = "PciRoot(0x0)/Pci(0xc,0x0)/Pci(0x0,0x0)"
            else:
                self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"


    def _nvidia_mxm_patch(self, backlight_path) -> None:
        """
        iMac Nvidia Kepler MXM Handler
        """

        if not support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
            # Ensure WEG is enabled as we need if for Backlight patching
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_navi_version, self.constants.whatevergreen_navi_path)
        if self.model in ["iMac11,1", "iMac11,2", "iMac11,3", "iMac10,1"]:
            logging.info("- Adding Nvidia Brightness Control and DRM patches")
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
            logging.info("- Adding Nvidia Brightness Control and DRM patches")
            self.config["DeviceProperties"]["Add"][backlight_path] = {
                "applbkl": binascii.unhexlify("01000000"),
                "@0,backlight-control": binascii.unhexlify("01000000"),
                "@0,built-in": binascii.unhexlify("01000000"),
                "shikigva": 256,
                "agdpmod": "vit9696",
            }
            logging.info("- Disabling unsupported iGPU")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                "name": binascii.unhexlify("23646973706C6179"),
                "class-code": binascii.unhexlify("FFFFFFFF"),
            }
        shutil.copy(self.constants.backlight_injector_path, self.constants.kexts_path)
        support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("BacklightInjector.kext")["Enabled"] = True
        self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
        self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True


    def _amd_mxm_patch(self, backlight_path) -> None:
        """
        iMac AMD GCN and Navi MXM Handler
        """

        logging.info("- Adding AMD DRM patches")
        if not support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
            # Ensure WEG is enabled as we need if for Backlight patching
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("WhateverGreen.kext", self.constants.whatevergreen_navi_version, self.constants.whatevergreen_navi_path)

        if self.model == "iMac9,1":
            logging.info("- Adding iMac9,1 Brightness Control and DRM patches")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("BacklightInjector.kext", self.constants.backlight_injectorA_version, self.constants.backlight_injectorA_path)

        if not self.constants.custom_model:
            if self.computer.dgpu.device_id == 0x7340:
                logging.info(f"- Adding AMD RX5500XT vBIOS injection")
                self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1, "ATY,bin_image": binascii.unhexlify(video_bios_data.RX5500XT_64K) }
                logging.info(f"- Adding AMD RX5500XT boot-args")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " agdpmod=pikera applbkl=3"
            elif self.computer.dgpu.device_id_unspoofed == 0x6981:
                logging.info(f"- Adding AMD WX3200 device spoofing")
                self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1, "model": "AMD Radeon Pro WX 3200", "device-id": binascii.unhexlify("FF67")}
            else:
                self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}
        else:
             self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}

        if self.constants.custom_model and self.model == "iMac11,2":
            # iMac11,2 can have either PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0) or PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
            # Set both properties when we cannot run hardware detection
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}
        if self.model in ["iMac12,1", "iMac12,2"]:
            logging.info("- Disabling unsupported iGPU")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                "name": binascii.unhexlify("23646973706C6179"),
                "class-code": binascii.unhexlify("FFFFFFFF"),
            }
        elif self.model in ["iMac9,1", "iMac10,1"]:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path)
        if self.computer and self.computer.dgpu:
            if self.computer.dgpu.arch == device_probe.AMD.Archs.Legacy_GCN_7000:
                logging.info("- Adding Legacy GCN Power Gate Patches")
                self.config["DeviceProperties"]["Add"][backlight_path].update({
                    "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                    "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                    "CAIL,CAIL_DisableUVDPowerGating": 1,
                    "CAIL,CAIL_DisableVCEPowerGating": 1,
                })
        if self.constants.imac_model == "GCN":
            logging.info("- Adding Legacy GCN Power Gate Patches")
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
        elif self.constants.imac_model == "Lexa":
            logging.info("- Adding Lexa Spoofing Patches")
            self.config["DeviceProperties"]["Add"][backlight_path].update({
                "model": "AMD Radeon Pro WX 3200",
                "device-id": binascii.unhexlify("FF67"),
            })
            if self.model == "iMac11,2":
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"].update({
                    "model": "AMD Radeon Pro WX 3200",
                    "device-id": binascii.unhexlify("FF67"),
                })
        elif self.constants.imac_model == "Navi":
            logging.info("- Adding Navi Spoofing Patches")
            navi_backlight_path = backlight_path+"/Pci(0x0,0x0)/Pci(0x0,0x0)"
            self.config["DeviceProperties"]["Add"][navi_backlight_path] = {
                "ATY,bin_image": binascii.unhexlify(video_bios_data.RX5500XT_64K),
                "shikigva": 128,
                "unfairgva": 1,
                "rebuild-device-tree": 1,
                "enable-gva-support": 1
            }
            logging.info(f"- Adding AMD RX5500XT boot-args")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " agdpmod=pikera applbkl=3"


    def _audio_handling(self) -> None:
        """
        Audio Handler
        """

        if (self.model in model_array.LegacyAudio or self.model in model_array.MacPro) and self.constants.set_alc_usage is True:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)

        # Audio Patch
        if self.constants.set_alc_usage is True:
            if smbios_data.smbios_dictionary[self.model]["Max OS Supported"] <= os_data.os_data.high_sierra:
                # Models dropped in Mojave also lost Audio support
                # Xserves and MacPro4,1 are exceptions
                # iMac7,1 and iMac8,1 require AppleHDA/IOAudioFamily downgrade
                if not (self.model.startswith("Xserve") or self.model in ["MacPro4,1", "iMac7,1", "iMac8,1"]):
                    if "nForce Chipset" in smbios_data.smbios_dictionary[self.model]:
                        hdef_path = "PciRoot(0x0)/Pci(0x8,0x0)"
                    else:
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
                    support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)
            elif (self.model.startswith("MacPro") and self.model != "MacPro6,1") or self.model.startswith("Xserve"):
                # Used to enable Audio support for non-standard dGPUs
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)

        # Due to regression in AppleALC 1.6.4+, temporarily use 1.6.3 and set override
        if support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleALC.kext")["Enabled"] is True:
            if "-lilubetaall" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -lilubetaall"


    def _firmware_handling(self) -> None:
        """
        Firmware Handler
        """

        # Add UGA to GOP layer
        if "UGA Graphics" in smbios_data.smbios_dictionary[self.model]:
            logging.info("- Adding UGA to GOP Patch")
            self.config["UEFI"]["Output"]["GopPassThrough"] = "Apple"

        # GMUX handling
        if self.constants.software_demux is True and self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            logging.info("- Enabling software demux")
            # Add ACPI patches
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-DGPU.aml")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "_INI to XINI")["Enabled"] = True
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
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AMDGPUWakeHandler.kext", self.constants.gpu_wake_version, self.constants.gpu_wake_path)

        if self.constants.dGPU_switch is True and "Switchable GPUs" in smbios_data.smbios_dictionary[self.model]:
            logging.info("- Allowing GMUX switching in Windows")
            self.config["Booter"]["Quirks"]["SignalAppleOS"] = True

        # Force Output support PC VBIOS on Mac Pros
        if self.constants.force_output_support is True:
            logging.info("- Forcing GOP Support")
            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

        # AMD GOP VBIOS injection for AMD GCN 1-4 GPUs
        if self.constants.amd_gop_injection is True:
            logging.info("- Adding AMDGOP.efi")
            shutil.copy(self.constants.amd_gop_driver_path, self.constants.drivers_path)
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("AMDGOP.efi", "UEFI", "Drivers")["Enabled"] = True

        # Nvidia Kepler GOP VBIOS injection
        if self.constants.nvidia_kepler_gop_injection is True:
            logging.info("- Adding NVGOP_GK.efi")
            shutil.copy(self.constants.nvidia_kepler_gop_driver_path, self.constants.drivers_path)
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("NVGOP_GK.efi", "UEFI", "Drivers")["Enabled"] = True


    def _spoof_handling(self) -> None:
        """
        SMBIOS Spoofing Handler
        """

        if self.constants.serial_settings == "None":
            return

        # AppleMuxControl Override
        if self.model == "MacBookPro9,1":
            logging.info("- Adding AppleMuxControl Override")
            amc_map_path = Path(self.constants.plist_folder_path) / Path("AppleMuxControl/Info.plist")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "vit9696"}
            Path(self.constants.amc_kext_folder).mkdir()
            Path(self.constants.amc_contents_folder).mkdir()
            shutil.copy(amc_map_path, self.constants.amc_contents_folder)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AMC-Override.kext")["Enabled"] = True

        if self.model not in model_array.NoAGPMSupport:
            logging.info("- Adding AppleGraphicsPowerManagement Override")
            agpm_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsPowerManagement/Info.plist")
            Path(self.constants.agpm_kext_folder).mkdir()
            Path(self.constants.agpm_contents_folder).mkdir()
            shutil.copy(agpm_map_path, self.constants.agpm_contents_folder)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AGPM-Override.kext")["Enabled"] = True

        if self.model in model_array.AGDPSupport:
            logging.info("- Adding AppleGraphicsDevicePolicy Override")
            agdp_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsDevicePolicy/Info.plist")
            Path(self.constants.agdp_kext_folder).mkdir()
            Path(self.constants.agdp_contents_folder).mkdir()
            shutil.copy(agdp_map_path, self.constants.agdp_contents_folder)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AGDP-Override.kext")["Enabled"] = True

        # AGPM Patch
        if self.model in model_array.DualGPUPatch:
            logging.info("- Adding dual GPU patch")
            if not self.constants.custom_model and self.computer.dgpu and self.computer.dgpu.pci_path:
                self.gfx0_path = self.computer.dgpu.pci_path
                logging.info(f"- Found GFX0 Device Path: {self.gfx0_path}")
            else:
                if not self.constants.custom_model:
                    logging.info("- Failed to find GFX0 Device path, falling back on known logic")
                self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"

            if self.model in model_array.IntelNvidiaDRM and self.constants.drm_support is True:
                logging.info("- Prioritizing DRM support over Intel QuickSync")
                self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696", "shikigva": 256}
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                    "name": binascii.unhexlify("23646973706C6179"),
                    "IOName": "#display",
                    "class-code": binascii.unhexlify("FFFFFFFF"),
                }
            elif self.constants.serial_settings != "None":
                if self.gfx0_path not in self.config["DeviceProperties"]["Add"] or "agdpmod" not in self.config["DeviceProperties"]["Add"][self.gfx0_path]:
                    self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696"}

        if self.model.startswith("iMac14,1"):
            # Ensure that agdpmod is applied to iMac14,x with iGPU only
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {"agdpmod": "vit9696"}


    def _imac_mxm_patching(self) -> None:
        """
        General iMac MXM Handler
        """

        self._backlight_path_detection()
        # Check GPU Vendor
        if self.constants.metal_build is True:
            logging.info("- Adding Metal GPU patches on request")
            if self.constants.imac_vendor == "AMD":
                self._amd_mxm_patch(self.gfx0_path)
            elif self.constants.imac_vendor == "Nvidia":
                self._nvidia_mxm_patch(self.gfx0_path)
            else:
                logging.info("- Failed to find vendor")
        elif not self.constants.custom_model and self.model in model_array.LegacyGPU and self.computer.dgpu:
            logging.info(f"- Detected dGPU: {utilities.friendly_hex(self.computer.dgpu.vendor_id)}:{utilities.friendly_hex(self.computer.dgpu.device_id)}")
            if self.computer.dgpu.arch in [
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000,
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Polaris_Spoof,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                self._amd_mxm_patch(self.gfx0_path)
            elif self.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                self._nvidia_mxm_patch(self.gfx0_path)

    def _ioaccel_workaround(self) -> None:
        """
        Miscellaneous IOAccelerator Handler

        When MTL bundles are missing from disk, WindowServer will repeatedly crash
        This primarily occurs when installing an RSR update, where root is cleaned but AuxKC is not
        """

        gpu_archs = []
        if not self.constants.custom_model:
            gpu_archs = [gpu.arch for gpu in self.constants.computer.gpus]
        else:
            if self.model not in smbios_data.smbios_dictionary:
                return
            gpu_archs = smbios_data.smbios_dictionary[self.model]["Stock GPUs"]

        # Check if KDKless and KDK GPUs are present
        # We only want KDKless.kext if there are no KDK GPUs
        has_kdkless_gpu = False
        has_kdk_gpu = False
        for arch in gpu_archs:
            if arch in [
                device_probe.Intel.Archs.Ivy_Bridge,
                device_probe.Intel.Archs.Haswell,
                device_probe.Intel.Archs.Broadwell,
                device_probe.Intel.Archs.Skylake,
                device_probe.NVIDIA.Archs.Kepler,
            ]:
                has_kdkless_gpu = True

            # Non-Metal KDK
            if arch in [
                device_probe.NVIDIA.Archs.Tesla,
                device_probe.NVIDIA.Archs.Maxwell,
                device_probe.NVIDIA.Archs.Pascal,
                device_probe.AMD.Archs.TeraScale_1,
                device_probe.AMD.Archs.TeraScale_2,
                device_probe.Intel.Archs.Iron_Lake,
                device_probe.Intel.Archs.Sandy_Bridge,
            ]:
                has_kdk_gpu = True

            if arch in [
                # Metal KDK (always)
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000,
            ]:
                has_kdk_gpu = True

            if arch in [
                # Metal KDK (pre-AVX2.0)
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Polaris_Spoof,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                if (
                    self.model == "MacBookPro13,3" or
                    smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.ivy_bridge.value
                ):
                    # MacBookPro13,3 has AVX2.0 however the GPU has an unsupported framebuffer
                    has_kdk_gpu = True

        if has_kdkless_gpu is True and has_kdk_gpu is False:
            # KDKlessWorkaround is required for KDKless GPUs
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("KDKlessWorkaround.kext", self.constants.kdkless_version, self.constants.kdkless_path)
            return

        # KDKlessWorkaround supports disabling native AMD stack on Ventura for pre-AVX2.0 CPUs
        # Applicable for Polaris, Vega, Navi GPUs
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] > cpu_data.CPUGen.ivy_bridge.value:
            return
        for arch in gpu_archs:
            if arch in [
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Polaris_Spoof,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("KDKlessWorkaround.kext", self.constants.kdkless_version, self.constants.kdkless_path)
                return
