# Copyright (C) 2020-2023, Dhinak G, Mykola Grymalyuk

import argparse
import atexit
import binascii
import logging
import math
import os
import plistlib
import re
import shutil
import subprocess
from pathlib import Path
import py_sip_xnu

from data import os_data, sip_data
from resources import constants, ioreg


def hexswap(input_hex: str):
    hex_pairs = [input_hex[i : i + 2] for i in range(0, len(input_hex), 2)]
    hex_rev = hex_pairs[::-1]
    hex_str = "".join(["".join(x) for x in hex_rev])
    return hex_str.upper()


def string_to_hex(input_string):
    if not (len(input_string) % 2) == 0:
        input_string = "0" + input_string
    input_string = hexswap(input_string)
    input_string = binascii.unhexlify(input_string)
    return input_string


def process_status(process_result):
    if process_result.returncode != 0:
        logging.info(f"Process failed with exit code {process_result.returncode}")
        logging.info(f"Please report the issue on the Discord server")
        raise Exception(f"Process result: \n{process_result.stdout.decode()}")


def human_fmt(num):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num) < 1000.0:
            return "%3.1f %s" % (num, unit)
        num /= 1000.0
    return "%.1f %s" % (num, "EB")


def seconds_to_readable_time(seconds) -> str:
    """
    Convert seconds to a readable time format

    Parameters:
        seconds (int | float | str): Seconds to convert

    Returns:
        str: Readable time format
    """
    seconds = int(seconds)
    time = ""

    if 0 <= seconds < 60:
        return "Less than a minute "
    if seconds < 0:
        return "Indeterminate time "

    years, seconds = divmod(seconds, 31536000)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if years > 0:
        return "Over a year"
    if days > 0:
        if days > 31:
            return "Over a month"
        time += f"{days}d "
    if hours > 0:
        time += f"{hours}h "
    if minutes > 0:
        time += f"{minutes}m "
    #if seconds > 0:
    #    time += f"{seconds}s"
    return time


def header(lines):
    lines = [i for i in lines if i is not None]
    total_length = len(max(lines, key=len)) + 4
    logging.info("#" * (total_length))
    for line in lines:
        left_side = math.floor(((total_length - 2 - len(line.strip())) / 2))
        logging.info("#" + " " * left_side + line.strip() + " " * (total_length - len("#" + " " * left_side + line.strip()) - 1) + "#")
    logging.info("#" * total_length)


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

