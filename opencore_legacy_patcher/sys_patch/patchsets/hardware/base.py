"""
base.py: Base class for hardware patch set detection
"""

from enum    import StrEnum
from pathlib import Path

from ..base import BasePatchset

from ....constants import Constants

from ....datasets.os_data       import os_data
from ....datasets.sip_data      import system_integrity_protection
from ....detections.amfi_detect import AmfiConfigDetectLevel
from ....detections             import device_probe


class HardwareVariant(StrEnum):
    """
    Hardware variant for patch set
    """
    GRAPHICS:      str = "Graphics"
    NETWORKING:    str = "Networking"
    AUDIO:         str = "Audio"
    MISCELLANEOUS: str = "Miscellaneous"


class HardwareVariantGraphicsSubclass(StrEnum):
    """
    Graphics hardware variant subclass
    """
    NON_METAL_GRAPHICS:   str = "Non-Metal Graphics"
    METAL_3802_GRAPHICS:  str = "Metal 3802 Graphics"
    METAL_31001_GRAPHICS: str = "Metal 31001 Graphics"
    HEADLESS_GRAPHICS:    str = "Headless Graphics"
    NOT_APPLICABLE:       str = "N/A"


class BaseHardware(BasePatchset):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__()
        self._xnu_major = xnu_major
        self._xnu_minor = xnu_minor
        self._os_build  = os_build
        self._constants = global_constants
        self._computer  = global_constants.computer

        self._xnu_float = float(f"{self._xnu_major}.{self._xnu_minor}")


    def name(self) -> str:
        """
        Name of the patch set
        """
        raise NotImplementedError


    def present(self) -> bool:
        """
        Whether the hardware is present in the system
        """
        raise NotImplementedError


    def native_os(self) -> bool:
        """
        Is on native OS
        """
        raise NotImplementedError


    def hardware_variant(self) -> HardwareVariant:
        """
        What hardware variant is this patch set for
        """
        raise NotImplementedError


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        What subclass of graphics
        """
        return HardwareVariantGraphicsSubclass.NOT_APPLICABLE


    def required_amfi_level(self) -> AmfiConfigDetectLevel:
        """
        What level of AMFI configuration is required for this patch set
        Currently defaulted to AMFI needing to be disabled
        """
        return AmfiConfigDetectLevel.ALLOW_ALL


    def requires_primary_kernel_cache(self) -> bool:
        """
        Whether patch set requires access to the primary kernel cache
        ex. Boot/System Kernel Collection on Big Sur and newer
        """
        return False


    def requires_kernel_debug_kit(self) -> bool:
        """
        Whether patch set requires access to the Kernel Debug Kit
        """
        return False


    def requires_metallib_support_pkg(self) -> bool:
        """
        Whether patch set requires access to the MetallibSupportPkg PKG
        """
        return False


    def required_system_integrity_protection_configurations(self) -> list[str]:
        """
        List of required SIP configurations for the patch set
        """
        if self._xnu_major >= os_data.ventura.value:
            return system_integrity_protection.root_patch_sip_ventura
        if self._xnu_major >= os_data.big_sur.value:
            return system_integrity_protection.root_patch_sip_big_sur
        return system_integrity_protection.root_patch_sip_mojave


    def patches(self) -> dict:
        """
        Dictionary of patches
        """
        raise NotImplementedError


    def _is_gpu_architecture_present(self, gpu_architectures: list[device_probe.GPU]) -> bool:
        """
        Check if a GPU architecture is present
        """
        for gpu in self._computer.gpus:
            if not gpu.class_code:
                continue
            if not gpu.arch:
                continue
            if gpu.class_code == 0xFFFFFFFF:
                continue

            if gpu.arch in gpu_architectures:
                return True

        return False


    def _resolve_monterey_framebuffers(self) -> str:
        """
        Resolve patchset directory for framebuffers last supported in Monterey:
        - AppleIntelBDWGraphics.kext
        - AppleIntelBDWGraphicsFramebuffer.kext
        - AppleIntelFramebufferAzul.kext
        - AppleIntelHD5000Graphics.kext
        - AppleIntelSKLGraphics.kext
        - AppleIntelSKLGraphicsFramebuffer.kext
        - AMDRadeonX4000.kext
        - AMDRadeonX5000.kext
        """
        if self._xnu_major < os_data.sonoma.value:
            return "12.5"
        if self._xnu_float < self.macOS_14_4:
            return "12.5-23"
        return "12.5-23.4"


    def _dortania_internal_check(self) -> None:
        """
        Determine whether to unlock Dortania Developer mode
        """
        return Path("~/.dortania_developer").expanduser().exists()
