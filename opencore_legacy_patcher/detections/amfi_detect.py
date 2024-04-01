"""
amfi_detect.py: Determine AppleMobileFileIntegrity's OS configuration
"""

import enum

from ..support import utilities
from ..datasets import amfi_data


class AmfiConfigDetectLevel(enum.IntEnum):
    """
    Configuration levels used by AmfiConfigurationDetection
    """

    NO_CHECK:                   int = 0
    LIBRARY_VALIDATION:         int = 1  # For Ventura, use LIBRARY_VALIDATION_AND_SIG
    LIBRARY_VALIDATION_AND_SIG: int = 2
    ALLOW_ALL:                  int = 3


class AmfiConfigurationDetection:
    """
    Detect AppleMobileFileIntegrity's OS configuration

    Usage:

    >>> import amfi_detect
    >>> can_patch = amfi_detect.AmfiConfigurationDetection().check_config(amfi_detect.AmfiConfigDetectLevel.ALLOW_ALL)

    """

    def __init__(self) -> None:
        self.AMFI_ALLOW_TASK_FOR_PID:      bool = False
        self.AMFI_ALLOW_INVALID_SIGNATURE: bool = False
        self.AMFI_LV_ENFORCE_THIRD_PARTY:  bool = False
        self.AMFI_ALLOW_EVERYTHING:        bool = False
        self.SKIP_LIBRARY_VALIDATION:      bool = False

        self.boot_args: list = []
        self.oclp_args: list = []

        self._init_nvram_dicts()

        self._parse_amfi_bitmask()
        self._parse_amfi_boot_args()
        self._parse_oclp_configuration()


    def _init_nvram_dicts(self) -> None:
        """
        Initialize the boot-args and OCLP-Settings NVRAM dictionaries
        """

        boot_args = utilities.get_nvram("boot-args", decode=True)
        oclp_args = utilities.get_nvram("OCLP-Settings", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)

        if boot_args:
            self.boot_args = boot_args.split(" ")

        if oclp_args:
            self.oclp_args = oclp_args.split(" ")


    def _parse_amfi_bitmask(self) -> None:
        """
        Parse the AMFI bitmask from boot-args
        See data/amfi_data.py for more information
        """

        amfi_value = 0
        for arg in self.boot_args:
            if not arg.startswith("amfi="):
                continue
            try:
                amfi_value = arg.split("=")
                if len(amfi_value) != 2:
                    return
                amfi_value = amfi_value[1]
                if amfi_value.startswith("0x"):
                    amfi_value = int(amfi_value, 16)
                else:
                    amfi_value = int(amfi_value)
            except:
                return
            break

        if amfi_value == 0:
            return

        self.AMFI_ALLOW_TASK_FOR_PID:      bool = amfi_value & amfi_data.AppleMobileFileIntegrity.AMFI_ALLOW_TASK_FOR_PID
        self.AMFI_ALLOW_INVALID_SIGNATURE: bool = amfi_value & amfi_data.AppleMobileFileIntegrity.AMFI_ALLOW_INVALID_SIGNATURE
        self.AMFI_LV_ENFORCE_THIRD_PARTY:  bool = amfi_value & amfi_data.AppleMobileFileIntegrity.AMFI_LV_ENFORCE_THIRD_PARTY

        if amfi_value & amfi_data.AppleMobileFileIntegrity.AMFI_ALLOW_EVERYTHING:
            self.AMFI_ALLOW_EVERYTHING        = True
            self.SKIP_LIBRARY_VALIDATION      = True
            self.AMFI_ALLOW_INVALID_SIGNATURE = True


    def _parse_amfi_boot_args(self) -> None:
        """
        Parse the AMFI boot-args
        """

        for arg in self.boot_args:
            if arg.startswith("amfi_unrestrict_task_for_pid"):
                value = arg.split("=")
                if len(value) == 2:
                    if value[1] in ["0x1", "1"]:
                        self.AMFI_ALLOW_TASK_FOR_PID = True
            elif arg.startswith("amfi_allow_any_signature"):
                value = arg.split("=")
                if len(value) == 2:
                    if value[1] in ["0x1", "1"]:
                        self.AMFI_ALLOW_INVALID_SIGNATURE = True
            elif arg.startswith("amfi_get_out_of_my_way"):
                value = arg.split("=")
                if len(value) == 2:
                    if value[1] in ["0x1", "1"]:
                        self.AMFI_ALLOW_EVERYTHING = True
                        self.SKIP_LIBRARY_VALIDATION = True
                        self.AMFI_ALLOW_INVALID_SIGNATURE = True


    def _parse_oclp_configuration(self) -> None:
        """
        Parse the OCLP configuration
        """

        if "-allow_amfi" in self.oclp_args:
            self.SKIP_LIBRARY_VALIDATION = True


    def check_config(self, level: int) -> bool:
        """
        Check the AMFI configuration based on provided AMFI level
        See AmfiConfigLevel enum for valid levels

        Parameters:
            level (int): The level of AMFI checks to check for

        Returns:
            bool: True if the AMFI configuration matches the level, False otherwise
        """

        if level == AmfiConfigDetectLevel.NO_CHECK:
            return True
        if level == AmfiConfigDetectLevel.LIBRARY_VALIDATION:
            return self.SKIP_LIBRARY_VALIDATION
        if level == AmfiConfigDetectLevel.LIBRARY_VALIDATION_AND_SIG:
            return bool(self.SKIP_LIBRARY_VALIDATION and self.AMFI_ALLOW_INVALID_SIGNATURE)
        if level == AmfiConfigDetectLevel.ALLOW_ALL:
            return self.AMFI_ALLOW_EVERYTHING

        return False