def check_if_root_is_apfs_snapshot():
    root_partition_info = plistlib.loads(subprocess.run("diskutil info -plist /".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
    try:
        is_snapshotted = root_partition_info["APFSSnapshot"]
    except KeyError:
        is_snapshotted = False
    return is_snapshotted


def check_seal():
    # 'Snapshot Sealed' property is only listed on booted snapshots
    sealed = subprocess.run(["diskutil", "apfs", "list"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if "Snapshot Sealed:           Yes" in sealed.stdout.decode():
        return True
    else:
        return False

def check_filesystem_type():
    # Expected to return 'apfs' or 'hfs'
    filesystem_type = plistlib.loads(subprocess.run(["diskutil", "info", "-plist", "/"], stdout=subprocess.PIPE).stdout.decode().strip().encode())
    return filesystem_type["FilesystemType"]


def csr_decode(os_sip):
    sip_int = py_sip_xnu.SipXnu().get_sip_status().value
    for i,  current_sip_bit in enumerate(sip_data.system_integrity_protection.csr_values):
        if sip_int & (1 << i):
            sip_data.system_integrity_protection.csr_values[current_sip_bit] = True

    # Can be adjusted to whatever OS needs patching
    sip_needs_change = all(sip_data.system_integrity_protection.csr_values[i] for i in os_sip)
    if sip_needs_change is True:
        return False
    else:
        return True


def friendly_hex(integer: int):
    return "{:02X}".format(integer)

sleep_process = None

def disable_sleep_while_running():
    global sleep_process
    logging.info("Disabling Idle Sleep")
    if sleep_process is None:
        # If sleep_process is active, we'll just keep it running
        sleep_process = subprocess.Popen(["caffeinate", "-d", "-i", "-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Ensures that if we don't properly close the process, 'atexit' will for us
    atexit.register(enable_sleep_after_running)

def enable_sleep_after_running():
    global sleep_process
    if sleep_process:
        logging.info("Re-enabling Idle Sleep")
        sleep_process.kill()
        sleep_process = None


def check_kext_loaded(bundle_id: str) -> str:
    """
    Checks if a kext is loaded

    Parameters:
        bundle_id (str): The bundle ID of the kext to check

    Returns:
        str: The version of the kext if it is loaded, or "" if it is not loaded
    """
    # Name (Version) UUID <Linked Against>
    # no UUID for kextstat
    pattern = re.compile(re.escape(bundle_id) + r"\s+\((?P<version>.+)\)")

    args = ["kextstat", "-l", "-b", bundle_id]

    if Path("/usr/bin/kmutil").exists():
        args = ["kmutil", "showloaded", "--list-only", "--variant-suffix", "release", "--optional-identifier", bundle_id]

    kext_loaded = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if kext_loaded.returncode != 0:
        return ""
    output = kext_loaded.stdout.decode()
    if not output.strip():
        return ""
    match = pattern.search(output)
    if match:
        return match.group("version")
    return ""


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
    if computer.gpus:
        for gpu in computer.gpus:
            if (
                (gpu.arch in [
                    device_probe.NVIDIA.Archs.Tesla,
                    device_probe.NVIDIA.Archs.Fermi,
                    device_probe.NVIDIA.Archs.Maxwell,
                    device_probe.NVIDIA.Archs.Pascal,
                    device_probe.AMD.Archs.TeraScale_1,
                    device_probe.AMD.Archs.TeraScale_2,
                    device_probe.Intel.Archs.Iron_Lake,
                    device_probe.Intel.Archs.Sandy_Bridge
                    ]
                )
            ):
                return False
    return True


def check_filevault_skip():
    # Check whether we can skip FileVault check with Root Patching
    nvram = get_nvram("OCLP-Settings", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
    if nvram:
        if "-allow_fv" in nvram:
            return True
    return False


def check_secure_boot_model():
    sbm_byte = get_nvram("HardwareModel", "94B73556-2197-4702-82A8-3E1337DAFBFB", decode=False)
    if sbm_byte:
        sbm_byte = sbm_byte.replace(b"\x00", b"")
        sbm_string = sbm_byte.decode("utf-8")
        return sbm_string
    return None

def check_ap_security_policy():
    ap_security_policy_byte = get_nvram("AppleSecureBootPolicy", "94B73556-2197-4702-82A8-3E1337DAFBFB", decode=False)
    if ap_security_policy_byte:
        # Supported Apple Secure Boot Policy values:
        #     AppleImg4SbModeDisabled = 0,
        #     AppleImg4SbModeMedium   = 1,
        #     AppleImg4SbModeFull     = 2
        # Ref: https://github.com/acidanthera/OpenCorePkg/blob/f7c1a3d483fa2535b6a62c25a4f04017bfeee09a/Include/Apple/Protocol/AppleImg4Verification.h#L27-L31
        return int.from_bytes(ap_security_policy_byte, byteorder="little")
    return 0

def check_secure_boot_level():
    if check_secure_boot_model() in constants.Constants().sbm_values:
        # OpenCorePkg logic:
        #   - If a T2 Unit is used with ApECID, will return 2
        #   - Either x86legacy or T2 without ApECID, returns 1
        #   - Disabled, returns 0
        # Ref: https://github.com/acidanthera/OpenCorePkg/blob/f7c1a3d483fa2535b6a62c25a4f04017bfeee09a/Library/OcMainLib/OpenCoreUefi.c#L490-L502
        #
        # Genuine Mac logic:
        #   - On genuine non-T2 Macs, they always return 0
        #   - T2 Macs will return based on their Startup Policy (Full(2), Medium(1), Disabled(0))
        # Ref: https://support.apple.com/en-us/HT208198
        if check_ap_security_policy() != 0:
            return True
        else:
            return False
    return False


def patching_status(os_sip, os):
    # Detection for Root Patching
    sip_enabled = True  #  System Integrity Protection
    sbm_enabled = True  #  Secure Boot Status (SecureBootModel)
    fv_enabled = True  #   FileVault
    dosdude_patched = True

    gen6_kext = "/System/Library/Extension/AppleIntelHDGraphics.kext"
    gen7_kext = "/System/Library/Extension/AppleIntelHD3000Graphics.kext"


    sbm_enabled = check_secure_boot_level()

    if os > os_data.os_data.yosemite:
        sip_enabled = csr_decode(os_sip)
    else:
        sip_enabled = False

    if os > os_data.os_data.catalina and not check_filevault_skip():
        # Assume non-OCLP Macs do not have our APFS seal patch
        fv_status: str = subprocess.run("fdesetup status".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if "FileVault is Off" in fv_status:
            fv_enabled = False
    else:
        fv_enabled = False

    if not (Path(gen6_kext).exists() and Path(gen7_kext).exists()):
        dosdude_patched = False

    return sip_enabled, sbm_enabled, fv_enabled, dosdude_patched


clear = True


def disable_cls():
    global clear
    clear = False


def cls():
    global clear
    if not clear:
        return
    if check_cli_args() is None:
        # Our GUI does not support clear screen
        if not check_recovery():
            os.system("cls" if os.name == "nt" else "clear")
        else:
            logging.info("\u001Bc")

def check_command_line_tools():
    # Determine whether Command Line Tools exist
    # xcode-select -p
    xcode_select = subprocess.run("xcode-select -p".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if xcode_select.returncode == 0:
        return True
    else:
        return False

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

    if decode:
        if isinstance(value, bytes):
            try:
                value = value.strip(b"\0").decode()
            except UnicodeDecodeError:
                # Some sceanrios the firmware will throw garbage in
                # ie. iMac12,2 with FireWire boot-path
                value = None
        elif isinstance(value, str):
            value = value.strip("\0")
    return value


def get_rom(variable: str, *, decode: bool = False):
    # TODO: Properly fix for El Capitan, which does not print the XML representation even though we say to

    rom = ioreg.IORegistryEntryFromPath(ioreg.kIOMasterPortDefault, "IODeviceTree:/rom".encode())

    value = ioreg.IORegistryEntryCreateCFProperty(rom, variable, ioreg.kCFAllocatorDefault, ioreg.kNilOptions)

    ioreg.IOObjectRelease(rom)

    if not value:
        return None

    value = ioreg.corefoundation_to_native(value)

    if decode and isinstance(value, bytes):
        value = value.strip(b"\0").decode()
    return value

def get_firmware_vendor(*, decode: bool = False):
    efi = ioreg.IORegistryEntryFromPath(ioreg.kIOMasterPortDefault, "IODeviceTree:/efi".encode())
    value = ioreg.IORegistryEntryCreateCFProperty(efi, "firmware-vendor", ioreg.kCFAllocatorDefault, ioreg.kNilOptions)
    ioreg.IOObjectRelease(efi)

    if not value:
        return None

    value = ioreg.corefoundation_to_native(value)
    if decode:
        if isinstance(value, bytes):
            value = value.strip(b"\0").decode()
        elif isinstance(value, str):
            value = value.strip("\0")
    return value


def find_apfs_physical_volume(device):
    # ex: disk3s1s1
    # return: [disk0s2]
    disk_list = None
    physical_disks = []
    try:
        disk_list = plistlib.loads(subprocess.run(["diskutil", "info", "-plist", device], stdout=subprocess.PIPE).stdout)
    except TypeError:
        pass

    if disk_list:
        try:
            # Note: Fusion Drive Macs return multiple APFSPhysicalStores:
            # APFSPhysicalStores:
            #  - 0:
            #      APFSPhysicalStore: disk0s2
            #  - 1:
            #      APFSPhysicalStore: disk3s2
            for disk in disk_list["APFSPhysicalStores"]:
                physical_disks.append(disk["APFSPhysicalStore"])
        except KeyError:
            pass
    return physical_disks

def clean_device_path(device_path: str):
    # ex:
    #   'PciRoot(0x0)/Pci(0xA,0x0)/Sata(0x0,0x0,0x0)/HD(1,GPT,C0778F23-3765-4C8E-9BFA-D60C839E7D2D,0x28,0x64000)/EFI\OC\OpenCore.efi'
    #   'PciRoot(0x0)/Pci(0x1A,0x7)/USB(0x0,0x0)/USB(0x2,0x0)/HD(2,GPT,4E929909-2074-43BA-9773-61EBC110A670,0x64800,0x38E3000)/EFI\OC\OpenCore.efi'
    #   'PciRoot(0x0)/Pci(0x1A,0x7)/USB(0x0,0x0)/USB(0x1,0x0)/\EFI\OC\OpenCore.efi'
    # return:
    #   'C0778F23-3765-4C8E-9BFA-D60C839E7D2D'
    #   '4E929909-2074-43BA-9773-61EBC110A670'
    #   'None'

    if device_path:
        if not any(partition in device_path for partition in ["GPT", "MBR"]):
            return None
        device_path_array = device_path.split("/")
        # we can always assume [-1] is 'EFI\OC\OpenCore.efi'
        if len(device_path_array) >= 2:
            device_path_stripped = device_path_array[-2]
            device_path_root_array = device_path_stripped.split(",")
            if len(device_path_root_array) > 2:
                return device_path_root_array[2]
    return None


def find_disk_off_uuid(uuid):
    # Find disk by UUID
    disk_list = None
    try:
        disk_list = plistlib.loads(subprocess.run(["diskutil", "info", "-plist", uuid], stdout=subprocess.PIPE).stdout)
    except TypeError:
        pass
    if disk_list:
        try:
            return disk_list["DeviceIdentifier"]
        except KeyError:
            pass
    return None

def get_free_space(disk=None):
    """
    Get free space on disk in bytes

    Parameters:
        disk (str): Path to mounted disk (or folder on disk)

    Returns:
        int: Free space in bytes
    """
    if disk is None:
        disk = "/"

    total, used, free = shutil.disk_usage(disk)
    return free

def grab_mount_point_from_disk(disk):
    data = plistlib.loads(subprocess.run(f"diskutil info -plist {disk}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
    return data["MountPoint"]

def monitor_disk_output(disk):
    # Returns MB written on drive
    output = subprocess.check_output(["iostat", "-Id", disk])
    output = output.decode("utf-8")
    #  Grab second last entry (last is \n)
    output = output.split(" ")
    output = output[-2]
    return output


def get_preboot_uuid() -> str:
    """
    Get the UUID of the Preboot volume
    """
    args = ["ioreg", "-a", "-n", "chosen", "-p", "IODeviceTree", "-r"]
    output = plistlib.loads(subprocess.run(args, stdout=subprocess.PIPE).stdout)
    return output[0]["apfs-preboot-uuid"].strip(b"\0").decode()


def block_os_updaters():
    # Disables any processes that would be likely to mess with
    # the root volume while we're working with it.
    bad_processes = [
        "softwareupdate",
        "SoftwareUpdate",
        "Software Update",
        "MobileSoftwareUpdate",
    ]
    output = subprocess.check_output(["ps", "-ax"])
    lines = output.splitlines()
    for line in lines:
        entry = line.split()
        pid = entry[0].decode()
        current_process = entry[3].decode()
        for bad_process in bad_processes:
            if bad_process in current_process:
                if pid != "":
                    logging.info(f"Killing Process: {pid} - {current_process.split('/')[-1]}")
                    subprocess.run(["kill", "-9", pid])
                    break

def check_boot_mode():
    # Check whether we're in Safe Mode or not
    try:
        sys_plist = plistlib.loads(subprocess.run(["system_profiler", "SPSoftwareDataType"], stdout=subprocess.PIPE).stdout)
        return sys_plist[0]["_items"][0]["boot_mode"]
    except (KeyError, TypeError, plistlib.InvalidFileException):
        return None

def elevated(*args, **kwargs) -> subprocess.CompletedProcess:
    # When running through our GUI, we run as root, however we do not get uid 0
    # Best to assume CLI is running as root
    if os.getuid() == 0 or check_cli_args() is not None:
        return subprocess.run(*args, **kwargs)
    else:
        return subprocess.run(["sudo"] + [args[0][0]] + args[0][1:], **kwargs)


def fetch_staged_update(variant: str = "Update") -> (str, str):
    """
    Check for staged macOS update
    Supported variants:
    - Preflight
    - Update
    """

    os_build   = None
    os_version = None

    update_config = f"/System/Volumes/Update/{variant}.plist"
    if not Path(update_config).exists():
        return (None, None)
    try:
        update_staged = plistlib.load(open(update_config, "rb"))
    except:
        return (None, None)
    if "update-asset-attributes" not in update_staged:
        return (None, None)

    os_build   = update_staged["update-asset-attributes"]["Build"]
    os_version = update_staged["update-asset-attributes"]["OSVersion"]

    return os_version, os_build


def check_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", help="Build OpenCore", action="store_true", required=False)
    parser.add_argument("--verbose", help="Enable verbose boot", action="store_true", required=False)
    parser.add_argument("--debug_oc", help="Enable OpenCore DEBUG", action="store_true", required=False)
    parser.add_argument("--debug_kext", help="Enable kext DEBUG", action="store_true", required=False)
    parser.add_argument("--hide_picker", help="Hide OpenCore picker", action="store_true", required=False)
    parser.add_argument("--disable_sip", help="Disable SIP", action="store_true", required=False)
    parser.add_argument("--disable_smb", help="Disable SecureBootModel", action="store_true", required=False)
    parser.add_argument("--vault", help="Enable OpenCore Vaulting", action="store_true", required=False)
    parser.add_argument("--support_all", help="Allow OpenCore on natively supported Models", action="store_true", required=False)
    parser.add_argument("--firewire", help="Enable FireWire Booting", action="store_true", required=False)
    parser.add_argument("--nvme", help="Enable NVMe Booting", action="store_true", required=False)
    parser.add_argument("--wlan", help="Enable Wake on WLAN support", action="store_true", required=False)
    # parser.add_argument("--disable_amfi", help="Disable AMFI", action="store_true", required=False)
    parser.add_argument("--moderate_smbios", help="Moderate SMBIOS Patching", action="store_true", required=False)
    parser.add_argument("--disable_tb", help="Disable Thunderbolt on 2013-2014 MacBook Pros", action="store_true", required=False)
    parser.add_argument("--force_surplus", help="Force SurPlus in all newer OSes", action="store_true", required=False)

    # Building args requiring value values (ie. --model iMac12,2)
    parser.add_argument("--model", action="store", help="Set custom model", required=False)
    parser.add_argument("--disk", action="store", help="Specifies disk to install to", required=False)
    parser.add_argument("--smbios_spoof", action="store", help="Set SMBIOS patching mode", required=False)

    # sys_patch args
    parser.add_argument("--patch_sys_vol", help="Patches root volume", action="store_true", required=False)
    parser.add_argument("--unpatch_sys_vol", help="Unpatches root volume, EXPERIMENTAL", action="store_true", required=False)
    parser.add_argument("--prepare_for_update", help="Prepares host for macOS update, ex. clean /Library/Extensions", action="store_true", required=False)
    parser.add_argument("--cache_os", help="Caches patcher files (ex. KDKs) for incoming OS in Preflight.plist", action="store_true", required=False)

    # validation args
    parser.add_argument("--validate", help="Runs Validation Tests for CI", action="store_true", required=False)

    # GUI args
    parser.add_argument("--gui_patch", help="Starts GUI in Root Patcher", action="store_true", required=False)
    parser.add_argument("--gui_unpatch", help="Starts GUI in Root Unpatcher", action="store_true", required=False)
    parser.add_argument("--auto_patch", help="Check if patches are needed and prompt user", action="store_true", required=False)
    parser.add_argument("--update_installed", help="Prompt user to finish updating via GUI", action="store_true", required=False)

    args = parser.parse_args()
    if not (
        args.build or
        args.patch_sys_vol or
        args.unpatch_sys_vol or
        args.validate or
        args.auto_patch or
        args.prepare_for_update or
        args.cache_os
    ):
        return None
    else:
        return args
