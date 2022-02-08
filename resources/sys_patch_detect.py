from resources import constants, device_probe, utilities, generate_smbios
from data import model_array, os_data, smbios_data, cpu_data, sip_data

class detect_root_patch:
    def __init__(self, model, versions):
        self.model = model
        self.constants: constants.Constants() = versions
        self.computer = self.constants.computer

        # GPU Patch Detection
        self.nvidia_legacy= False
        self.kepler_gpu= False
        self.amd_ts1= False
        self.amd_ts2= False
        self.iron_gpu= False
        self.sandy_gpu= False
        self.ivy_gpu= False

        # Misc Patch Detection
        self.brightness_legacy= False
        self.legacy_audio= False
        self.legacy_wifi= False
        self.legacy_gmux= False
        self.legacy_keyboard_backlight= False

        # Patch Requirements
        self.amfi_must_disable= False
        self.check_board_id= False
        self.supports_metal= False

        # Validation Checks
        self.sip_enabled = False
        self.sbm_enabled = False
        self.amfi_enabled = False
        self.fv_enabled = False
        self.dosdude_patched = False
        self.bad_board_id = False

    
    def detect_gpus(self):
        gpus = self.constants.computer.gpus
        if self.constants.moj_cat_accel is True:
            non_metal_os = os_data.os_data.high_sierra
        else:
            non_metal_os = os_data.os_data.catalina
        for i, gpu in enumerate(gpus):
            if gpu.class_code and gpu.class_code != 0xFFFFFFFF:
                print(f"- Found GPU ({i}): {utilities.friendly_hex(gpu.vendor_id)}:{utilities.friendly_hex(gpu.device_id)}")
                if gpu.arch in [device_probe.NVIDIA.Archs.Tesla, device_probe.NVIDIA.Archs.Fermi]:
                    if self.constants.detected_os > non_metal_os:
                        self.nvidia_legacy = True
                        self.amfi_must_disable = True
                        self.legacy_keyboard_backlight = self.check_legacy_keyboard_backlight()
                elif gpu.arch == device_probe.NVIDIA.Archs.Kepler:
                    if self.constants.detected_os > os_data.os_data.big_sur:
                        # Kepler drivers were dropped with Beta 7
                        # 12.0 Beta 5: 21.0.0 - 21A5304g
                        # 12.0 Beta 6: 21.1.0 - 21A5506j
                        # 12.0 Beta 7: 21.1.0 - 21A5522h
                        if self.constants.detected_os == os_data.os_data.monterey and self.constants.detected_os_minor > 0:
                            if "21A5506j" not in self.constants.detected_os_build:
                                self.kepler_gpu = True
                                self.supports_metal = True
                elif gpu.arch == device_probe.AMD.Archs.TeraScale_1:
                    if self.constants.detected_os > non_metal_os:
                        self.amd_ts1 = True
                        self.amfi_must_disable = True
                elif gpu.arch == device_probe.AMD.Archs.TeraScale_2:
                    if self.constants.detected_os > non_metal_os:
                        self.amd_ts2 = True
                        self.amfi_must_disable = True
                elif gpu.arch == device_probe.Intel.Archs.Iron_Lake:
                    if self.constants.detected_os > non_metal_os:
                        self.iron_gpu = True
                        self.amfi_must_disable = True
                elif gpu.arch == device_probe.Intel.Archs.Sandy_Bridge:
                    if self.constants.detected_os > non_metal_os:
                        self.sandy_gpu = True
                        self.amfi_must_disable = True
                        self.check_board_id = True
                elif gpu.arch == device_probe.Intel.Archs.Ivy_Bridge:
                    if self.constants.detected_os > os_data.os_data.big_sur:
                        self.ivy_gpu = True
                        self.supports_metal = True
        if self.supports_metal is True:
            # Avoid patching Metal and non-Metal GPUs if both present, prioritize Metal GPU
            # Main concerns are for iMac12,x with Sandy iGPU and Kepler dGPU
            self.nvidia_legacy = False
            self.amd_ts1 = False
            self.amd_ts2 = False
            self.iron_gpu = False
            self.sandy_gpu = False
    
    def check_dgpu_status(self):
        dgpu = self.constants.computer.dgpu
        if dgpu:
            if dgpu.class_code and dgpu.class_code == 0xFFFFFFFF:
                # If dGPU is disabled via class-codes, assume demuxed
                return False
            return True
        return False

    def detect_demux(self):
        # If GFX0 is missing, assume machine was demuxed
        # -wegnoegpu would also trigger this, so ensure arg is not present
        if not "-wegnoegpu" in (utilities.get_nvram("boot-args") or ""):
            igpu = self.constants.computer.igpu
            dgpu = self.check_dgpu_status()
            if igpu and not dgpu:
                return True
        return False
    
    def check_legacy_keyboard_backlight(self):
        # With Big Sur and newer, Skylight patch set unfortunately breaks native keyboard backlight
        # Penryn Macs are able to re-enable the keyboard backlight by simply running '/usr/libexec/TouchBarServer'
        # For Arrendale and newer, this has no effect.
        if self.model.startswith("MacBookPro") or self.model.startswith("MacBookAir"):
            # non-Metal MacBooks never had keyboard backlight
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.penryn.value:
                if self.constants.detected_os > os_data.os_data.catalina:
                    return True
        return False

    def detect_patch_set(self):
        self.detect_gpus()
        if self.model in model_array.LegacyBrightness:
            if self.constants.detected_os > os_data.os_data.catalina:
                self.brightness_legacy = True

        if self.model in ["iMac7,1", "iMac8,1"] or (self.model in model_array.LegacyAudio and utilities.check_kext_loaded("AppleALC", self.constants.detected_os) is False):
            # Special hack for systems with botched GOPs
            # TL;DR: No Boot Screen breaks Lilu, therefore breaking audio
            if self.constants.detected_os > os_data.os_data.catalina:
                self.legacy_audio = True

        if (
            isinstance(self.constants.computer.wifi, device_probe.Broadcom)
            and self.constants.computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
        ) or (isinstance(self.constants.computer.wifi, device_probe.Atheros) and self.constants.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40):
            if self.constants.detected_os > os_data.os_data.big_sur:
                self.legacy_wifi = True

        # if self.model in ["MacBookPro5,1", "MacBookPro5,2", "MacBookPro5,3", "MacBookPro8,2", "MacBookPro8,3"]:
        if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            # Sierra uses a legacy GMUX control method needed for dGPU switching on MacBookPro5,x
            # Same method is also used for demuxed machines
            # Note that MacBookPro5,x machines are extremely unstable with this patch set, so disabled until investigated further
            # Ref: https://github.com/dortania/OpenCore-Legacy-Patcher/files/7360909/KP-b10-030.txt
            if self.constants.detected_os > os_data.os_data.high_sierra:
                if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
                    # Ref: https://doslabelectronics.com/Demux.html
                    if self.detect_demux() is True:
                        self.legacy_gmux = True
                else:
                    self.legacy_gmux = True
        
        self.root_patch_dict = {
            "Graphics: Nvidia Tesla": self.nvidia_legacy,
            "Graphics: Nvidia Kepler": self.kepler_gpu,
            "Graphics: AMD TeraScale 1": self.amd_ts1,
            "Graphics: AMD TeraScale 2": self.amd_ts2,
            "Graphics: Intel Ironlake": self.iron_gpu,
            "Graphics: Intel Sandy Bridge": self.sandy_gpu,
            "Graphics: Intel Ivy Bridge": self.ivy_gpu,
            # "Graphics: Intel Ivy Bridge": True,
            "Brightness: Legacy Backlight Control": self.brightness_legacy,
            "Audio: Legacy Realtek": self.legacy_audio,
            "Networking: Legacy Wireless": self.legacy_wifi,
            "Miscellaneous: Legacy GMUX": self.legacy_gmux,
            "Miscellaneous: Legacy Keyboard Backlight": self.legacy_keyboard_backlight,
            "Settings: Requires AMFI exemption": self.amfi_must_disable,
            "Settings: Requires Board ID validation": self.check_board_id,
            "Validation: Patching Possible": self.verify_patch_allowed(),
            "Validation: SIP is enabled": self.sip_enabled,
            "Validation: SBM is enabled": self.sbm_enabled,
            "Validation: AMFI is enabled": self.amfi_enabled if self.amfi_must_disable else False,
            "Validation: FileVault is enabled": self.fv_enabled,
            "Validation: System is dosdude1 patched": self.dosdude_patched,
            f"Validation: Board ID is unsupported \n({self.computer.reported_board_id})": self.bad_board_id,
        }
        
        return self.root_patch_dict
    
    def verify_patch_allowed(self):
        sip = sip_data.system_integrity_protection.root_patch_sip_big_sur if self.constants.detected_os > os_data.os_data.catalina else sip_data.system_integrity_protection.root_patch_sip_mojave
        self.sip_enabled, self.sbm_enabled, self.amfi_enabled, self.fv_enabled, self.dosdude_patched = utilities.patching_status(sip, self.constants.detected_os)

        if self.check_board_id is True and (self.computer.reported_board_id not in self.constants.sandy_board_id and self.computer.reported_board_id not in self.constants.sandy_board_id_stock):
            self.bad_board_id = True

        if any(
            [self.sip_enabled, self.sbm_enabled, self.fv_enabled, self.dosdude_patched, self.amfi_enabled if self.amfi_must_disable else False, self.bad_board_id if self.check_board_id else False]
        ):
            return False
        else:
            return True