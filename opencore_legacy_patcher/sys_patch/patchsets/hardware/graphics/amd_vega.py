"""
amd_vega.py: AMD Vega detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.monterey_gva    import MontereyGVA
from ...shared_patches.monterey_opencl import MontereyOpenCL
from ...shared_patches.amd_opencl      import AMDOpenCL

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class AMDVega(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: AMD Vega"


    def present(self) -> bool:
        """
        Targeting AMD Vega GPUs with CPUs lacking AVX2.0
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.AMD.Archs.Vega
            ]
        ) and "AVX2" not in self._computer.cpu.leafs


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
        return HardwareVariantGraphicsSubclass.METAL_31001_GRAPHICS


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
            "AMD Vega": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AMDRadeonX5000.kext":            self._resolve_monterey_framebuffers(),

                        "AMDRadeonVADriver2.bundle":      "12.5",
                        "AMDRadeonX5000GLDriver.bundle":  "12.5",
                        "AMDRadeonX5000MTLDriver.bundle": "12.5" if self._xnu_major < os_data.sequoia else "12.5-24",
                        "AMDRadeonX5000Shared.bundle":    "12.5",

                        "AMDShared.bundle":               "12.5",
                    },
                },
            },
        }


    def _model_specific_patches_extended(self) -> dict:
        """
        Support mixed legacy and modern AMD GPUs
        Specifically systems using AMD GCN 1-3 and Vega (ex. MacPro6,1 with eGPU)
        Assume 'AMD Legacy GCN' patchset is installed alongside this
        """
        if self._is_gpu_architecture_present([
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000
            ]) is False:
            return {}

        return {
            "AMD Vega Extended": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AMDRadeonX5000HWServices.kext": "12.5",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for AMD Vega GPUs
        """
        if self.native_os() is True:
            return {}

        return {
            # AMD GCN and newer GPUs can still use the native GVA stack
            **MontereyGVA(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).revert_patches(),

            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **AMDOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),
            **self._model_specific_patches_extended(),
        }