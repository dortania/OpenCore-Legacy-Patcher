"""
amd_legacy_gcn.py: AMD Legacy GCN detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.monterey_gva    import MontereyGVA
from ...shared_patches.monterey_opencl import MontereyOpenCL
from ...shared_patches.amd_opencl      import AMDOpenCL

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class AMDLegacyGCN(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: AMD Legacy GCN"


    def present(self) -> bool:
        """
        Targeting AMD Legacy GCN GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000
            ]
        ) and self._computer.rosetta_active is False # Rosetta 2 mimics an AMD R9 270X


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
        # If 3802 GPU present, use stock Monterey bronze bundle even on Sequoia
        bronze_bundle_source = "12.5"
        if self._is_gpu_architecture_present(
            [
                device_probe.Intel.Archs.Ivy_Bridge,
                device_probe.Intel.Archs.Haswell,
                device_probe.NVIDIA.Archs.Kepler,
            ]
        ) is False:
            if self._xnu_major >= os_data.sequoia:
                bronze_bundle_source = "12.5-24"

        return {
            "AMD Legacy GCN": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AMD7000Controller.kext":        "12.5",
                        "AMD8000Controller.kext":        "12.5",
                        "AMD9000Controller.kext":        "12.5",
                        "AMD9500Controller.kext":        "12.5",
                        "AMD10000Controller.kext":       "12.5",
                        "AMDRadeonX4000.kext":           self._resolve_monterey_framebuffers(),
                        "AMDRadeonX4000HWServices.kext": "12.5",
                        "AMDFramebuffer.kext":           "12.5" if self._xnu_float < self.macOS_13_3 else "12.5-GCN",
                        "AMDSupport.kext":               "12.5",

                        "AMDRadeonVADriver.bundle":      "12.5",
                        "AMDRadeonVADriver2.bundle":     "12.5",
                        "AMDRadeonX4000GLDriver.bundle": "12.5",
                        "AMDMTLBronzeDriver.bundle":     bronze_bundle_source,
                        "AMDShared.bundle":              "12.5",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for AMD Legacy GCN GPUs
        """
        if self.native_os() is True:
            return {}

        _base = {}

        # AMD GCN and newer GPUs can still use the native GVA stack
        _base.update({
            **MontereyGVA(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).revert_patches(),
        })

        _base.update({
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **AMDOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),
        })

        return _base