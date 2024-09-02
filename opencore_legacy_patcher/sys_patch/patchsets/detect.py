"""
detect.py: Detects patches for a given system
"""

import logging
import plistlib
import subprocess
import py_sip_xnu
import packaging.version

from enum      import StrEnum
from pathlib   import Path
from functools import cache

from .hardware.base import BaseHardware

from .hardware.graphics import (
    intel_iron_lake,
    intel_sandy_bridge,
    intel_ivy_bridge,
    intel_haswell,
    intel_broadwell,
    intel_skylake,

    nvidia_tesla,
    nvidia_kepler,
    nvidia_webdriver,

    amd_terascale_1,
    amd_terascale_2,
    amd_legacy_gcn,
    amd_polaris,
    amd_vega,
)
from .hardware.networking import (
    legacy_wireless,
    modern_wireless,
)
from .hardware.misc import (
    display_backlight,
    gmux,
    keyboard_backlight,
    legacy_audio,
    pcie_webcam,
    t1_security,
    usb11,
)

from ... import constants

from ...datasets import sip_data
from ...datasets.os_data import os_data
from ...support import (
    network_handler,
    utilities,
    kdk_handler,
    metallib_handler
)
from ...detections import (
    amfi_detect,
    device_probe
)


class HardwarePatchsetSettings(StrEnum):
    """
    Enum for patch settings
    """
    KERNEL_DEBUG_KIT_REQUIRED     = "Settings: Kernel Debug Kit required"
    KERNEL_DEBUG_KIT_MISSING      = "Settings: Kernel Debug Kit missing"
    METALLIB_SUPPORT_PKG_REQUIRED = "Settings: MetallibSupportPkg.pkg required"
    METALLIB_SUPPORT_PKG_MISSING  = "Settings: MetallibSupportPkg.pkg missing"


class HardwarePatchsetValidation(StrEnum):
    """
    Enum for validation settings
    """
    UNSUPPORTED_HOST_OS           = "Validation: Unsupported Host OS"
    MISSING_NETWORK_CONNECTION    = "Validation: Missing Network Connection"
    FILEVAULT_ENABLED             = "Validation: FileVault is enabled"
    SIP_ENABLED                   = "Validation: System Integrity Protection is enabled"
    SECURE_BOOT_MODEL_ENABLED     = "Validation: SecureBootModel is enabled"
    AMFI_ENABLED                  = "Validation: AMFI is enabled"
    WHATEVERGREEN_MISSING         = "Validation: WhateverGreen.kext missing"
    FORCE_OPENGL_MISSING          = "Validation: Force OpenGL property missing"
    FORCE_COMPAT_MISSING          = "Validation: Force compat property missing"
    NVDA_DRV_MISSING              = "Validation: nvda_drv(_vrl) variable missing"
    HELL_SPAWN_GPU_PRESENT        = "Validation: Graphics Patches unavailable for macOS Sequoia"
    PATCHING_NOT_POSSIBLE         = "Validation: Patching not possible"
    UNPATCHING_NOT_POSSIBLE       = "Validation: Unpatching not possible"


