"""
nvidia_webdriver.py: Nvidia Web Driver detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.non_metal             import NonMetal
from ...shared_patches.monterey_webkit       import MontereyWebKit
from ...shared_patches.non_metal_ioaccel     import NonMetalIOAccelerator
from ...shared_patches.non_metal_coredisplay import NonMetalCoreDisplay
from ...shared_patches.non_metal_enforcement import NonMetalEnforcement

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data  import os_data
from .....datasets.sip_data import system_integrity_protection


class NvidiaWebDriver(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Nvidia Web Drivers"


    def present(self) -> bool:
        """
        Targeting Nvidia Fermi, Maxwell, Pascal GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.NVIDIA.Archs.Fermi,
                device_probe.NVIDIA.Archs.Maxwell,
                device_probe.NVIDIA.Archs.Pascal,
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major < os_data.mojave.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        Type of hardware variant subclass
        """
        return HardwareVariantGraphicsSubclass.NON_METAL_GRAPHICS


    def requires_kernel_debug_kit(self) -> bool:
        """
        Apple no longer provides standalone kexts in the base OS
        """
        return self._xnu_major >= os_data.ventura.value


    def required_system_integrity_protection_configurations(self) -> list[str]:
        """
        List of required SIP configurations for the patch set
        """
        return system_integrity_protection.root_patch_sip_big_sur_3rd_part_kexts


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Nvidia Web Drivers": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "GeForceAIRPluginWeb.bundle":     "WebDriver-387.10.10.10.40.140",
                        "GeForceGLDriverWeb.bundle":      "WebDriver-387.10.10.10.40.140",
                        "GeForceMTLDriverWeb.bundle":     "WebDriver-387.10.10.10.40.140",
                        "GeForceVADriverWeb.bundle":      "WebDriver-387.10.10.10.40.140",

                        # Tesla-only files
                        "GeForceTeslaGAWeb.bundle":       "WebDriver-387.10.10.10.40.140",
                        "GeForceTeslaGLDriverWeb.bundle": "WebDriver-387.10.10.10.40.140",
                        "GeForceTeslaVADriverWeb.bundle": "WebDriver-387.10.10.10.40.140",
                    },
                },
                PatchType.OVERWRITE_DATA_VOLUME: {
                    "/Library/Extensions": {
                        "GeForceWeb.kext":                "WebDriver-387.10.10.10.40.140",
                        "NVDAGF100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAGK100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAGM100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAGP100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAResmanWeb.kext":             "WebDriver-387.10.10.10.40.140",
                        "NVDAStartupWeb.kext":            "WebDriver-387.10.10.10.40.140",

                        # Tesla-only files
                        "GeForceTeslaWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDANV50HalTeslaWeb.kext":       "WebDriver-387.10.10.10.40.140",
                        "NVDAResmanTeslaWeb.kext":        "WebDriver-387.10.10.10.40.140",
                    },

                    # Disabled due to issues with Pref pane stripping 'nvda_drv' NVRAM
                    # variables
                    # "/Library/PreferencePanes": {
                    #     "NVIDIA Driver Manager.prefPane": "WebDriver-387.10.10.10.40.140",
                    # },
                    #  "/Library/LaunchAgents": {
                    #     "com.nvidia.nvagent.plist":       "WebDriver-387.10.10.10.40.140",
                    # },
                    # "/Library/LaunchDaemons": {
                    #     "com.nvidia.nvroothelper.plist":  "WebDriver-387.10.10.10.40.140",
                    # },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        # Restore OpenCL by adding missing compiler files
                        **({ "GPUCompiler.framework": "11.6"} if self._xnu_major >= os_data.monterey else {}),
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        # Due to how late the Auxiliary cache loads, NVDAStartup will match first and then the Web Driver kexts.
                        # This has no effect for Maxwell and Pascal, however for development purposes, Tesla and Kepler are partially supported.
                        "NVDAStartup.kext",
                    ],
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Nvidia Web Drivers
        """
        if self.native_os() is True:
            return {}

        if self._xnu_major not in self._constants.legacy_accel_support and self._dortania_internal_check() is False:
            return {**self._model_specific_patches()}

        return {
            **NonMetal(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **NonMetalIOAccelerator(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **NonMetalCoreDisplay(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **MontereyWebKit(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
            **NonMetalEnforcement(self._xnu_major, self._xnu_minor, self._os_build).patches(),
        }