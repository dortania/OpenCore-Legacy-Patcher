"""
t1_security.py: T1 Security Chip detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants import Constants

from .....datasets.os_data import os_data


class T1SecurityChip(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: T1 Security Chip"


    def present(self) -> bool:
        """
        Targeting T1 Security Chip
        """
        return self._computer.t1_chip


    def native_os(self) -> bool:
        """
        Dropped support with macOS 14, Sonoma
        """
        return self._xnu_major < os_data.sonoma.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def patches(self) -> dict:
        """
        Patches for T1 Security Chip
        """
        if self.native_os() is True:
            return {}

        return {
            "T1 Security Chip": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    # Required for Apple Pay
                    "/usr/lib": {
                        "libNFC_Comet.dylib":          "13.6",
                        "libNFC_HAL.dylib":            "13.6",

                        "libnfshared.dylib":           "13.6",
                        "libnfshared.dylibOld.dylib":  "13.6",
                        "libnfstorage.dylib":          "13.6",
                        "libnfrestore.dylib":          "13.6",

                        "libPN548_API.dylib":          "13.6"
                    },
                    "/usr/libexec": {
                        "biometrickitd":      "13.6",    # Required for Touch ID
                        "nfcd":               "13.6",    # Required for Apple Pay
                        "nfrestore_service":  "13.6",    # Required for Apple Pay
                    },
                    "/usr/standalone/firmware/nfrestore/firmware/fw": {
                        "PN549_FW_02_01_5A_rev88207.bin":         "13.6",
                        "SN100V_FW_A3_01_01_81_rev127208.bin":    "13.6",
                        "SN200V_FW_B1_02_01_86_rev127266.bin":    "13.6",
                        "SN300V_FW_B0_02_01_22_rev129172.bin":    "13.6",
                    }
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks/LocalAuthentication.framework/Support": {
                        "SharedUtils.framework": f"13.6-{self._xnu_major}" if self._xnu_major < os_data.sequoia else f"13.7.1-{self._xnu_major}",  # Required for Password Authentication (SharedUtils.framework)
                        **({ "MechanismPlugins": "15.0 Beta 4" } if self._xnu_major >= os_data.sequoia else {}), # Required to add a TouchID fingerprint
                        **({ "ModulePlugins": "15.1" } if self._xnu_float >= self.macOS_15_2 else {}),
                    },
                    "/System/Library/PrivateFrameworks": {
                        "EmbeddedOSInstall.framework": "13.6",  # Required for biometrickitd
                        **({ "NearField.framework": "14.7.2" } if self._xnu_major >= os_data.sequoia else {}),
                    },
                }
            },
        }