# Copyright (C) 2020-2021, Dhinak G
from __future__ import print_function

import os
import math
from pathlib import Path
import plistlib
import subprocess
import requests
import hashlib
import requests

from Resources import Constants


def hexswap(input_hex: str):
    hex_pairs = [input_hex[i : i + 2] for i in range(0, len(input_hex), 2)]
    hex_rev = hex_pairs[::-1]
    hex_str = "".join(["".join(x) for x in hex_rev])
    return hex_str.upper()


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


def csr_decode(csr_active_config):
    if csr_active_config is None:
        csr_active_config = b"\x00\x00\x00\x00"
    sip_int = int.from_bytes(csr_active_config, byteorder="little")
    i = 0
    for current_sip_bit in Constants.Constants.csr_values:
        if sip_int & (1 << i):
            Constants.Constants.csr_values[current_sip_bit] = True
        i = i + 1

    # Can be adjusted to whatever OS needs patching
    sip_needs_change = all(Constants.Constants.csr_values[i] for i in Constants.Constants.root_patch_sip_big_sur)
    if sip_needs_change is True:
        return False
    else:
        return True


def friendly_hex(integer: int):
    return "{:02X}".format(integer)


def patching_status():
    # Detection for Root Patching
    sip_enabled = True  # System Integrity Protection
    sbm_enabled = True  # Secure Boot Status (SecureBootModel)
    amfi_enabled = True  # Apple Mobile File Integrity
    fv_enabled = True  # FileVault

    amfi_1 = "amfi_get_out_of_my_way=0x1"
    amfi_2 = "amfi_get_out_of_my_way=1"

    if get_nvram("boot-args", decode=False) and amfi_1 in get_nvram("boot-args", decode=False) or amfi_2 in get_nvram("boot-args", decode=False):
        amfi_enabled = False
    if get_nvram("HardwareModel", "94B73556-2197-4702-82A8-3E1337DAFBFB", decode=False) not in Constants.Constants.sbm_values:
        sbm_enabled = False

    if get_nvram("csr-active-config", decode=False) and csr_decode(get_nvram("csr-active-config", decode=False)) is False:
        sip_enabled = False

    fv_status: str = subprocess.run("fdesetup status".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
    if fv_status.startswith("FileVault is Off"):
        fv_enabled = False

    return sip_enabled, sbm_enabled, amfi_enabled, fv_enabled


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
    result = subprocess.run(f"nvram -x {uuid}{variable}".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()
    try:
        value = plistlib.loads(result)[f"{uuid}{variable}"]
    except plistlib.InvalidFileException:
        return None
    if decode:
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
            print(f"- Downloading package")
            print(f"- {count / 1024 / 1024}MB Downloaded")
    checksum = hashlib.sha256()
    with location.open("rb") as file:
        chunk = file.read(1024 * 1024 * 16)
        while chunk:
            checksum.update(chunk)
            chunk = file.read(1024 * 1024 * 16)
    print(f"- Checksum: {checksum.hexdigest()}")


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
