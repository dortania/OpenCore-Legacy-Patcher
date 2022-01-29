import subprocess
from resources import build
from data import example_data, model_array


def validate(settings):
    # Runs through ocvalidate to check for errors

    valid_dumps = [
        example_data.MacBookPro.MacBookPro92_Stock,
        example_data.MacBookPro.MacBookPro111_Stock,
        # example_data.MacBookPro.MacBookPro171_Stock,
        # example_data.Macmini.Macmini91_Stock,
        example_data.iMac.iMac81_Stock,
        example_data.iMac.iMac112_Stock,
        example_data.iMac.iMac122_Upgraded,
        example_data.iMac.iMac122_Upgraded_Nvidia,
        example_data.iMac.iMac151_Stock,
        example_data.MacPro.MacPro31_Stock,
        example_data.MacPro.MacPro31_Upgrade,
        example_data.MacPro.MacPro31_Modern_AMD,
        example_data.MacPro.MacPro31_Modern_Kepler,
        example_data.MacPro.MacPro41_Upgrade,
        example_data.MacPro.MacPro41_Modern_AMD,
        example_data.MacPro.MacPro41_51__Flashed_Modern_AMD,
    ]

    valid_dumps_native = [
        example_data.iMac.iMac201_Stock,
        example_data.MacBookPro.MacBookPro141_SSD_Upgrade,
    ]

    settings.validate = True

    def build_prebuilt():
        for model in model_array.SupportedSMBIOS:
            print(f"Validating predefined model: {model}")
            settings.custom_model = model
            build.BuildOpenCore(settings.custom_model, settings).build_opencore()
            result = subprocess.run([settings.ocvalidate_path, f"{settings.opencore_release_folder}/EFI/OC/config.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("Error on build!")
                print(result.stdout.decode())
                raise Exception(f"Validation failed for predefined model: {model}")
            else:
                print(f"Validation succeeded for predefined model: {model}")

    def build_dumps():
        for model in valid_dumps:
            settings.computer = model
            settings.custom_model = ""
            print(f"Validating dumped model: {settings.computer.real_model}")
            build.BuildOpenCore(settings.computer.real_model, settings).build_opencore()
            result = subprocess.run([settings.ocvalidate_path, f"{settings.opencore_release_folder}/EFI/OC/config.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("Error on build!")
                print(result.stdout.decode())
                raise Exception(f"Validation failed for predefined model: {settings.computer.real_model}")
            else:
                print(f"Validation succeeded for predefined model: {settings.computer.real_model}")

    # First run is with default settings
    build_prebuilt()
    build_dumps()
    # Second run, flip all settings
    settings.verbose_debug = True
    settings.opencore_debug = True
    settings.opencore_build = "DEBUG"
    settings.kext_debug = True
    settings.kext_variant = "DEBUG"
    settings.kext_debug = True
    settings.showpicker = False
    settings.sip_status = False
    settings.secure_status = True
    settings.firewire_boot = True
    settings.nvme_boot = True
    settings.enable_wake_on_wlan = True
    settings.disable_tb = True
    settings.force_surplus = True
    settings.software_demux = True
    settings.serial_settings = "Minimal"
    build_prebuilt()
    build_dumps()
