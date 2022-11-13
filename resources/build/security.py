
from resources import constants, utilities
from resources.build import support

import binascii


class build_security:

    def __init__(self, model, versions, config):
        self.model = model
        self.constants: constants.Constants = versions
        self.config = config
        self.computer = self.constants.computer


    def build(self):
        if self.constants.vault is True:
            print("- Setting Vault configuration")
            self.config["Misc"]["Security"]["Vault"] = "Secure"
            support.build_support(self.model, self.constants, self.config).get_efi_binary_by_path("OpenShell.efi", "Misc", "Tools")["Enabled"] = False
        if self.constants.sip_status is False or self.constants.custom_sip_value:
            # Work-around 12.3 bug where Electron apps no longer launch with SIP lowered
            # Unknown whether this is intended behavior or not, revisit with 12.4
            print("- Adding ipc_control_port_options=0 to boot-args")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ipc_control_port_options=0"
            # Adds AutoPkgInstaller for Automatic OpenCore-Patcher installation
            # Only install if running the GUI (AutoPkg-Assets.pkg requires the GUI)
            if self.constants.wxpython_variant is True:
                support.build_support(self.model, self.constants, self.config).enable_kext("AutoPkgInstaller.kext", self.constants.autopkg_version, self.constants.autopkg_path)
            if self.constants.custom_sip_value:
                print(f"- Setting SIP value to: {self.constants.custom_sip_value}")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = utilities.string_to_hex(self.constants.custom_sip_value.lstrip("0x"))
            elif self.constants.sip_status is False:
                print("- Set SIP to allow Root Volume patching")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = binascii.unhexlify("03080000")

            # apfs.kext has an undocumented boot-arg that allows FileVault usage on broken APFS seals (-arv_allow_fv)
            # This is however hidden behind kern.development, thus we patch _apfs_filevault_allowed to always return true
            # Note this function was added in 11.3 (20E232, 20.4), older builds do not support this (ie. 11.2.3)
            print("- Allowing FileVault on Root Patched systems")
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Force FileVault on Broken Seal")["Enabled"] = True
            # Lets us check in sys_patch.py if config supports FileVault
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_fv"

        if self.constants.disable_cs_lv is True:
            print("- Disabling Library Validation")
            # In Ventura, LV patch broke. For now, add AMFI arg
            # Before merging into mainline, this needs to be resolved
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable Library Validation Enforcement")["Enabled"] = True
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable _csr_check() in _vnode_check_signature")["Enabled"] = True
            if self.constants.disable_amfi is True:
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " amfi=0x80"
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_amfi"
            # CSLVFixup simply patches out __RESTRICT and __restrict out of the Music.app Binary
            # Ref: https://pewpewthespells.com/blog/blocking_code_injection_on_ios_and_os_x.html
            support.build_support(self.model, self.constants, self.config).enable_kext("CSLVFixup.kext", self.constants.cslvfixup_version, self.constants.cslvfixup_path)
        if self.constants.secure_status is False:
            print("- Disabling SecureBootModel")
            self.config["Misc"]["Security"]["SecureBootModel"] = "Disabled"
            if self.constants.force_vmm is True:
                print("- Forcing VMM patchset to support OTA updates")
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] = True
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Legacy")["Enabled"] = True
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Ventura")["Enabled"] = True
