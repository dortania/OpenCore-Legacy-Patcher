"""
intel_ivy_bridge.py: Intel Ivy Bridge detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base            import PatchType

from ...shared_patches.metal_3802      import LegacyMetal3802
from ...shared_patches.big_sur_gva     import BigSurGVA
from ...shared_patches.monterey_opencl import MontereyOpenCL
from ...shared_patches.big_sur_opencl  import BigSurOpenCL
from ...shared_patches.monterey_webkit import MontereyWebKit

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelIvyBridge(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Intel Ivy Bridge"


    def present(self) -> bool:
        """
        Targeting Intel Ivy Bridge GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Ivy_Bridge
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 12, Monterey
        """
        return self._xnu_major < os_data.monterey.value


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


    def requires_metallib_support_pkg(self) -> bool:
        """
        New compiler format introduced in macOS 15, Sequoia
        """
        return self._xnu_major >= os_data.sequoia.value


    def _resolve_ivy_bridge_framebuffers(self) -> str:
        """
        Resolve patchset directory for Ivy Bridge framebuffers:
        - AppleIntelFramebufferCapri.kext
        - AppleIntelHD4000Graphics.kext
        """
        if self._xnu_major < os_data.sonoma:
            return "11.7.10"
        if self._xnu_float < self.macOS_14_4:
            return "11.7.10-23"
        return "11.7.10-23.4"


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Intel Ivy Bridge": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelHD4000GraphicsGLDriver.bundle":  "11.7.10",
                        "AppleIntelHD4000GraphicsMTLDriver.bundle": "11.7.10" if self._xnu_major < os_data.ventura else "11.7.10-22",
                        "AppleIntelHD4000GraphicsVADriver.bundle":  "11.7.10",
                        "AppleIntelFramebufferCapri.kext":          self._resolve_ivy_bridge_framebuffers(),
                        "AppleIntelHD4000Graphics.kext":            self._resolve_ivy_bridge_framebuffers(),
                        "AppleIntelIVBVA.bundle":                   "11.7.10",
                        "AppleIntelGraphicsShared.bundle":          "11.7.10", # libIGIL-Metal.dylib pulled from 11.0 Beta 6
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Intel Ivy Bridge iGPUs
        """
        if self.native_os() is True:
            return {}

        return {
            **LegacyMetal3802(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **BigSurGVA(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **BigSurOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyWebKit(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
        }
