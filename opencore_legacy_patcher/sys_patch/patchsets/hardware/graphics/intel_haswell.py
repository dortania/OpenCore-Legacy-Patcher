"""
intel_haswell.py: Intel Haswell detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.metal_3802      import LegacyMetal3802
from ...shared_patches.monterey_gva    import MontereyGVA
from ...shared_patches.monterey_opencl import MontereyOpenCL
from ...shared_patches.tahoe_graphics  import TahoeGraphics

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelHaswell(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Intel Haswell"


    def present(self) -> bool:
        """
        Targeting Intel Haswell GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Haswell
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 13, Ventura
        """
        return self._xnu_major < os_data.ventura.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        Type of hardware variant subclass
        """
        return HardwareVariantGraphicsSubclass.METAL_3802_GRAPHICS


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        framebuffer = "12.7.6" if self._xnu_major == os_data.ventura.value else "12.7.6-23.4"
        if self._xnu_major == os_data.sonoma.value and self._xnu_float < self.macOS_14_4:
            framebuffer = "12.7.6-23"
        graphics_kext = "12.7.6-22" if self._xnu_major == os_data.ventura.value else framebuffer
        metal_driver = "12.7.6-3802-24" if self._xnu_major >= os_data.sequoia.value else "12.7.6-3802"
        return {
            "Intel Haswell": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelFramebufferAzul.kext":           framebuffer,
                        "AppleIntelHD5000Graphics.kext":            graphics_kext,
                        "AppleIntelHD5000GraphicsGLDriver.bundle":  "12.7.6",
                        "AppleIntelHD5000GraphicsMTLDriver.bundle": metal_driver,
                        "AppleIntelHD5000GraphicsVADriver.bundle":  "12.7.6",
                        "AppleIntelHSWVA.bundle":                   "12.7.6",
                        "AppleIntelGraphicsShared.bundle":          "12.7.6",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Intel Haswell iGPUs
        """
        if self.native_os() is True:
            return {}

        return {
            **LegacyMetal3802(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyGVA(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),

        }
