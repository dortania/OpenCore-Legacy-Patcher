# Generate Default Data
from resources import utilities, device_probe
from data import model_array

class generate_defaults():
    def probe(model, host_is_target, settings):
        # Generate Default Data
        # Takes in Settings data set, and returns updated Settings
        settings.sip_status = True
        settings.secure_status = False  # Default false for Monterey
        settings.amfi_status = True

        if host_is_target:
            if utilities.check_metal_support(device_probe, settings.computer) is False:
                settings.disable_cs_lv = True
            if settings.computer.dgpu and settings.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                settings.sip_status = False
                settings.amfi_status = True
                settings.allow_fv_root = True  #  Allow FileVault on broken seal
            if (
                isinstance(settings.computer.wifi, device_probe.Broadcom)
                and settings.computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
            ) or (isinstance(settings.computer.wifi, device_probe.Atheros) and settings.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40):
                settings.sip_status = False
                settings.allow_fv_root = True  #  Allow FileVault on broken seal
        elif model in model_array.LegacyGPU:
            settings.disable_cs_lv = True

        if model in model_array.LegacyGPU:
            if host_is_target and utilities.check_metal_support(device_probe, settings.computer) is True:
                # Building on device and we have a native, supported GPU
                if settings.computer.dgpu and settings.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                    settings.sip_status = False
                    # settings.secure_status = True  # Monterey
                    settings.allow_fv_root = True  #  Allow FileVault on broken seal
                else:
                    settings.sip_status = True
                    # settings.secure_status = True  # Monterey
                    settings.amfi_status = True
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
        

        if model == "MacBook8,1":
            # MacBook8,1 has an odd bug where it cannot install Monterey with Minimal spoofing
            settings.serial_settings = "Moderate"

        custom_cpu_model_value = utilities.get_nvram("revcpuname", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if custom_cpu_model_value is not None:
            # TODO: Fix to not use two separate variables
            settings.custom_cpu_model = 1
            settings.custom_cpu_model_value = custom_cpu_model_value.split("%00")[0]

        if "-v" in (utilities.get_nvram("boot-args") or ""):
            settings.verbose_debug = True

        if utilities.amfi_status() is False:
            settings.amfi_status = False

        if utilities.get_nvram("gpu-power-prefs", "FA4CE28D-B62F-4C99-9CC3-6815686E30F9"):
            # Users disabling TS2 most likely have a faulty dGPU
            # users can override this in settings
            settings.allow_ts2_accel = False

        # Check if running in RecoveryOS
        settings.recovery_status = utilities.check_recovery()