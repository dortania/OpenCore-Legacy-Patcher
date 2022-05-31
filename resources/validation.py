import subprocess
from resources import build, sys_patch_helpers
from data import example_data, model_array, sys_patch_dict, os_data
from pathlib import Path


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
        example_data.MacPro.MacPro41_51_Flashed_NVIDIA_WEB_DRIVERS,
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


    def validate_root_patch_files(major_kernel, minor_kernel):
        patchset = sys_patch_dict.SystemPatchDictionary(major_kernel, minor_kernel, settings.legacy_accel_support)
        host_os_float = float(f"{major_kernel}.{minor_kernel}")
        for patch_subject in patchset:
            for patch_core in patchset[patch_subject]:
                patch_os_min_float = float(f'{patchset[patch_subject][patch_core]["OS Support"]["Minimum OS Support"]["OS Major"]}.{patchset[patch_subject][patch_core]["OS Support"]["Minimum OS Support"]["OS Minor"]}')
                patch_os_max_float = float(f'{patchset[patch_subject][patch_core]["OS Support"]["Maximum OS Support"]["OS Major"]}.{patchset[patch_subject][patch_core]["OS Support"]["Maximum OS Support"]["OS Minor"]}')
                if (host_os_float < patch_os_min_float or host_os_float > patch_os_max_float):
                    continue
                for install_type in ["Install", "Install Non-Root"]:
                    if install_type in patchset[patch_subject][patch_core]:
                        for install_directory in patchset[patch_subject][patch_core][install_type]:
                            for install_file in patchset[patch_subject][patch_core][install_type][install_directory]:
                                source_file = str(settings.payload_local_binaries_root_path) + "/" + patchset[patch_subject][patch_core][install_type][install_directory][install_file] + install_directory + "/" + install_file
                                if not Path(source_file).exists():
                                    print(f"File not found: {source_file}")
                                    raise Exception(f"Failed to find {source_file}")

        print(f"Validating Root Patch Dictionary integrity for Darwin {major_kernel}.{minor_kernel}")
        if not sys_patch_helpers.sys_patch_helpers(settings).generate_patchset_plist(patchset, "OpenCore-Legacy-Patcher"):
            raise Exception("Failed to generate patchset plist")


    def validate_sys_patch():
        if Path(settings.payload_local_binaries_root_path_zip).exists():
            print("Validating Root Patch File integrity")
            if not Path(settings.payload_local_binaries_root_path).exists():
                subprocess.run(["ditto", "-V", "-x", "-k", "--sequesterRsrc", "--rsrc", settings.payload_local_binaries_root_path_zip, settings.payload_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for supported_os in [os_data.os_data.big_sur, os_data.os_data.monterey]:
                validate_root_patch_files(supported_os, 6)
            print("Validating SNB Board ID patcher")
            settings.computer.reported_board_id = "Mac-7BA5B2DFE22DDD8C"
            sys_patch_helpers.sys_patch_helpers(settings).snb_board_id_patch(settings.payload_local_binaries_root_path)
        else:
            print("Skipping Root Patch File integrity validation")

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
    validate_sys_patch()
