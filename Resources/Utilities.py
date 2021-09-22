# Copyright (C) 2020-2021, Dhinak G
from __future__ import print_function

import hashlib
import math
import os
import plistlib
import subprocess
from pathlib import Path
import re
import os

try:
    import requests
except ImportError:
    subprocess.run(["pip3", "install", "requests"], stdout=subprocess.PIPE)
    try:
        import requests
    except ImportError:
        raise Exception("Missing requests library!\nPlease run the following before starting OCLP:\npip3 install requests")

from Resources import Constants, ioreg, device_probe


def hexswap(input_hex: str):
    hex_pairs = [input_hex[i : i + 2] for i in range(0, len(input_hex), 2)]
    hex_rev = hex_pairs[::-1]
    hex_str = "".join(["".join(x) for x in hex_rev])
    return hex_str.upper()


def process_status(process_result):
    if process_result.returncode != 0:
        print(f"Process failed with exit code {process_result.returncode}")
        print(f"Please file an issue on our Github")
        raise Exception(f"Process result: \n{process_result.stdout.decode()}")


def human_fmt(num):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num) < 1000.0:
            return "%3.1f %s" % (num, unit)
        num /= 1000.0
    return "%.1f %s" % (num, "EB")


def header(lines):
    lines = [i for i in lines if i is not None]
    total_length = len(max(lines, key=len)) + 4
    print("#" * (total_length))
    for line in lines:
        left_side = math.floor(((total_length - 2 - len(line.strip())) / 2))
        print("#" + " " * left_side + line.strip() + " " * (total_length - len("#" + " " * left_side + line.strip()) - 1) + "#")
    print("#" * total_length)


RECOVERY_STATUS = None


def check_recovery():
    global RECOVERY_STATUS  # pylint: disable=global-statement # We need to cache the result

    if RECOVERY_STATUS is None:
        RECOVERY_STATUS = Path("/System/Library/BaseSystem").exists()

    return RECOVERY_STATUS


