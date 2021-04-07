# Platform Plugin Plists

This folder contains many profiles for CPU power management. These plist were originally provided by Apple within IOPlatformPluginFamily's `ACPI_SMC_PlatformPlugin` and `X86PlatformPlugin`, then converted into CPUFriend compatible data via [ResourceConverter.sh](https://github.com/acidanthera/CPUFriend/blob/master/Tools/ResourceConverter.sh).

This allows for all Mac models in this patcher to support the correct power management regardless of the SMBIOS used.

* Note: iMac7,1 and older did not support ACPI_SMC_PlatformPlugin so no CPUFriend support is required
* Note 2: Models dropped in macOS Sierra seem to have throttling issues if CPUFriend with accompanying data is injected. For short term, we've disabled this data injection until resolved.