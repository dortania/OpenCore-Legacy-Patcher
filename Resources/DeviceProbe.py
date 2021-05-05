# Probe devices, return device entries
# Copyright (C) 2021 Mykola Grymalyuk
from __future__ import print_function

import binascii
import plistlib
import shutil
import subprocess
import uuid
import os
import sys
import platform
from pathlib import Path

from Resources import Constants, ModelArray, Utilities

class pci_probe:
    def __init__(self):
        self.constants = Constants.Constants()

    def hexswap(self, input_hex: str):
        hex_pairs = [input_hex[i:i + 2] for i in range(0, len(input_hex), 2)]
        hex_rev = hex_pairs[::-1]
        hex_str = "".join(["".join(x) for x in hex_rev])
        return hex_str.upper()

    # Converts given device IDs to DeviceProperty pathing, requires ACPI pathing as DeviceProperties shouldn't be used otherwise
    def deviceproperty_probe(self, vendor_id, device_id):
        gfxutil_output: str = subprocess.run([self.constants.gfxutil_path] + f"-v".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        try:
            #device_path = [line.strip().split("= ", 1)[1] for line in gfxutil_output.split("\n") if f'{vendor_id}:{device_id}'.lower() in line.strip() and f'{acpi_path}' in line.strip()][0]
            device_path = [line.strip().split("= ", 1)[1] for line in gfxutil_output.split("\n") if f'{vendor_id}:{device_id}'.lower() in line.strip()][0]
            return device_path
        except IndexError:
            #print(f"- No DevicePath found for {vendor_id}:{device_id} at {acpi_path}")
            print(f"- No DevicePath found for {vendor_id}:{device_id}")
            return ""

    # Returns the device path of parent controller
    def device_property_parent(self, device_path):
        device_path_parent = "/".join(device_path.split("/")[:-1])
        return device_path_parent

    # GPU probing, note best way to handle is:
    #   vendor,device,acpi_path = gpu_vendor_probe("GFX0")
    #
    # Note gpu_probe should only be used on IGPU and GFX0 entries
    def gpu_probe(self, gpu_type):
        print(f"- Probing IOService for device: {gpu_type}")
        try:
            devices = plistlib.loads(subprocess.run(f"ioreg -r -n {gpu_type} -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            vendor_id = self.hexswap(binascii.hexlify(devices[0]["vendor-id"]).decode()[:4])
            device_id = self.hexswap(binascii.hexlify(devices[0]["device-id"]).decode()[:4])
            try:
                acpi_path = devices[0]["acpi-path"]
                return vendor_id, device_id, acpi_path
            except KeyError:
                print(f"- No ACPI entry found for {gpu_type}")
                return vendor_id, device_id, ""
        except ValueError:
            print(f"- No IOService entry found for {gpu_type}")
            return "", "", ""

    def wifi_probe(self):
        try:
            devices = plistlib.loads(subprocess.run("ioreg -r -n ARPT -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        except ValueError:
            devices = plistlib.loads(subprocess.run("ioreg -c IOPCIDevice -r -d2 -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        try:
            devices = [i for i in devices if i["class-code"] == binascii.unhexlify(self.constants.classcode_wifi)]
            vendor_id = self.hexswap(binascii.hexlify(devices[0]["vendor-id"]).decode()[:4])
            device_id = self.hexswap(binascii.hexlify(devices[0]["device-id"]).decode()[:4])
            ioname = devices[0]["IOName"]
            return vendor_id, device_id, ioname
        except ValueError:
            print(f"- No IOService entry found for Wireless Card")
            return "", "", ""