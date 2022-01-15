# Generate Default Data
from resources import utilities, device_probe, generate_smbios
from data import model_array, smbios_data


class generate_defaults:
    def probe(model, host_is_target, settings):
        # Generate Default Data
        # Takes in Settings data set, and returns updated Settings
        settings.sip_status = True
        settings.secure_status = False  # Default false for Monterey
        settings.amfi_status = True

        if host_is_target:
            if utilities.check_metal_support(device_probe, settings.computer) is False:
                settings.disable_cs_lv = True
            if settings.computer.gpus: 
                for gpu in settings.computer.gpus:
                    if gpu.arch == device_probe.NVIDIA.Archs.Kepler:
                        # 12.0 (B7+): Kepler are now unsupported
                        settings.sip_status = False
                        settings.amfi_status = True
                        settings.allow_fv_root = True  #  Allow FileVault on broken seal
                        break
            if model not in model_array.SupportedSMBIOS:
                # Allow FeatureUnlock on native models
                settings.fu_status = True
                settings.fu_arguments = None
            else:
                settings.fu_status = True
                settings.fu_arguments = " -disable_sidecar_mac"
            if (
                isinstance(settings.computer.wifi, device_probe.Broadcom)
                and settings.computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
            ) or (isinstance(settings.computer.wifi, device_probe.Atheros) and settings.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40):
                # 12.0: Legacy Wireless chipsets require root patching
                settings.sip_status = False
                settings.allow_fv_root = True  #  Allow FileVault on broken seal

            if settings.computer.gpus: 
                for gpu in settings.computer.gpus:
                    if gpu.arch in [
                        device_probe.AMD.Archs.Legacy_GCN_7000,
                        device_probe.AMD.Archs.Legacy_GCN_8000,
                        device_probe.AMD.Archs.Legacy_GCN_9000,
                        device_probe.AMD.Archs.Polaris,
                        device_probe.AMD.Archs.Vega,
                        device_probe.AMD.Archs.Navi,
                    ]:
                        # Allow H.265 on AMD
                        try:
                            smbios_data.smbios_dictionary[model]["Socketed GPUs"]
                            settings.serial_settings = "Minimal"
                        except KeyError:
                            pass
                        break
        elif model in ["MacPro4,1", "MacPro5,1"]:
            # Allow H.265 on AMD
            # Assume 2009+ machines have Polaris on pre-builts (internal testing)
            # Hardware Detection will never hit this
            settings.serial_settings = "Minimal"
        elif model in model_array.LegacyGPU:
            settings.disable_cs_lv = True
        elif model in model_array.SupportedSMBIOS:
            settings.fu_status = True
            settings.fu_arguments = " -disable_sidecar_mac"

        if model in model_array.LegacyGPU:
            if host_is_target and utilities.check_metal_support(device_probe, settings.computer) is True:
                # Building on device and we have a native, supported GPU
                if settings.computer.dgpu and settings.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                    settings.sip_status = False
                    # settings.secure_status = True  # Monterey
                    settings.allow_fv_root = True  #  Allow FileVault on broken seal
            else:
                settings.sip_status = False  #    Unsigned kexts
                settings.secure_status = False  # Root volume modified
                settings.amfi_status = False  #   Unsigned binaries
                settings.allow_fv_root = True  #  Allow FileVault on broken seal
        if model in model_array.ModernGPU:
            # Systems with Ivy or Kepler GPUs, Monterey requires root patching for accel
            settings.sip_status = False  #    Unsigned kexts
            settings.secure_status = False  # Modified root volume
            settings.allow_fv_root = True  #  Allow FileVault on broken seal
            # settings.amfi_status = True  #  Signed bundles, Don't need to explicitly set currently

        custom_cpu_model_value = utilities.get_nvram("revcpuname", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if custom_cpu_model_value is not None:
            # TODO: Fix to not use two separate variables
            settings.custom_cpu_model = 1
            settings.custom_cpu_model_value = custom_cpu_model_value.split("%00")[0]

        if "-v" in (utilities.get_nvram("boot-args") or ""):
            settings.verbose_debug = True

        if utilities.amfi_status() is False:
            settings.amfi_status = False

        if model in ["MacBookPro8,2", "MacBookPro8,3"]:
            # Users disabling TS2 most likely have a faulty dGPU
            # users can override this in settings
            settings.allow_ts2_accel = False

        # Check if running in RecoveryOS
        settings.recovery_status = utilities.check_recovery()

        # Check if model uses T2 SMBIOS, if so see if it needs root patching (determined earlier on via SIP variable)
        # If not, allow SecureBootModel usage, otherwise force VMM patching
        # Needed for macOS Monterey to allow OTA updates
        try:
            spoof_model = generate_smbios.set_smbios_model_spoof(model)
        except:
            # Native Macs (mainly M1s) will error out as they don't know what SMBIOS to spoof to
            # As we don't spoof on native models, we can safely ignore this
            spoof_model = model
        try:
            if smbios_data.smbios_dictionary[spoof_model]["SecureBootModel"] is not None:
                if settings.sip_status is False:
                    # Force VMM as root patching breaks .im4m signature
                    settings.secure_status = False
                    settings.force_vmm = True
                else:
                    # Allow SecureBootModel
                    settings.secure_status = True
                    settings.force_vmm = False
        except KeyError:
            pass
