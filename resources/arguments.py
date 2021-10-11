import sys
from resources import defaults, build, utilities, validation, sys_patch
from data import model_array

# Generic building args
class arguments:
    def __init__(self):
        self.args = utilities.check_cli_args()

    def parse_arguments(self, settings):
        if self.args.model:
            if self.args.model:
                print(f"- Using custom model: {self.args.model}")
                settings.custom_model = self.args.model
                defaults.generate_defaults.probe(settings.custom_model, False, settings)
            elif settings.computer.real_model not in model_array.SupportedSMBIOS and settings.allow_oc_everywhere is False:
                print(
                    """Your model is not supported by this patcher for running unsupported OSes!"

If you plan to create the USB for another machine, please select the "Change Model" option in the menu."""
                )
                sys.exit(1)
            else:
                print(f"- Using detected model: {settings.computer.real_model}")
                defaults.generate_defaults.probe(settings.custom_model, True, settings)

        if self.args.disk:
            print(f"- Install Disk set: {self.args.disk}")
            settings.disk = self.args.disk
        if self.args.validate:
            validation.validate(settings)
        if self.args.verbose:
            print("- Set verbose configuration")
            settings.verbose_debug = True
        else:
            settings.verbose_debug = False  # Override Defaults detected
        if self.args.debug_oc:
            print("- Set OpenCore DEBUG configuration")
            settings.opencore_debug = True
            settings.opencore_build = "DEBUG"
        if self.args.debug_kext:
            print("- Set kext DEBUG configuration")
            settings.kext_debug = True
        if self.args.hide_picker:
            print("- Set HidePicker configuration")
            settings.showpicker = False
        if self.args.disable_sip:
            print("- Set Disable SIP configuration")
            settings.sip_status = False
        else:
            settings.sip_status = True  # Override Defaults detected
        if self.args.disable_smb:
            print("- Set Disable SecureBootModel configuration")
            settings.secure_status = False
        else:
            settings.secure_status = True  # Override Defaults detected
        if self.args.vault:
            print("- Set Vault configuration")
            settings.vault = True
        if self.args.firewire:
            print("- Set FireWire Boot configuration")
            settings.firewire_boot = True
        if self.args.nvme:
            print("- Set NVMe Boot configuration")
            settings.nvme_boot = True
        # if self.args.disable_amfi:
        #     print("- Set Disable AMFI configuration")
        #     settings.amfi_status = False
        if self.args.wlan:
            print("- Set Wake on WLAN configuration")
            settings.enable_wake_on_wlan = True
        if self.args.disable_tb:
            print("- Set Disable Thunderbolt configuration")
            settings.disable_tb = True
        if self.args.force_surplus:
            print("- Forcing SurPlus override configuration")
            settings.force_surplus = True
        if self.args.moderate_smbios:
            print("- Set Moderate SMBIOS Patching configuration")
            settings.serial_settings = "Moderate"
        if self.args.smbios_spoof:
            if self.args.smbios_spoof == "Minimal":
                settings.serial_settings = "Minimal"
            elif self.args.smbios_spoof == "Moderate":
                settings.serial_settings = "Moderate"
            elif self.args.smbios_spoof == "Advanced":
                settings.serial_settings = "Advanced"
            else:
                print(f"- Unknown SMBIOS arg passed: {self.args.smbios_spoof}")

        if self.args.support_all:
            print("- Building for natively supported model")
            settings.allow_oc_everywhere = True
            settings.serial_settings = "None"

        # Avoid running the root patcher if we're just building
        if self.args.build:
            build.BuildOpenCore(settings.custom_model or settings.computer.real_model, settings).build_opencore()
        elif self.args.patch_sys_vol:
            if self.args.moj_cat_accel:
                print("- Set Mojave/Catalina root patch configuration")
                settings.moj_cat_accel = True
            print("- Set System Volume patching")
            sys_patch.PatchSysVolume(settings.custom_model or settings.computer.real_model, settings).start_patch()
        elif self.args.unpatch_sys_vol:
            print("- Set System Volume unpatching")
            sys_patch.PatchSysVolume(settings.custom_model or settings.computer.real_model, settings).start_unpatch()