def get_disk_path():
    root_partition_info = plistlib.loads(subprocess.run("diskutil info -plist /".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
    root_mount_path = root_partition_info["DeviceIdentifier"]
    root_mount_path = root_mount_path[:-2] if root_mount_path.count("s") > 1 else root_mount_path
    return root_mount_path


def check_seal():
    # 'Snapshot Sealed' property is only listed on booted snapshots
    sealed = subprocess.run(["diskutil", "apfs", "list"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if "Snapshot Sealed:           Yes" in sealed.stdout.decode():
        return True
    else:
        return False


def latebloom_detection(model):
    if model in ["MacPro4,1", "MacPro5,1", "iMac7,1", "iMac8,1"]:
        # These machines are more likely to experience boot hangs, increase delays to accomodate
        lb_delay = "250"
    else:
        lb_delay = "100"
    lb_range = "1"
    lb_debug = "1"
    boot_args = get_nvram("boot-args", decode=False)
    # boot_args = "latebloom=200 lb_range=40 lb_debug=0 keepsyms=1 debug=0x100 -lilubetaall"
    if boot_args:
        # TODO: This crashes if latebloom=xxx is the very first entry in boot-args
        if "latebloom=" in boot_args:
            lb_delay = re.search(r"(?:[, ])latebloom=(\d+)", boot_args)
            lb_delay = lb_delay[1]
        if "lb_range=" in boot_args:
            lb_range = re.search(r"(?:[, ])lb_range=(\d+)", boot_args)
            lb_range = lb_range[1]
        if "lb_debug=" in boot_args:
            lb_debug = re.search(r"(?:[, ])lb_debug=(\d+)", boot_args)
            lb_debug = lb_debug[1]
    return int(lb_delay), int(lb_range), int(lb_debug)


def csr_decode(csr_active_config, os_sip):
    if csr_active_config is None:
        csr_active_config = b"\x00\x00\x00\x00"
    sip_int = int.from_bytes(csr_active_config, byteorder="little")
    i = 0
    for current_sip_bit in Constants.Constants.csr_values:
        if sip_int & (1 << i):
            Constants.Constants.csr_values[current_sip_bit] = True
        i = i + 1

    # Can be adjusted to whatever OS needs patching
    sip_needs_change = all(Constants.Constants.csr_values[i] for i in os_sip)
    if sip_needs_change is True:
        return False
    else:
        return True


def friendly_hex(integer: int):
    return "{:02X}".format(integer)


def amfi_status():
    amfi_1 = "amfi_get_out_of_my_way=0x1"
    amfi_2 = "amfi_get_out_of_my_way=1"
    if get_nvram("boot-args", decode=False) and (amfi_1 in get_nvram("boot-args", decode=False) or amfi_2 in get_nvram("boot-args", decode=False)):
        return False
    return True


def check_oclp_boot():
    if get_nvram("OCLP-Version", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True):
        return True
    else:
        return False


def check_monterey_wifi():
    IO80211ElCap = "com.apple.iokit.IO80211ElCap"
    CoreCaptureElCap = "com.apple.driver.corecaptureElCap"
    loaded_kexts: str = subprocess.run("kextcache".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
    if IO80211ElCap in loaded_kexts and CoreCaptureElCap in loaded_kexts:
        return True
    else:
        return False


def check_metal_support(device_probe, computer):
    dgpu = computer.dgpu
    igpu = computer.igpu
    if (
        (dgpu and dgpu.arch in [device_probe.NVIDIA.Archs.Tesla, device_probe.NVIDIA.Archs.Fermi, device_probe.AMD.Archs.TeraScale_1, device_probe.AMD.Archs.TeraScale_2])
        or (igpu and igpu.arch in [device_probe.Intel.Archs.Iron_Lake, device_probe.Intel.Archs.Sandy_Bridge])
        or isinstance(igpu, device_probe.NVIDIA)
    ):
        return False
    else:
        return True

def check_filevault_skip():
    # Check whether we can skip FileVault check with Root Patching
    if get_nvram("OCLP-Settings", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=False) and "-allow_fv" in get_nvram("OCLP-Settings", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=False):
        return True
    else:
        return False

def patching_status(os_sip, os):
    # Detection for Root Patching
    sip_enabled = True  #  System Integrity Protection
    sbm_enabled = True  #  Secure Boot Status (SecureBootModel)
    amfi_enabled = True  # Apple Mobile File Integrity
    fv_enabled = True  #   FileVault
    dosdude_patched = True

    gen6_kext = "/System/Library/Extension/AppleIntelHDGraphics.kext"
    gen7_kext = "/System/Library/Extension/AppleIntelHD3000Graphics.kext"

    if os > Constants.Constants().catalina and not check_oclp_boot():
        # Assume non-OCLP Macs don't patch _cs_require_lv
        amfi_enabled = amfi_status()
    else:
        # Catalina and older supports individually disabling Library Validation
        amfi_enabled = False

    if get_nvram("HardwareModel", "94B73556-2197-4702-82A8-3E1337DAFBFB", decode=False) not in Constants.Constants.sbm_values:
        sbm_enabled = False

    if get_nvram("csr-active-config", decode=False) and csr_decode(get_nvram("csr-active-config", decode=False), os_sip) is False:
        sip_enabled = False

    if os > Constants.Constants().catalina and not check_filevault_skip():
        # Assume non-OCLP Macs do not have our APFS seal patch
        fv_status: str = subprocess.run("fdesetup status".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if "FileVault is Off" in fv_status:
            fv_enabled = False
    else:
        fv_enabled = False

    if not (Path(gen6_kext).exists() and Path(gen7_kext).exists()):
        dosdude_patched = False

    return sip_enabled, sbm_enabled, amfi_enabled, fv_enabled, dosdude_patched


clear = True


def disable_cls():
    global clear
    clear = False


def cls():
    global clear
    if not clear:
        return
    if not check_recovery():
        os.system("cls" if os.name == "nt" else "clear")
    else:
        print("\u001Bc")


def get_nvram(variable: str, uuid: str = None, *, decode: bool = False):
    # TODO: Properly fix for El Capitan, which does not print the XML representation even though we say to

    if uuid is not None:
        uuid += ":"
    else:
        uuid = ""

    nvram = ioreg.IORegistryEntryFromPath(ioreg.kIOMasterPortDefault, "IODeviceTree:/options".encode())

    value = ioreg.IORegistryEntryCreateCFProperty(nvram, f"{uuid}{variable}", ioreg.kCFAllocatorDefault, ioreg.kNilOptions)

    ioreg.IOObjectRelease(nvram)

    if not value:
        return None

    value = ioreg.corefoundation_to_native(value)

    if decode and isinstance(value, bytes):
        value = value.strip(b"\0").decode()
    return value


def download_file(link, location):
    print("- Attempting download from following link:")
    print(link)
    if Path(location).exists():
        print("- Removing old file")
        Path(location).unlink()
    response = requests.get(link, stream=True)
    with location.open("wb") as file:
        count = 0
        for chunk in response.iter_content(1024 * 1024 * 4):
            file.write(chunk)
            count += len(chunk)
            cls()
            print("- Downloading package")
            print(f"- {count / 1024 / 1024}MB Downloaded")
    checksum = hashlib.sha256()
    with location.open("rb") as file:
        chunk = file.read(1024 * 1024 * 16)
        while chunk:
            checksum.update(chunk)
            chunk = file.read(1024 * 1024 * 16)
    return checksum


def enable_apfs(fw_feature, fw_mask):
    fw_feature |= 2 ** 19
    fw_mask |= 2 ** 19
    return fw_feature, fw_mask


# def menu(title, prompt, menu_options, add_quit=True, auto_number=False, in_between=[], top_level=False):
#     return_option = ["Q", "Quit", None] if top_level else ["B", "Back", None]
#     if add_quit: menu_options.append(return_option)

#     cls()
#     header(title)
#     print()

#     for i in in_between: print(i)
#     if in_between: print()

#     for index, option in enumerate(menu_options):
#         if auto_number and not (index == (len(menu_options) - 1) and add_quit):
#             option[0] = str((index + 1))
#         print(option[0] + ".  " + option[1])

#     print()
#     selected = input(prompt)

#     keys = [option[0].upper() for option in menu_options]
#     if not selected or selected.upper() not in keys:
#         return
#     if selected.upper() == return_option[0]:
#         return -1
#     else:
#         menu_options[keys.index(selected.upper())][2]() if menu_options[keys.index(selected.upper())][2] else None


class TUIMenu:
    def __init__(self, title, prompt, options=None, return_number_instead_of_direct_call=False, add_quit=True, auto_number=False, in_between=None, top_level=False, loop=False):
        self.title = title
        self.prompt = prompt
        self.in_between = in_between or []
        self.options = options or []
        self.return_number_instead_of_direct_call = return_number_instead_of_direct_call
        self.auto_number = auto_number
        self.add_quit = add_quit
        self.top_level = top_level
        self.loop = loop
        self.added_quit = False

    def add_menu_option(self, name, description="", function=None, key=""):
        self.options.append([key, name, description, function])

    def start(self):
        return_option = ["Q", "Quit"] if self.top_level else ["B", "Back"]
        if self.add_quit and not self.added_quit:
            self.add_menu_option(return_option[1], function=None, key=return_option[0])
            self.added_quit = True

        while True:
            cls()
            header(self.title)
            print()

            for i in self.in_between:
                print(i)
            if self.in_between:
                print()

            for index, option in enumerate(self.options):
                if self.auto_number and not (index == (len(self.options) - 1) and self.add_quit):
                    option[0] = str((index + 1))
                print(option[0] + ".  " + option[1])
                for i in option[2]:
                    print("\t" + i)

            print()
            selected = input(self.prompt)

            keys = [option[0].upper() for option in self.options]
            if not selected or selected.upper() not in keys:
                if self.loop:
                    continue
                else:
                    return
            if self.add_quit and selected.upper() == return_option[0]:
                return -1
            elif self.return_number_instead_of_direct_call:
                return self.options[keys.index(selected.upper())][0]
            else:
                self.options[keys.index(selected.upper())][3]() if self.options[keys.index(selected.upper())][3] else None
                if not self.loop:
                    return


class TUIOnlyPrint:
    def __init__(self, title, prompt, in_between=None):
        self.title = title
        self.prompt = prompt
        self.in_between = in_between or []

    def start(self):
        cls()
        header(self.title)
        print()

        for i in self.in_between:
            print(i)
        if self.in_between:
            print()

        return input(self.prompt)
