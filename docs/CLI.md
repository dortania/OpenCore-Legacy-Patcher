# Command Line Args

With OpenCore Legacy Patcher, we include an extra binary called [OCLP-CLI](https://github.com/dortania/OpenCore-Legacy-Patcher/releases/). The purpose of this binary is to easily run our OpenCore build process for other programs to hook onto. Below is documentation on currently supported arguments.

### Build Arguments

* **--build**: Build OpenCore
  * **--model xxxx**: override default model detection
    * ex. **--model iMac11,2**
  * **--metal_gpu xxxx**: override default GPU detection (ie. Nvidia, AMD)
    * **--metal_gpu Nvidia**
  * **--smbios_spoof xxxx**: set spoofing mode, defaults to Minimal if no arg provided (ie. Minimal, Moderate, Advanced)
    * ex. **--smbios_spoof Moderate**
  * **--verbose**: enable verbose booting
  * **--debug_oc**: enable debug OpenCore
  * **--debug_kext**: enable debug kexts
  * **--skip_wifi**: skip wifi patch
  * **--hide_picker**: hide OpenCore's picker
  * **--disable_sip**: disables SIP
  * **--disable_smb**: disables SecureBootModel
  * **--vault**: enable OpenCore vaulting
  
Example usage:

```bash
./OCLP-CLI --build --verbose --debug_oc --debug_kext --model iMac11,2
```

Note, when building OpenCore the output folder will be next to the OCLP binary as OpenCore-RELEASE or OpenCore-DEBUG folder.

### Patch System Arguments

* **--patch_sys_vol**: patches root volume with detected hardware

Example usage:

```bash
sudo ./OCLP-CLI --patch_sys_vol
```

Note, root volume patching needs to be run as sudo
