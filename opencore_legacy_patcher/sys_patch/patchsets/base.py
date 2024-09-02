"""
base.py: Base class for all patch sets
"""

from enum import StrEnum


class PatchType(StrEnum):
    """
    Type of patch
    """
    INSTALL_SYSTEM_VOLUME = "Install System Volume"
    INSTALL_DATA_VOLUME   = "Install Data Volume"
    REMOVE_SYSTEM_VOLUME  = "Remove System Volume"
    REMOVE_DATA_VOLUME    = "Remove Data Volume"
    EXECUTE               = "Execute"


class DynamicPatchset(StrEnum):
    MetallibSupportPkg = "MetallibSupportPkg"


class BasePatchset:

    def __init__(self) -> None:
        # XNU Kernel versions
        self.macOS_12_0_B7: float = 21.1
        self.macOS_12_4:    float = 21.5
        self.macOS_12_5:    float = 21.6
        self.macOS_13_3:    float = 22.4
        self.macOS_14_1:    float = 23.1
        self.macOS_14_2:    float = 23.2
        self.macOS_14_4:    float = 23.4