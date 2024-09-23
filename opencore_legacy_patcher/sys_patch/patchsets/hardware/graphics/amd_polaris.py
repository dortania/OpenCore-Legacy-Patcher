"""
amd_polaris.py: AMD Polaris detection
"""

from .amd_legacy_gcn import AMDLegacyGCN

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.monterey_gva    import MontereyGVA
from ...shared_patches.monterey_opencl import MontereyOpenCL
from ...shared_patches.amd_opencl      import AMDOpenCL

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class AMDPolaris(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: AMD Polaris"


    def present(self) -> bool:
        """
        Targeting AMD Polaris GPUs with CPUs lacking AVX2.0 or missing Framebuffer patches (ie. MacBookPro13,3 and MacBookPro14,3)
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.AMD.Archs.Polaris
            ]
        ) and ("AVX2" not in self._computer.cpu.leafs or self._computer.real_model in ["MacBookPro13,3", "MacBookPro14,3"])


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

        # For MacBookPro13,3 missing framebuffers (ex. 'ATY,Berbice')
        if self._computer.real_model in ["MacBookPro13,3"]:
            # Since dropped at the same time, we can use the same patches
            result = AMDLegacyGCN(self._xnu_major, self._xnu_minor, self._os_build, self._constants)._model_specific_patches()
            # Have to rename 'AMD Legacy GCN' to 'AMD Polaris' for model detection
            return {"AMD Polaris": result["AMD Legacy GCN"]}

        # For MacBookPro14,3 (and other AMD dGPUs that no longer function in Sonoma)
        # iMac18,2/3 still function with the generic framebuffer, however if issues arise
        # we'll downgrade them as well.
        if self._computer.real_model in ["MacBookPro14,3"]:
            if self._xnu_major < os_data.sonoma.value:
                return {}
            return {
                "AMD Polaris": {
                    PatchType.OVERWRITE_SYSTEM_VOLUME: {
                        "/System/Library/Extensions": {
                            "AMD9500Controller.kext":  "13.5.2",
                            "AMD10000Controller.kext": "13.5.2",
                            "AMDFramebuffer.kext":     "13.5.2",
                            "AMDSupport.kext":         "13.5.2",
                        },
                    },
                },
            }

        # Assuming non-AVX2.0 CPUs
        # Note missing framebuffers are not restored (ex. 'ATY,Berbice')
        return {
            "AMD Polaris": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AMDRadeonX4000.kext":           self._resolve_monterey_framebuffers(),
                        "AMDRadeonX4000HWServices.kext": "12.5",
                        "AMDRadeonVADriver2.bundle":     "12.5",
                        "AMDRadeonX4000GLDriver.bundle": "12.5",
                        "AMDMTLBronzeDriver.bundle":     "12.5" if self._xnu_major < os_data.sequoia else "12.5-24",
                        "AMDShared.bundle":              "12.5",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for AMD Polaris GPUs
        """
        if self.native_os() is True:
            return {}

        # Minimal amount of patches required for 2017 Polaris
        if self._computer.real_model in ["MacBookPro14,3"]:
            return self._model_specific_patches()

        _base = {
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),
        }
        if "AVX2" not in self._computer.cpu.leafs:
            _base.update({
                **AMDOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            })

        # AMD GCN and newer GPUs can still use the native GVA stack
        _base.update({
            **MontereyGVA(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).revert_patches(),
        })

        return _base