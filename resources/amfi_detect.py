# Determine AppleMobileFileIntegrity's OS configuration

from resources import utilities

class amfi_configuration_detection:

    def __init__(self):
        self.AMFI_ALLOW_TASK_FOR_PID =      False
        self.AMFI_ALLOW_INVALID_SIGNATURE = False
        self.AMFI_LV_ENFORCE_THIRD_PARTY =  False
        self.AMFI_ALLOW_EVERYTHING =        False
        self.SKIP_LIBRARY_VALIDATION =      False

        self.boot_args = []
        self.oclp_args = []

        self.init_nvram_dicts()

        self.parse_amfi_bitmask()
        self.parse_amfi_boot_args()
        self.parse_oclp_configuration()


    def init_nvram_dicts(self):
        boot_args = utilities.get_nvram("boot-args", decode=True)
        oclp_args = utilities.get_nvram("OCLP-Settings", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)

        if boot_args:
            self.boot_args = boot_args.split(" ")

        if oclp_args:
            self.oclp_args = oclp_args.split(" ")


    def parse_amfi_bitmask(self):
        # See data/amfi_data.py for more information
        amfi_value = 0
        for arg in self.boot_args:
            if arg.startswith("amfi="):
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

        if amfi_value & 0x1:
            self.AMFI_ALLOW_TASK_FOR_PID = True
        if amfi_value & 0x2:
            self.AMFI_ALLOW_INVALID_SIGNATURE = True
        if amfi_value & 0x4:
            self.AMFI_LV_ENFORCE_THIRD_PARTY = True
        if amfi_value & 0x80:
            self.AMFI_ALLOW_EVERYTHING = True
            self.SKIP_LIBRARY_VALIDATION = True
            self.AMFI_ALLOW_INVALID_SIGNATURE = True


    def parse_amfi_boot_args(self):
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


    def parse_oclp_configuration(self):
        if "-allow_amfi" in self.oclp_args:
            self.SKIP_LIBRARY_VALIDATION = True


    def check_config(self, level):
        # Levels:
        # - 0: No checks
        # - 1. Library Validation (Monterey and Older)
        # - 2. Library Validation and Signature Checks (Ventura and Newer)
        # - 3. Disable all AMFI checks

        if level == 0:
            return True

        if level == 1:
            return self.SKIP_LIBRARY_VALIDATION
        if level == 2:
            return bool(self.SKIP_LIBRARY_VALIDATION and self.AMFI_ALLOW_INVALID_SIGNATURE)
        if level == 3:
            return self.AMFI_ALLOW_EVERYTHING

        return False