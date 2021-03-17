# Framework for mounting and patching macOS root volume
from __future__ import print_function

import binascii
import plistlib
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path
from datetime import date

from Resources import Constants, ModelArray, utilities


class PatchSysVolume:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions

    def find_mount_root_vol(self):
        root_partition_info = plistlib.loads(subprocess.run("diskutil info -plist /".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        self.root_mount_path = root_partition_info["DeviceIdentifier"]
        self.mount_location = "/System/Volumes/Update/mnt1"
        self.mount_extensions = f"{self.mount_location}/System/Library/Extensions"
        self.mount_frameworks = f"{self.mount_location}/System/Library/Frameworks"
        self.mount_lauchd = f"{self.mount_location}/System/Library/LaunchDaemons"
        self.mount_private_frameworks = f"{self.mount_location}/System/Library/PrivateFrameworks"

        if self.root_mount_path.startswith("disk"):
            self.root_mount_path = self.root_mount_path.replace("s1", "", 1)
            print(f"- Found Root Volume at: {self.root_mount_path}")
            if Path(self.mount_extensions).exists():
                print("- Root Volume is already mounted")
                self.patch_root_vol()
            else:
                print("- Mounting drive as writable")
                subprocess.run(f"sudo mount -o nobrowse -t apfs /dev/{self.root_mount_path} {self.mount_location}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                if Path(self.mount_extensions).exists():
                    print("- Sucessfully mounted the Root Volume")
                    self.patch_root_vol()
                else:
                    print("- Failed to mount the Root Volume")
        else:
            print("- Could not find root volume")

    def gpu_accel_patches(self):
        # Remove a *lot* of garbage
        # Remove AMD Drivers
        print("- Deleting unsupported Binaries")
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX4000.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX4000HWServices.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX5000.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX5000HWServices.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX6000.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX6000Framebuffer.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AMDRadeonX6000HWServices.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Remove Intel
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelBDWGraphics.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelBDWGraphicsFramebuffer.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelCFLGraphicsFramebuffer.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelHD4000Graphics.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelHD5000Graphics.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelICLGraphics.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelICLLPGraphicsFramebuffer.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelKBLGraphics.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelKBLGraphicsFramebuffer.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelSKLGraphics.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelSKLGraphicsFramebuffer.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelFramebufferAzul.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelFramebufferCapri.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Paravirtualized GPU
        subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleParavirtGPU.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Nvidia
        subprocess.run(f"sudo rm -R {self.mount_extensions}/GeForce.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Misc
        subprocess.run(f"sudo rm -R {self.mount_extensions}/IOAcceleratorFamily2.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/IOGPUFamily.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_extensions}/IOSurface.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Frameworks
        subprocess.run(f"sudo rm -R {self.mount_frameworks}/CoreDisplay.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_frameworks}/IOSurface.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_frameworks}/OpenGL.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Private Framworks
        subprocess.run(f"sudo rm -R {self.mount_private_frameworks}/GPUSupport.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo rm -R {self.mount_private_frameworks}/SkyLight.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()


        # Now add our trash
        # Kexts
        print("- Adding supported Binaries")
        subprocess.run(f"sudo cp -R {self.constants.geforcega_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforcetesla_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforceteslagl_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforceteslava_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.iosurface_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.nvdanv50haltesla_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.nvdaresmantesla_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforcega_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforcega_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforcega_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforcega_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.geforcega_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Frameworks
        subprocess.run(f"sudo cp -R {self.constants.coredisplay_path} {self.mount_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.iosurface_f_path} {self.mount_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.opengl_path} {self.mount_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # LaunchDaemons
        subprocess.run(f"sudo cp -R {self.constants.hiddhack_path} {self.mount_lauchd}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # PrivateFrameworks
        subprocess.run(f"sudo cp -R {self.constants.gpusupport_path} {self.mount_private_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo cp -R {self.constants.skylight_path} {self.mount_private_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        print("- Disabling NSDefenestratorModeEnabled")
        subprocess.run("defaults write -g NSDefenestratorModeEnabled -bool false".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()


    def patch_root_vol(self):
        print(f"- Detecting patches for {self.model}")
        print("- Creating backup snapshot")
        subprocess.run("tmutil snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Start Patch engine
        if self.model in ModelArray.LegacyAudio:
            print("- Attempting AppleHDA Patch")
            subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleHDA.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            subprocess.run(f"sudo cp -R {self.constants.applehda_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            rebuild_required = True

        if self.model in ModelArray.EthernetBroadcom:
            print("- Attempting AppleBCM5701Ethernet Patch")
            subprocess.run(f"sudo rm -R {self.mount_extensions}/IONetworkingFamily.kext/Contents/PlugIns/AppleBCM5701Ethernet.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            subprocess.run(f"sudo cp -R {self.constants.applebcm_path} {self.mount_extensions}/IONetworkingFamily.kext/Contents/PlugIns/".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            rebuild_required = True

        if self.model in ModelArray.LegacyGPU:
            #print("- Attemping Legacy GPU Patches")
            #TODO: Re-enable when GPU patches are public
            #self.gpu_accel_patches()
            #rebuild_required = True

        if rebuild_required is True:
            self.rebuild_snapshot()

    def rebuild_snapshot(self):
        input("Press [ENTER] to continue with cache rebuild and snapshotting")
        print("- Rebuilding Kernel Cache (This may take some time)")
        subprocess.run(f"sudo kmutil install --volume-root {self.mount_location} --update-all".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        print("- Creating new APFS snapshot")
        subprocess.run(f"sudo bless --folder {self.mount_location}/System/Library/CoreServices --bootefi --create-snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def start_patch(self):
        # Check SIP
        if self.constants.custom_model != None:
            print("Root Patching must be done on target machine!")
        elif self.model in ModelArray.NoRootPatch11:
            print("Root Patching not required for this machine!")
        elif self.model not in ModelArray.SupportedSMBIOS:
            print("Cannot run on this machine!")
        elif self.constants.detected_os < 10.16:
            print(f"Cannot run on this OS: {self.constants.detected_os}")
        else:
            nvram_dump = plistlib.loads(subprocess.run("nvram -x -p".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            try:
                sip_status = nvram_dump["csr-active-config"]
            except KeyError:
                print("- csr-active-config var is missing")
                sip_status = b'\x00\x00\x00\x00'

            smb_model: str = subprocess.run("nvram 94B73556-2197-4702-82A8-3E1337DAFBFB:HardwareModel	".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
            if not smb_model.startswith("nvram: Error getting variable"):
                smb_model = [line.strip().split(":HardwareModel	", 1)[1] for line in smb_model.split("\n") if line.strip().startswith("94B73556-2197-4702-82A8-3E1337DAFBFB:")][0]
                if smb_model.startswith("j137"):
                    smb_status = "Enabled"
                else:
                    smb_status = "Disabled"
            else:
                smb_status = "Disabled"

            if (sip_status == b'\xef\x0f\x00\x00') and (smb_status == "Disabled"):
                print("- Detected SIP is disabled, continuing")
                input("\nPress [ENTER] to continue")
                self.find_mount_root_vol()
                print("- Patching complete")
                print("\nPlease reboot the machine for patches to take effect")
            else:
                print("- SIP and SecureBootModel set incorrectly, unable to patch")
                print("\nPlease disable SIP and SecureBootModel in Patcher Settings")
                print("Then build OpenCore again, reinstall OpenCore to your drive and reboot.")
        input("Press [Enter] to go exit.")