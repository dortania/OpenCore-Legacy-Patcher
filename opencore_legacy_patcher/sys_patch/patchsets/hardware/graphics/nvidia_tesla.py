"""
nvidia_tesla.py: Nvidia Tesla detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.non_metal       import NonMetal
from ...shared_patches.monterey_webkit import MontereyWebKit

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class NvidiaTesla(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Nvidia Tesla"


    def present(self) -> bool:
        """
        Targeting Nvidia Tesla GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.NVIDIA.Archs.Tesla
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


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Nvidia Tesla": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "GeForceGA.bundle":            "10.13.6",
                        "GeForceTesla.kext":           "10.13.6",
                        "GeForceTeslaGLDriver.bundle": "10.13.6",
                        "GeForceTeslaVADriver.bundle": "10.13.6",
                        "NVDANV50HalTesla.kext":       "10.13.6",
                        "NVDAResmanTesla.kext":        "10.13.6",
                        # Apple dropped NVDAStartup in 12.0 Beta 7 (XNU 21.1)
                        **({ "NVDAStartup.kext":       "12.0 Beta 6" } if self._xnu_float >= self.macOS_12_0_B7 else {})
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Nvidia Tesla GPUs
        """
        if self.native_os() is True:
            return {}

        if self._xnu_major not in self._constants.legacy_accel_support and self._dortania_internal_check() is False:
            return {**self._model_specific_patches()}

        return {
            **NonMetal(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **MontereyWebKit(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
        }