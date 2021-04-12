# Benefits and Drawbacks between OpenCore Legacy Patcher and other patchers

With OpenCore Legacy Patcher we recommend users go through the below table to understand what the benefits and drawbacks are compared to other patchers. There are positive and negatives to each and we feel transparency is most important when patching another users machine. There should be no grey areas where users may be mislead.

| Features | [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher/) | [Patched Sur](https://github.com/BenSova/Patched-Sur) |
| :--- | :--- | :--- |
| Over The Air Updates | <span style="color:#30BCD5">Native System Preferences, additionally supports Deltas (~2GB) for Metal GPUs</span> | <span style="color:red">Inside Patcher Sur app (~12GB), only available when InstallAssistants release</span> |
| FileVault | <span style="color:#30BCD5">Supported on Metal GPUs</span> | <span style="color:red">Not supported</span> | 
| System Integrity Protection | <span style="color:#30BCD5">Fully enabled on Metal GPUs</span> | <span style="color:red">Disabled for early 2013 and older</span> |
| APFS Snapshots | <span style="color:#30BCD5">Fully enabled</span> | <span style="color:red">Disabled</span> |
| User facing | <span style="color:red">TUI interface</span> | <span style="color:#30BCD5">SwiftUI interface, more user friendly</span> | 
| Supported OSes | <span style="color:#30BCD5">10.7-11</span> | <span style="color:red">10.15-11</span> |
| Firmware Patching | <span style="color:#30BCD5">None required</span> | <span style="color:red">Required for models without native APFS support</span> |
| BootCamp Switching | <span style="color:red">Requires EFI Conversion for Start Disk support, otherwise still supported</span> | <span style="color:#30BCD5">Native</span> |
| Brightness Control on Legacy GPUs | <span style="color:#30BCD5">Supported</span> | <span style="color:#30BCD5">Supported</span> |
| WPA Wifi Support | <span style="color:#30BCD5">Native, stable</span> | <span style="color:red">Unstable</span> |
| Legacy GPU Acceleration | <span style="color:red">Coming soon</span> | <span style="color:red">Coming soon</span> |
| Brightness Control on Legacy GPUs | <span style="color:red">Coming soon</span> | <span style="color:#30BCD5">Supported</span> |
| HEVC/H.265 Support for Mac Pros and iMacs with Polaris+ GPUs | <span style="color:#30BCD5">Supported</span> | <span style="color:red">Not supported</span> |
| Big Sur-styled Boot Picker |  <span style="color:#30BCD5">Available</span> | <span style="color:red">Not available</span> |
| El Capitan-era Wifi cards | <span style="color:#30BCD5">Supported</span> | <span style="color:red">Not supported</span> |
| Hibernation Support | <span style="color:#30BCD5">Supports 3rd party SATA SSDs in addition to stock models</span> | <span style="color:red">Only supports stock drives</span> |