class HardwarePatchsetDetection:

    def __init__(self, constants: constants.Constants,
                 xnu_major: int = None, xnu_minor:  int = None,
                 os_build:  str = None, os_version: str = None,
                 validation: bool = False # Whether to run validation checks
                 ) -> None:
        self._constants = constants

        self._xnu_major  = xnu_major  or self._constants.detected_os
        self._xnu_minor  = xnu_minor  or self._constants.detected_os_minor
        self._os_build   = os_build   or self._constants.detected_os_build
        self._os_version = os_version or self._constants.detected_os_version
        self._validation = validation

        self._hardware_variants = [
            intel_iron_lake.IntelIronLake,
            intel_sandy_bridge.IntelSandyBridge,
            intel_ivy_bridge.IntelIvyBridge,
            intel_haswell.IntelHaswell,
            intel_broadwell.IntelBroadwell,
            intel_skylake.IntelSkylake,

            nvidia_tesla.NvidiaTesla,
            nvidia_kepler.NvidiaKepler,
            nvidia_webdriver.NvidiaWebDriver,

            amd_terascale_1.AMDTeraScale1,
            amd_terascale_2.AMDTeraScale2,
            amd_legacy_gcn.AMDLegacyGCN,
            amd_polaris.AMDPolaris,
            amd_vega.AMDVega,

            legacy_wireless.LegacyWireless,
            modern_wireless.ModernWireless,

            display_backlight.DisplayBacklight,
            gmux.GraphicsMultiplexer,
            keyboard_backlight.KeyboardBacklight,
            legacy_audio.LegacyAudio,
            pcie_webcam.PCIeFaceTimeCamera,
            t1_security.T1SecurityChip,
            usb11.USB11Controller,
        ]

        self.device_properties = None
        self.patches           = None

        self.can_patch         = False
        self.can_unpatch       = False

        self._detect()


    def _validation_check_unsupported_host_os(self) -> bool:
        """
        Determine if host OS is unsupported
        """
        _min_os = os_data.big_sur.value
        _max_os = os_data.sequoia.value
        if self._xnu_major < _min_os or self._xnu_major > _max_os:
            return True
        return False


    @cache
    def _validation_check_missing_network_connection(self) -> bool:
        """
        Determine if network connection is present
        """
        return network_handler.NetworkUtilities().verify_network_connection() is False


    @cache
    def _validation_check_filevault_is_enabled(self) -> bool:
        """
        Determine if FileVault is enabled
        """
        # macOS 11.0 introduced a FileVault check for root patching
        if self._xnu_major < os_data.big_sur.value:
            return False

        # OpenCore Legacy Patcher exposes whether it patched APFS.kext to allow for FileVault
        nvram = utilities.get_nvram("OCLP-Settings", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if nvram:
            if "-allow_fv" in nvram:
                return False

        return "FileVault is Off" not in subprocess.run(["/usr/bin/fdesetup", "status"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()


    def _validation_check_system_integrity_protection_enabled(self, configs: list[str]) -> bool:
        """
        Determine if System Integrity Protection is enabled
        """
        return utilities.csr_decode(configs)


    def _validation_check_secure_boot_model_enabled(self) -> bool:
        """
        Determine if SecureBootModel is enabled
        """
        return utilities.check_secure_boot_level()


    def _validation_check_amfi_enabled(self, level: amfi_detect.AmfiConfigDetectLevel) -> bool:
        """
        Determine if AMFI is enabled
        """
        return not amfi_detect.AmfiConfigurationDetection().check_config(self._override_amfi_level(level))


    def _validation_check_whatevergreen_missing(self) -> bool:
        """
        Determine if WhateverGreen.kext is missing
        """
        return utilities.check_kext_loaded("as.vit9696.WhateverGreen") is False


    @cache
    def _validation_check_force_opengl_missing(self) -> bool:
        """
        Determine if Force OpenGL property is missing
        """
        nv_on = utilities.get_nvram("boot-args", decode=True)
        if nv_on:
            if "ngfxgl=" in nv_on:
                return True
        for gpu in self._constants.computer.gpus:
            if isinstance(gpu, device_probe.NVIDIA):
                if gpu.disable_metal is True:
                    return True
        return False


    def _validation_check_force_compat_missing(self) -> bool:
        """
        Determine if Force compat property is missing
        """
        nv_on = utilities.get_nvram("boot-args", decode=True)
        if nv_on:
            if "ngfxcompat=" in nv_on:
                return True
        for gpu in self._constants.computer.gpus:
            if isinstance(gpu, device_probe.NVIDIA):
                if gpu.force_compatible is True:
                    return True
        return False


    def _validation_check_nvda_drv_missing(self) -> bool:
        """
        Determine if nvda_drv(_vrl) variable is missing
        """
        nv_on = utilities.get_nvram("boot-args", decode=True)
        if nv_on:
            if "nvda_drv_vrl=" in nv_on:
                return True
        nv_on = utilities.get_nvram("nvda_drv")
        if nv_on:
            return True
        return False


    @cache
    def _override_amfi_level(self, level: amfi_detect.AmfiConfigDetectLevel) -> amfi_detect.AmfiConfigDetectLevel:
        """
        Override level required based on whether AMFIPass is loaded
        """
        amfipass_version = utilities.check_kext_loaded("com.dhinakg.AMFIPass")
        if amfipass_version:
            if packaging.version.parse(amfipass_version) >= packaging.version.parse(self._constants.amfipass_compatibility_version):
                # If AMFIPass is loaded, our binaries will work
                return amfi_detect.AmfiConfigDetectLevel.NO_CHECK
        return level


    def _dortania_internal_check(self) -> None:
        """
        Determine whether to unlock Dortania Developer mode
        """
        return Path("~/.dortania_developer").expanduser().exists()


    def _already_has_networking_patches(self) -> bool:
        """
        Check if network patches are already applied
        """
        oclp_patch_path = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"
        if not Path(oclp_patch_path).exists():
            return False
        try:
            oclp_plist = plistlib.load(open(oclp_patch_path, "rb"))
        except Exception as e:
            return False
        if "Legacy Wireless" in oclp_plist or "Modern Wireless" in oclp_plist:
            return True
        return False


    def _is_cached_kernel_debug_kit_present(self) -> bool:
        """
        Check if Kernel Debug Kit is present
        """
        return kdk_handler.KernelDebugKitObject(self._constants, self._os_build, self._os_version).kdk_already_installed


    def _is_cached_metallib_support_pkg_present(self) -> bool:
        """
        Check if MetallibSupportPkg is present
        """
        return metallib_handler.MetalLibraryObject(self._constants, self._os_build, self._os_version).metallib_already_installed


    def _can_patch(self, requirements: dict, ignore_keys: list[str] = []) -> bool:
        """
        Check if patching is possible
        """
        for key, value in requirements.items():
            if key in ignore_keys:
                continue
            if not key.startswith("Validation:"):
                continue
            if value is True:
                return False
        return True


    def _convert_required_sip_config_to_int(self, configs: list[str]) -> int:
        """
        Convert required SIP configurations to integer
        """
        value = 0
        for config in configs:
            if config in sip_data.system_integrity_protection.csr_values_extended:
                value += sip_data.system_integrity_protection.csr_values_extended[config]["value"]

        return value


    def _detect(self) -> None:
        """
        Detect patches for a given system
        """

        device_properties = {}
        patches = {}

        requires_metallib_support_pkg = False
        missing_metallib_support_pkg  = False
        requires_kernel_debug_kit     = False
        missing_kernel_debug_kit      = False
        has_nvidia_web_drivers        = False
        has_3802_gpu                  = False
        highest_amfi_level            = amfi_detect.AmfiConfigDetectLevel.NO_CHECK
        required_sip_configs          = []

        for hardware in self._hardware_variants:
            item: BaseHardware = hardware(
                xnu_major        = self._xnu_major,
                xnu_minor        = self._xnu_minor,
                os_build         = self._os_build,
                global_constants = self._constants
            )
            # During validation, don't skip missing items
            # This is to ensure we can validate all files
            if self._validation is False:
                if item.present() is False: # Skip if not present
                    continue
            if item.native_os() is True:    # Skip if native OS
                continue

            device_properties[item.name()] = True

            if item.name() == "Graphics: Nvidia Web Drivers":
                has_nvidia_web_drivers = True
            if item.name() in ["Graphics: Nvidia Kepler", "Graphics: Intel Ivy Bridge", "Graphics: Intel Haswell"]:
                has_3802_gpu = True

            for config in item.required_system_integrity_protection_configurations():
                if config not in required_sip_configs:
                    required_sip_configs.append(config)

            if item.requires_metallib_support_pkg() is True:
                requires_metallib_support_pkg = True
            if item.requires_kernel_debug_kit() is True:
                requires_kernel_debug_kit = True
            if item.required_amfi_level() > highest_amfi_level:
                highest_amfi_level = item.required_amfi_level()

            patches.update(item.patches())


        if requires_metallib_support_pkg is True:
            missing_metallib_support_pkg = not self._is_cached_metallib_support_pkg_present()
        if requires_kernel_debug_kit is True:
            missing_kernel_debug_kit = not self._is_cached_kernel_debug_kit_present()


        requirements = {
            HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED:     requires_kernel_debug_kit,
            HardwarePatchsetSettings.KERNEL_DEBUG_KIT_MISSING:      missing_kernel_debug_kit,
            HardwarePatchsetSettings.METALLIB_SUPPORT_PKG_REQUIRED: requires_metallib_support_pkg,
            HardwarePatchsetSettings.METALLIB_SUPPORT_PKG_MISSING:  missing_metallib_support_pkg,

            HardwarePatchsetValidation.UNSUPPORTED_HOST_OS:         self._validation_check_unsupported_host_os(),
            HardwarePatchsetValidation.MISSING_NETWORK_CONNECTION:  self._validation_check_missing_network_connection() if any([missing_metallib_support_pkg, missing_kernel_debug_kit]) else False,
            HardwarePatchsetValidation.FILEVAULT_ENABLED:           self._validation_check_filevault_is_enabled(),
            HardwarePatchsetValidation.SIP_ENABLED:                 self._validation_check_system_integrity_protection_enabled(required_sip_configs),
            HardwarePatchsetValidation.SECURE_BOOT_MODEL_ENABLED:   self._validation_check_secure_boot_model_enabled(),
            HardwarePatchsetValidation.AMFI_ENABLED:                self._validation_check_amfi_enabled(highest_amfi_level),
            HardwarePatchsetValidation.WHATEVERGREEN_MISSING:       self._validation_check_whatevergreen_missing() if has_nvidia_web_drivers is True else False,
            HardwarePatchsetValidation.FORCE_OPENGL_MISSING:        self._validation_check_force_opengl_missing()  if has_nvidia_web_drivers is True else False,
            HardwarePatchsetValidation.FORCE_COMPAT_MISSING:        self._validation_check_force_compat_missing()  if has_nvidia_web_drivers is True else False,
            HardwarePatchsetValidation.NVDA_DRV_MISSING:            self._validation_check_nvda_drv_missing()      if has_nvidia_web_drivers is True else False,
            HardwarePatchsetValidation.HELL_SPAWN_GPU_PRESENT:      has_3802_gpu and not self._dortania_internal_check(),
        }

        _cant_patch   = False
        _cant_unpatch = requirements[HardwarePatchsetValidation.SIP_ENABLED]

        if requirements[HardwarePatchsetValidation.SIP_ENABLED] is True:
            current_sip_status  = hex(py_sip_xnu.SipXnu().get_sip_status().value)
            expected_sip_status = hex(self._convert_required_sip_config_to_int(required_sip_configs))
            sip_string = f"Validation: Booted SIP: {current_sip_status} vs expected: {expected_sip_status}"
            index = list(requirements.keys()).index(HardwarePatchsetValidation.SIP_ENABLED)
            requirements = dict(list(requirements.items())[:index+1] + [(sip_string, True)] + list(requirements.items())[index+1:])

        # If MISSING_NETWORK_CONNECTION is enabled, see whether 'Networking: Legacy Wireless' or 'Networking: Modern Wireless' is present
        # If so, remove other patches and set PATCHING_NOT_POSSIBLE to True
        if requirements[HardwarePatchsetValidation.MISSING_NETWORK_CONNECTION] is True:
            if self._can_patch(requirements, ignore_keys=[HardwarePatchsetValidation.MISSING_NETWORK_CONNECTION]) is True:
                logging.info("Network connection missing, checking whether network patches are applicable")
                if self._already_has_networking_patches() is True:
                    logging.info("Network patches are already applied, requiring network connection")
                else:
                    if "Networking: Legacy Wireless" in device_properties or "Networking: Modern Wireless" in device_properties:
                        logging.info("Network patches are applicable, removing other patches")
                        for key in list(device_properties.keys()):
                            if key.startswith("Networking:"):
                                continue
                            device_properties.pop(key, None)
                        requirements[HardwarePatchsetValidation.MISSING_NETWORK_CONNECTION]  = False
                        requirements[HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED]     = False
                        requirements[HardwarePatchsetSettings.KERNEL_DEBUG_KIT_MISSING]      = False
                        requirements[HardwarePatchsetSettings.METALLIB_SUPPORT_PKG_REQUIRED] = False
                        requirements[HardwarePatchsetSettings.METALLIB_SUPPORT_PKG_MISSING]  = False

        _cant_patch = not self._can_patch(requirements)

        requirements[HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE]   = _cant_patch
        requirements[HardwarePatchsetValidation.UNPATCHING_NOT_POSSIBLE] = _cant_unpatch

        self.can_patch   = not _cant_patch
        self.can_unpatch = not _cant_unpatch

        device_properties.update(requirements)

        self.device_properties = device_properties
        self.patches           = patches


    def detailed_errors(self) -> None:
        """
        Print out detailed errors
        """
        logging.error("- Breakdown:")
        for key, value in self.device_properties.items():
            if not key.startswith("Validation:"):
                continue
            if key in ["Validation: Patching not possible", "Validation: Unpatching not possible"]:
                continue
            if value is False:
                continue
            logging.error(f"  - {key.replace('Validation: ', '')}")
