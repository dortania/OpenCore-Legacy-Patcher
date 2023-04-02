# Hardware Detection Logic for Root Patching
# Returns a dictionary of patches with boolean values
# Used when supplying data to sys_patch.py
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

import plistlib
import logging
import py_sip_xnu
from pathlib import Path

from resources import (
    constants,
    device_probe,
    utilities,
    amfi_detect,
    network_handler,
    kdk_handler
)
from data import (
    model_array,
    os_data,
    sip_data,
    smbios_data,
    cpu_data
)


class DetectRootPatch:
    """
    Library for querying root volume patches applicable for booted system
    """

    def __init__(self, model: str, global_constants: constants.Constants):
        self.model: str = model

        self.constants: constants.Constants = global_constants

        self.computer = self.constants.computer

        # GPU Patch Detection
        self.nvidia_tesla   = False
        self.kepler_gpu     = False
        self.nvidia_web     = False
        self.amd_ts1        = False
        self.amd_ts2        = False
        self.iron_gpu       = False
        self.sandy_gpu      = False
        self.ivy_gpu        = False
        self.haswell_gpu    = False
        self.broadwell_gpu  = False
        self.skylake_gpu    = False
        self.legacy_gcn     = False
        self.legacy_polaris = False
        self.legacy_vega    = False

        # Misc Patch Detection
        self.brightness_legacy         = False
        self.legacy_audio              = False
        self.legacy_wifi               = False
        self.legacy_gmux               = False
        self.legacy_keyboard_backlight = False
        self.legacy_uhci_ohci          = False

        # Patch Requirements
        self.amfi_must_disable   = False
        self.amfi_shim_bins      = False
        self.supports_metal      = False
        self.needs_nv_web_checks = False
        self.requires_root_kc    = False

        # Validation Checks
        self.sip_enabled     = False
        self.sbm_enabled     = False
        self.amfi_enabled    = False
        self.fv_enabled      = False
        self.dosdude_patched = False
        self.missing_kdk     = False
        self.has_network     = False

        self.missing_whatever_green = False
        self.missing_nv_web_nvram   = False
        self.missing_nv_web_opengl  = False
        self.missing_nv_compat      = False


    def _detect_gpus(self):
        """
        Query GPUs and set flags for applicable patches
        """

        gpus = self.constants.computer.gpus
        non_metal_os = os_data.os_data.catalina
        for i, gpu in enumerate(gpus):
            if gpu.class_code and gpu.class_code != 0xFFFFFFFF:
                logging.info(f"- Found GPU ({i}): {utilities.friendly_hex(gpu.vendor_id)}:{utilities.friendly_hex(gpu.device_id)}")
                if gpu.arch in [device_probe.NVIDIA.Archs.Tesla] and self.constants.force_nv_web is False:
                    if self.constants.detected_os > non_metal_os:
                        self.nvidia_tesla = True
                        self.amfi_must_disable = True
                        if os_data.os_data.ventura in self.constants.legacy_accel_support:
                            self.amfi_shim_bins = True
                        self.legacy_keyboard_backlight = self._check_legacy_keyboard_backlight()
                        self.requires_root_kc = True
                elif gpu.arch == device_probe.NVIDIA.Archs.Kepler and self.constants.force_nv_web is False:
                    if self.constants.detected_os > os_data.os_data.big_sur:
                        # Kepler drivers were dropped with Beta 7
                        # 12.0 Beta 5: 21.0.0 - 21A5304g
                        # 12.0 Beta 6: 21.1.0 - 21A5506j
                        # 12.0 Beta 7: 21.1.0 - 21A5522h
                        if (
                            self.constants.detected_os >= os_data.os_data.ventura or
                            (
                                "21A5506j" not in self.constants.detected_os_build and
                                self.constants.detected_os == os_data.os_data.monterey and
                                self.constants.detected_os_minor > 0
                            )
                        ):
                            self.kepler_gpu = True
                            self.supports_metal = True
                            if self.constants.detected_os >= os_data.os_data.ventura:
                                self.amfi_must_disable = True
                                if (self.constants.detected_os == os_data.os_data.ventura and self.constants.detected_os_minor >= 4) or self.constants.detected_os > os_data.os_data.ventura:
                                    self.amfi_shim_bins = True
                elif gpu.arch in [
                    device_probe.NVIDIA.Archs.Fermi,
                    device_probe.NVIDIA.Archs.Kepler,
                    device_probe.NVIDIA.Archs.Maxwell,
                    device_probe.NVIDIA.Archs.Pascal,
                ]:
                    if self.constants.detected_os > os_data.os_data.mojave:
                        self.nvidia_web = True
                        self.amfi_must_disable = True
                        if os_data.os_data.ventura in self.constants.legacy_accel_support:
                            self.amfi_shim_bins = True
                        self.needs_nv_web_checks = True
                        self.requires_root_kc = True
                elif gpu.arch == device_probe.AMD.Archs.TeraScale_1:
                    if self.constants.detected_os > non_metal_os:
                        self.amd_ts1 = True
                        self.amfi_must_disable = True
                        if os_data.os_data.ventura in self.constants.legacy_accel_support:
                            self.amfi_shim_bins = True
                        self.requires_root_kc = True
                elif gpu.arch == device_probe.AMD.Archs.TeraScale_2:
                    if self.constants.detected_os > non_metal_os:
                        self.amd_ts2 = True
                        self.amfi_must_disable = True
                        if os_data.os_data.ventura in self.constants.legacy_accel_support:
                            self.amfi_shim_bins = True
                        self.requires_root_kc = True
                elif gpu.arch in [
                    device_probe.AMD.Archs.Legacy_GCN_7000,
                    device_probe.AMD.Archs.Legacy_GCN_8000,
                    device_probe.AMD.Archs.Legacy_GCN_9000,
                    device_probe.AMD.Archs.Polaris,
                ]:
                    if self.constants.detected_os > os_data.os_data.monterey:
                        if self.constants.computer.rosetta_active is True:
                            continue

                        if gpu.arch == device_probe.AMD.Archs.Polaris:
                            # Check if host supports AVX2.0
                            # If not, enable legacy GCN patch
                            # MacBookPro13,3 does include an unsupported framebuffer, thus we'll patch to ensure
                            # full compatibility (namely power states, etc)
                            # Reference: https://github.com/dortania/bugtracker/issues/292
                            # TODO: Probe framebuffer families further
                            if self.model != "MacBookPro13,3":
                                if "AVX2" in self.constants.computer.cpu.leafs:
                                    continue
                                self.legacy_polaris = True
                            else:
                                self.legacy_gcn = True
                        else:
                            self.legacy_gcn = True
                        self.supports_metal = True
                        self.requires_root_kc = True
                        self.amfi_must_disable = True
                elif gpu.arch == device_probe.AMD.Archs.Vega:
                     if self.constants.detected_os > os_data.os_data.monterey:
                        if "AVX2" in self.constants.computer.cpu.leafs:
                            continue

                        self.legacy_vega = True
                        self.supports_metal = True
                        self.requires_root_kc = True
                        self.amfi_must_disable = True
                elif gpu.arch == device_probe.Intel.Archs.Iron_Lake:
                    if self.constants.detected_os > non_metal_os:
                        self.iron_gpu = True
                        self.amfi_must_disable = True
                        if os_data.os_data.ventura in self.constants.legacy_accel_support:
                            self.amfi_shim_bins = True
                        self.legacy_keyboard_backlight = self._check_legacy_keyboard_backlight()
                        self.requires_root_kc = True
                elif gpu.arch == device_probe.Intel.Archs.Sandy_Bridge:
                    if self.constants.detected_os > non_metal_os:
                        self.sandy_gpu = True
                        self.amfi_must_disable = True
                        if os_data.os_data.ventura in self.constants.legacy_accel_support:
                            self.amfi_shim_bins = True
                        self.legacy_keyboard_backlight = self._check_legacy_keyboard_backlight()
                        self.requires_root_kc = True
                elif gpu.arch == device_probe.Intel.Archs.Ivy_Bridge:
                    if self.constants.detected_os > os_data.os_data.big_sur:
                        self.ivy_gpu = True
                        if self.constants.detected_os >= os_data.os_data.ventura:
                            self.amfi_must_disable = True
                            if (self.constants.detected_os == os_data.os_data.ventura and self.constants.detected_os_minor >= 4) or self.constants.detected_os > os_data.os_data.ventura:
                                self.amfi_shim_bins = True
                        self.supports_metal = True
                elif gpu.arch == device_probe.Intel.Archs.Haswell:
                    if self.constants.detected_os > os_data.os_data.monterey:
                        self.haswell_gpu = True
                        self.amfi_must_disable = True
                        if (self.constants.detected_os == os_data.os_data.ventura and self.constants.detected_os_minor >= 4) or self.constants.detected_os > os_data.os_data.ventura:
                            self.amfi_shim_bins = True
                        self.supports_metal = True
                elif gpu.arch == device_probe.Intel.Archs.Broadwell:
                    if self.constants.detected_os > os_data.os_data.monterey:
                        self.broadwell_gpu = True
                        self.amfi_must_disable = True
                        self.supports_metal = True
                elif gpu.arch == device_probe.Intel.Archs.Skylake:
                    if self.constants.detected_os > os_data.os_data.monterey:
                        self.skylake_gpu = True
                        self.amfi_must_disable = True
                        self.supports_metal = True
        if self.supports_metal is True:
            # Avoid patching Metal and non-Metal GPUs if both present, prioritize Metal GPU
            # Main concerns are for iMac12,x with Sandy iGPU and Kepler dGPU
            self.nvidia_tesla = False
            self.nvidia_web = False
            self.amd_ts1 = False
            self.amd_ts2 = False
            self.iron_gpu = False
            self.sandy_gpu = False
            self.legacy_keyboard_backlight = False

        if self.legacy_gcn is True:
            # We can only support one or the other due to the nature of relying
            # on portions of the native AMD stack for Polaris and Vega
            # Thus we'll prioritize legacy GCN due to being the internal card
            # ex. MacPro6,1 and MacBookPro11,5 with eGPUs
            self.legacy_polaris = False
            self.legacy_vega = False

        if self.constants.detected_os <= os_data.os_data.monterey:
            # Always assume Root KC requirement on Monterey and older
            self.requires_root_kc = True
        else:
            if self.requires_root_kc is True:
                self.missing_kdk = not self._check_kdk()

        self._check_networking_support()


    def _check_networking_support(self):
        """
        Query for network requirement, ex. KDK downloading

        On macOS Ventura, networking support is required to download KDKs.
        However for machines such as BCM94322, BCM94328 and Atheros chipsets,
        users may only have wifi as their only supported network interface.
        Thus we'll allow for KDK-less installs for these machines on first run.
        On subsequent runs, we'll require networking to be enabled.
        """

        if self.constants.detected_os < os_data.os_data.ventura:
            return
        if self.legacy_wifi is False:
            return
        if self.requires_root_kc is False:
            return
        if self.missing_kdk is False:
            return
        if self.has_network is True:
            return

        # Verify whether OCLP already installed network patches to the root volume
        # If so, require networking to be enabled (user just needs to connect to wifi)
        oclp_patch_path = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"
        if Path(oclp_patch_path).exists():
            oclp_plist = plistlib.load(open(oclp_patch_path, "rb"))
            if "Legacy Wireless" in oclp_plist:
                return

        # Due to the reliance of KDKs for most older patches, we'll allow KDK-less
        # installs for Legacy Wifi patches and remove others
        self.missing_kdk =      False
        self.requires_root_kc = False

        # Reset patches needing KDK
        self.nvidia_tesla              = False
        self.nvidia_web                = False
        self.amd_ts1                   = False
        self.amd_ts2                   = False
        self.iron_gpu                  = False
        self.sandy_gpu                 = False
        self.legacy_gcn                = False
        self.legacy_polaris            = False
        self.legacy_vega               = False
        self.brightness_legacy         = False
        self.legacy_audio              = False
        self.legacy_gmux               = False
        self.legacy_keyboard_backlight = False


    def _check_dgpu_status(self):
        """
        Query whether system has an active dGPU
        """

        dgpu = self.constants.computer.dgpu
        if dgpu:
            if dgpu.class_code and dgpu.class_code == 0xFFFFFFFF:
                # If dGPU is disabled via class-codes, assume demuxed
                return False
            return True
        return False


    def _detect_demux(self):
        """
        Query whether system has been demuxed (ex. MacBookPro8,2, disabled dGPU)
        """

        # If GFX0 is missing, assume machine was demuxed
        # -wegnoegpu would also trigger this, so ensure arg is not present
        if not "-wegnoegpu" in (utilities.get_nvram("boot-args", decode=True) or ""):
            igpu = self.constants.computer.igpu
            dgpu = self._check_dgpu_status()
            if igpu and not dgpu:
                return True
        return False


    def _check_legacy_keyboard_backlight(self):
        """
        Query whether system has a legacy keyboard backlight

        Returns:
            bool: True if legacy keyboard backlight, False otherwise
        """

        # iMac12,x+ have an 'ACPI0008' device, but it's not a keyboard backlight
        # Best to assume laptops will have a keyboard backlight
        if self.model.startswith("MacBook"):
            return self.constants.computer.ambient_light_sensor
        return False


    def _check_nv_web_nvram(self):
        """
        Query for Nvidia Web Driver property: nvda_drv_vrl or nvda_drv

        Returns:
            bool: True if property is present, False otherwise
        """

        nv_on = utilities.get_nvram("boot-args", decode=True)
        if nv_on:
            if "nvda_drv_vrl=" in nv_on:
                return True
        nv_on = utilities.get_nvram("nvda_drv")
        if nv_on:
            return True
        return False


    def _check_nv_web_opengl(self):
        """
        Query for Nvidia Web Driver property: ngfxgl

        Verify Web Drivers will run in OpenGL mode

        Returns:
            bool: True if property is present, False otherwise
        """

        nv_on = utilities.get_nvram("boot-args", decode=True)
        if nv_on:
            if "ngfxgl=" in nv_on:
                return True
        for gpu in self.constants.computer.gpus:
            if isinstance(gpu, device_probe.NVIDIA):
                if gpu.disable_metal is True:
                    return True
        return False


    def _check_nv_compat(self):
        """
        Query for Nvidia Web Driver property: ngfxcompat

        Verify Web Drivers will skip NVDAStartupWeb compatibility check

        Returns:
            bool: True if property is present, False otherwise
        """

        nv_on = utilities.get_nvram("boot-args", decode=True)
        if nv_on:
            if "ngfxcompat=" in nv_on:
                return True
        for gpu in self.constants.computer.gpus:
            if isinstance(gpu, device_probe.NVIDIA):
                if gpu.force_compatible is True:
                    return True
        return False


    def _check_whatevergreen(self):
        """
        Query whether WhateverGreen.kext is loaded

        Returns:
            bool: True if loaded, False otherwise
        """

        return utilities.check_kext_loaded("WhateverGreen", self.constants.detected_os)


    def _check_kdk(self):
        """
        Query whether Kernel Debug Kit is installed

        Returns:
            bool: True if installed, False otherwise
        """

        return kdk_handler.KernelDebugKitObject(self.constants, self.constants.detected_os_build, self.constants.detected_os_version, passive=True).kdk_already_installed


    def _check_sip(self):
        """
        Query System Integrity checks required for patching

        Returns:
            tuple: (list, str, str) of SIP values, SIP hex, SIP error message
        """

        if self.constants.detected_os > os_data.os_data.catalina:
            if self.nvidia_web is True:
                sip = sip_data.system_integrity_protection.root_patch_sip_big_sur_3rd_part_kexts
                sip_hex = "0xA03"
                sip_value = (
                    f"For Hackintoshes, please set csr-active-config to '030A0000' ({sip_hex})\nFor non-OpenCore Macs, please run 'csrutil disable' and \n'csrutil authenticated-root disable' in RecoveryOS"
                )
            elif self.constants.detected_os >= os_data.os_data.ventura:
                sip = sip_data.system_integrity_protection.root_patch_sip_ventura
                sip_hex = "0x803"
                sip_value = (
                    f"For Hackintoshes, please set csr-active-config to '03080000' ({sip_hex})\nFor non-OpenCore Macs, please run 'csrutil disable' and \n'csrutil authenticated-root disable' in RecoveryOS"
                )
            else:
                sip = sip_data.system_integrity_protection.root_patch_sip_big_sur
                sip_hex = "0x802"
                sip_value = (
                    f"For Hackintoshes, please set csr-active-config to '02080000' ({sip_hex})\nFor non-OpenCore Macs, please run 'csrutil disable' and \n'csrutil authenticated-root disable' in RecoveryOS"
                )
        else:
            sip = sip_data.system_integrity_protection.root_patch_sip_mojave
            sip_hex = "0x603"
            sip_value = f"For Hackintoshes, please set csr-active-config to '03060000' ({sip_hex})\nFor non-OpenCore Macs, please run 'csrutil disable' in RecoveryOS"
        return (sip, sip_value, sip_hex)


    def _check_uhci_ohci(self):
        """
        Query whether host has UHCI/OHCI controllers, and requires USB 1.1 patches

        Returns:
            bool: True if UHCI/OHCI patches required, False otherwise
        """

        if self.constants.detected_os < os_data.os_data.ventura:
            return False

        for controller in self.constants.computer.usb_controllers:
            if (isinstance(controller, device_probe.XHCIController)):
                # Currently USB 1.1 patches are incompatible with USB 3.0 controllers
                # TODO: Downgrade remaining USB stack to ensure full support
                return False

        # If we're on a hackintosh, check for UHCI/OHCI controllers
        if self.constants.host_is_hackintosh is True:
            for controller in self.constants.computer.usb_controllers:
                if (
                    isinstance(controller, device_probe.UHCIController) or
                    isinstance(controller, device_probe.OHCIController)
                ):
                    return True
            return False

        if self.model not in smbios_data.smbios_dictionary:
            return False

        # If we're on a Mac, check for Penryn or older
        # This is due to Apple implementing an internal USB hub on post-Penryn (excluding MacPro4,1 and MacPro5,1)
        # Ref: https://techcommunity.microsoft.com/t5/microsoft-usb-blog/reasons-to-avoid-companion-controllers/ba-p/270710
        if (
            smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.penryn.value or \
            self.model in ["MacPro4,1", "MacPro5,1"]
        ):
            return True

        return False


    # Entry point for patch set detection
    def detect_patch_set(self):
        """
        Query patch sets required for host

        Returns:
            dict: Dictionary of patch sets
        """

        self.has_network = network_handler.NetworkUtilities().verify_network_connection()

        if self._check_uhci_ohci() is True:
            self.legacy_uhci_ohci = True
            self.requires_root_kc = True

        if self.model in model_array.LegacyBrightness:
            if self.constants.detected_os > os_data.os_data.catalina:
                self.brightness_legacy = True

        if self.model in ["iMac7,1", "iMac8,1"] or (self.model in model_array.LegacyAudio and utilities.check_kext_loaded("AppleALC", self.constants.detected_os) is False):
            # Special hack for systems with botched GOPs
            # TL;DR: No Boot Screen breaks Lilu, therefore breaking audio
            if self.constants.detected_os > os_data.os_data.catalina:
                self.legacy_audio = True

        if (
            isinstance(self.constants.computer.wifi, device_probe.Broadcom)
            and self.constants.computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
        ) or (isinstance(self.constants.computer.wifi, device_probe.Atheros) and self.constants.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40):
            if self.constants.detected_os > os_data.os_data.big_sur:
                self.legacy_wifi = True
                if self.constants.detected_os >= os_data.os_data.ventura:
                    # Due to extracted frameworks for IO80211.framework and co, check library validation
                    self.amfi_must_disable = True

        # if self.model in ["MacBookPro5,1", "MacBookPro5,2", "MacBookPro5,3", "MacBookPro8,2", "MacBookPro8,3"]:
        if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            # Sierra uses a legacy GMUX control method needed for dGPU switching on MacBookPro5,x
            # Same method is also used for demuxed machines
            # Note that MacBookPro5,x machines are extremely unstable with this patch set, so disabled until investigated further
            # Ref: https://github.com/dortania/OpenCore-Legacy-Patcher/files/7360909/KP-b10-030.txt
            if self.constants.detected_os > os_data.os_data.high_sierra:
                if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
                    # Ref: https://doslabelectronics.com/Demux.html
                    if self._detect_demux() is True:
                        self.legacy_gmux = True
                else:
                    self.legacy_gmux = True

        self._detect_gpus()

        self.root_patch_dict = {
            "Graphics: Nvidia Tesla":                      self.nvidia_tesla,
            "Graphics: Nvidia Kepler":                     self.kepler_gpu,
            "Graphics: Nvidia Web Drivers":                self.nvidia_web,
            "Graphics: AMD TeraScale 1":                   self.amd_ts1,
            "Graphics: AMD TeraScale 2":                   self.amd_ts2,
            "Graphics: AMD Legacy GCN":                    self.legacy_gcn,
            "Graphics: AMD Legacy Polaris":                self.legacy_polaris,
            "Graphics: AMD Legacy Vega":                   self.legacy_vega,
            "Graphics: Intel Ironlake":                    self.iron_gpu,
            "Graphics: Intel Sandy Bridge":                self.sandy_gpu,
            "Graphics: Intel Ivy Bridge":                  self.ivy_gpu,
            "Graphics: Intel Haswell":                     self.haswell_gpu,
            "Graphics: Intel Broadwell":                   self.broadwell_gpu,
            "Graphics: Intel Skylake":                     self.skylake_gpu,
            "Brightness: Legacy Backlight Control":        self.brightness_legacy,
            "Audio: Legacy Realtek":                       self.legacy_audio,
            "Networking: Legacy Wireless":                 self.legacy_wifi,
            "Miscellaneous: Legacy GMUX":                  self.legacy_gmux,
            "Miscellaneous: Legacy Keyboard Backlight":    self.legacy_keyboard_backlight,
            "Miscellaneous: Legacy USB 1.1":               self.legacy_uhci_ohci,
            "Settings: Requires AMFI exemption":           self.amfi_must_disable,
            "Settings: Supports Auxiliary Cache":          not self.requires_root_kc,
            "Settings: Kernel Debug Kit missing":          self.missing_kdk if self.constants.detected_os >= os_data.os_data.ventura.value else False,
            "Validation: Patching Possible":               self.verify_patch_allowed(),
            "Validation: Unpatching Possible":             self._verify_unpatch_allowed(),
            f"Validation: SIP is enabled (Required: {self._check_sip()[2]} or higher)":  self.sip_enabled,
            f"Validation: Currently Booted SIP: ({hex(py_sip_xnu.SipXnu().get_sip_status().value)})":         self.sip_enabled,
            "Validation: SecureBootModel is enabled":      self.sbm_enabled,
            f"Validation: {'AMFI' if self.constants.host_is_hackintosh is True or self._get_amfi_level_needed() > 2 else 'Library Validation'} is enabled":                 self.amfi_enabled if self.amfi_must_disable is True else False,
            "Validation: FileVault is enabled":            self.fv_enabled,
            "Validation: System is dosdude1 patched":      self.dosdude_patched,
            "Validation: WhateverGreen.kext missing":      self.missing_whatever_green if self.nvidia_web is True else False,
            "Validation: Force OpenGL property missing":   self.missing_nv_web_opengl  if self.nvidia_web is True else False,
            "Validation: Force compat property missing":   self.missing_nv_compat      if self.nvidia_web is True else False,
            "Validation: nvda_drv(_vrl) variable missing": self.missing_nv_web_nvram   if self.nvidia_web is True else False,
            "Validation: Network Connection Required":     (not self.has_network) if (self.requires_root_kc and self.missing_kdk and self.constants.detected_os >= os_data.os_data.ventura.value) else False,
        }

        return self.root_patch_dict


    def _get_amfi_level_needed(self):
        """
        Query the AMFI level needed for the patcher to work

        Returns:
            int: AMFI level needed
        """

        if self.amfi_must_disable is False:
            return amfi_detect.AmfiConfigDetectLevel.NO_CHECK

        if self.constants.detected_os < os_data.os_data.big_sur:
            return amfi_detect.AmfiConfigDetectLevel.NO_CHECK

        if self.constants.detected_os >= os_data.os_data.ventura:
            if self.amfi_shim_bins is True:
                # Currently we require AMFI outright disabled
                # in Ventura to work with shim'd binaries
                return amfi_detect.AmfiConfigDetectLevel.ALLOW_ALL

        return amfi_detect.AmfiConfigDetectLevel.LIBRARY_VALIDATION


    def verify_patch_allowed(self, print_errors: bool = False):
        """
        Validate that the patcher can be run

        Parameters:
            print_errors (bool): Print errors to console

        Returns:
            bool: True if patching is allowed, False otherwise
        """

        sip_dict = self._check_sip()
        sip = sip_dict[0]
        sip_value = sip_dict[1]

        self.sip_enabled, self.sbm_enabled, self.fv_enabled, self.dosdude_patched = utilities.patching_status(sip, self.constants.detected_os)
        self.amfi_enabled = not amfi_detect.AmfiConfigurationDetection().check_config(self._get_amfi_level_needed())

        if self.nvidia_web is True:
            self.missing_nv_web_nvram   = not self._check_nv_web_nvram()
            self.missing_nv_web_opengl  = not self._check_nv_web_opengl()
            self.missing_nv_compat      = not self._check_nv_compat()
            self.missing_whatever_green = not self._check_whatevergreen()

        if print_errors is True:
            if self.sip_enabled is True:
                logging.info("\nCannot patch! Please disable System Integrity Protection (SIP).")
                logging.info("Disable SIP in Patcher Settings and Rebuild OpenCore\n")
                logging.info("Ensure the following bits are set for csr-active-config:")
                logging.info("\n".join(sip))
                logging.info(sip_value)

            if self.sbm_enabled is True:
                logging.info("\nCannot patch! Please disable Apple Secure Boot.")
                logging.info("Disable SecureBootModel in Patcher Settings and Rebuild OpenCore")
                logging.info("For Hackintoshes, set SecureBootModel to Disabled")

            if self.fv_enabled is True:
                logging.info("\nCannot patch! Please disable FileVault.")
                logging.info("For OCLP Macs, please rebuild your config with 0.2.5 or newer")
                logging.info("For others, Go to System Preferences -> Security and disable FileVault")

            if self.amfi_enabled is True and self.amfi_must_disable is True:
                logging.info("\nCannot patch! Please disable AMFI.")
                logging.info("For Hackintoshes, please add amfi_get_out_of_my_way=1 to boot-args")

            if self.dosdude_patched is True:
                logging.info("\nCannot patch! Detected machine has already been patched by another patcher")
                logging.info("Please ensure your install is either clean or patched with OpenCore Legacy Patcher")

            if self.nvidia_web is True:
                if self.missing_nv_web_opengl is True:
                    logging.info("\nCannot patch! Force OpenGL property missing")
                    logging.info("Please ensure ngfxgl=1 is set in boot-args")

                if self.missing_nv_compat is True:
                    logging.info("\nCannot patch! Force Nvidia compatibility property missing")
                    logging.info("Please ensure ngfxcompat=1 is set in boot-args")

                if self.missing_nv_web_nvram is True:
                    logging.info("\nCannot patch! nvda_drv(_vrl) variable missing")
                    logging.info("Please ensure nvda_drv_vrl=1 is set in boot-args")

                if self.missing_whatever_green is True:
                    logging.info("\nCannot patch! WhateverGreen.kext missing")
                    logging.info("Please ensure WhateverGreen.kext is installed")

            if (not self.has_network) if (self.requires_root_kc and self.missing_kdk and self.constants.detected_os >= os_data.os_data.ventura.value) else False:
                logging.info("\nCannot patch! Network Connection Required")
                logging.info("Please ensure you have an active internet connection")

        if any(
            [
                # General patch checks
                self.sip_enabled, self.sbm_enabled, self.fv_enabled, self.dosdude_patched,

                # non-Metal specific
                self.amfi_enabled if self.amfi_must_disable is True else False,

                # Web Driver specific
                self.missing_nv_web_nvram   if self.nvidia_web is True  else False,
                self.missing_nv_web_opengl  if self.nvidia_web is True  else False,
                self.missing_nv_compat      if self.nvidia_web is True  else False,
                self.missing_whatever_green if self.nvidia_web is True  else False,

                # KDK specific
                (not self.has_network) if (self.requires_root_kc and self.missing_kdk and self.constants.detected_os >= os_data.os_data.ventura.value) else False
            ]
        ):
            return False

        return True


    def _verify_unpatch_allowed(self):
        """
        Validate that the unpatcher can be run

        Preconditions:
            Must be called after verify_patch_allowed()

        Returns:
            bool: True if unpatching is allowed, False otherwise
        """

        return not self.sip_enabled