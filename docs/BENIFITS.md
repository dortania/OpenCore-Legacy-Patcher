# Benefits and Drawbacks between OpenCore Legacy Patcher and other patchers

With OpenCore Legacy Patcher we recommend users go through the below table to understand what the benefits and drawbacks are compared to other patchers. There are positive and negatives to each and we feel transparency is most important when patching another users machine. There should be no grey areas where users may be mislead.

* Note: [Patched Sur](https://github.com/BenSova/Patched-Sur) and [MicropatcherAutomator](https://github.com/moosethegoose2213/automator-for-barrykn-micropatcher) are iterations of [BarryKN's micropatcher](https://github.com/barrykn/big-sur-micropatcher) and therefore share many of the same benefits and limitations. Patched Sur is used for this comparison as it's the most common form of BarryKN's patcher users will find.

| Features | [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher/) | [Patched Sur](https://github.com/BenSova/Patched-Sur) |
| :--- | :--- | :--- |
| Over The Air Updates | <span style="color:#30BCD5">Native System Preferences, additionally supports Deltas (~2GB) for Metal GPUs</span> | <span style="color:red">Inside Patcher Sur app (~12GB), only available when InstallAssistants release.</span> InstallAssistants generally available same day as System Preference updates, however developer betas will lag behind by 1 day compared to OTAs |
| FileVault | <span style="color:#30BCD5">Supported on Metal GPUs</span> | <span style="color:red">Not supported</span> |
| System Integrity Protection | <span style="color:#30BCD5">Fully enabled on Metal GPUs</span> | <span style="color:red">Disabled for early 2013 and older during the patching process and first boot afterwards, otherwise enabled</span> |
| APFS Snapshots | <span style="color:#30BCD5">Fully enabled</span> | <span style="color:red">Disabled</span> |
| User facing | <span style="color:red">TUI interface</span> | <span style="color:#30BCD5">SwiftUI interface, more user friendly</span> |
| Supported OSes | <span style="color:#30BCD5">10.7-11</span> | <span style="color:red">10.15-11</span> |
| Firmware Patching | <span style="color:#30BCD5">None required</span> | <span style="color:red">Required for models without native APFS support</span> |
| BootCamp Switching | <span style="color:red">Requires EFI Conversion for Start Disk support, otherwise still supported</span> | <span style="color:#30BCD5">Native</span> |
| Legacy GPU Acceleration | <span style="color:#30BCD5">In active development</span>, see Acceleration Progress Tracker: [Link](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108) | <span style="color:red">Currently not researching</span> |
| El Capitan-era Wifi cards | <span style="color:#30BCD5">Supported</span> | <span style="colorred">Not supported</span> |
| WPA Wireless Support | <span style="color:#30BCD5">Supported</span> | <span style="color:red">Minority may experience issues on early 2013 and older Models</span> |
| Personal Hotspot Support | <span style="color:#30BCD5">Native</span> | <span style="color:red">Often requires extra steps to achieve on early 2013 and older Models</span> |
| HEVC/H.265 Support for Mac Pros and iMacs with Polaris+ GPUs | <span style="color:#30BCD5">Supported</span> | <span style="color:red">Not supported</span> |
| Big Sur-styled Boot Picker |  <span style="color:#30BCD5">Available</span>, though as a shim to the original boot picker | <span style="color:red">Not available</span> |
| Hibernation Support | <span style="color:#30BCD5">Supports 3rd party SATA SSDs on 2011 and older models in addition to stock drives</span> | <span style="color:red">Only supports stock drives on 2011 and older models</span> |
| Sidecar Support | <span style="color:#30BCD5">Supports any Mac with Metal Intel iGPU</span>, artifacting way exhibited on high movement screen content | <span style="color:red">Not supported at all</span> |
