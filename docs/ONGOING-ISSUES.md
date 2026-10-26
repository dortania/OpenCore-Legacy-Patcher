# Ongoing issues with different macOS versions

Here are some longstanding issues with different macOS versions. Make sure to also check the [GitHub issues page](https://github.com/dortania/OpenCore-Legacy-Patcher/issues) for more information.

macOS Ventura and newer

* [USB 1.1 (OHCI/UHCI) Support](#usb-1-1-ohci-uhci-support)
* [Graphics support and issues](#graphics-support-and-issues)
* [AMD Polaris, Vega and Navi support on pre-2019 Mac Pros and pre-2012 iMacs](#amd-polaris-vega-and-navi-support-on-pre-2019-mac-pros-and-pre-2012-imacs)


macOS Sequoia and newer

* [Dual socket CPUs with Mac Pros and Xserve](#dual-socket-cpus-with-mac-pro-2008-and-xserve-2008)
* [T2 Security chip](#t2-security-chip)

---


### USB 1.1 (OHCI/UHCI) Support


For Penryn systems, pre-2013 Mac Pros and Xserve, USB 1.1 support was outright removed in macOS Ventura, therefore this applies all the way to Sequoia.
While USB 1.1 may seem unimportant, it handles many important devices on your system. These include:

* Keyboard and Trackpad for laptops
* IR Receivers
* Bluetooth

Refer to [the troubleshooting page](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOT-HARDWARE.html#keyboard-mouse-and-trackpad-not-working-in-installer-or-after-update) on how to workaround this issue.


### Graphics support and issues


Refer to the following links for more information about Legacy Metal and non-Metal support and their respective issues on different macOS versions.

* [Legacy Metal](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008)
* [Non-Metal](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)


### AMD Polaris, Vega and Navi support on pre-2019 Mac Pros and pre-2012 iMacs


For users with 2008 to 2013 Mac Pros (MacPro3,1-6,1) and 2009 to 2011 iMacs (iMac9,1-12,2), [AVX2.0 support is required in the CPU](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions#Advanced_Vector_Extensions_2) for native graphics acceleration. Thus while your GPU may be natively supported, you cannot run Ventura or newer officially with these GPUs.


* CPUs supporting AVX2.0 are Haswell or newer, which no pre-2019 Mac Pros can be upgraded with.



Currently at this time, OpenCore Legacy Patcher only supports patching the AMD Polaris and Vega Graphics stack to no longer require AVX2.0. We're recently received an AMD RX 6600 donation, so hopefully in the future the project can support AMD Navi with pre-Haswell Macs. However, no time estimates can be given.


Following GPUs are applicable:


| GPU Architecture | Model Families | Supported |
| :--- | :--- | :--- |
| AMD Polaris | RX 4xx/5xx (10/20 series) | <span style="color:#30BCD5"> Supported with patching </span> |
| AMD Vega    | Vega 56/64/VII (10/20 series) | ^^ |
| AMD Navi    | RX 5xxx/6xxx (10/20 series) | <span style="color:red"> Unsupported </span> |



### Dual socket CPUs with Mac Pro 2008 and Xserve 2008


Booting Sequoia on Mac Pro 2008 (MacPro3,1) or Xserve 2008 (Xserve2,1) with more than 4 cores will cause them to panic. OpenCore Legacy Patcher will automatically disable additional cores.

This is due to the dual socket nature of the machine, and likely some firmware/ACPI table incompatibility.

**If building OpenCore for older OS, this limitation can be disabled in Settings -> Build -> "MacPro3,1/Xserve2,1 Workaround".**

::: warning Note

Dual booting Sequoia and older will not be possible with all cores enabled due to reasons described before. In these cases you will be limited to 4 cores.

:::



### T2 security chip

As seen with MacBookAir8,x and macOS Sequoia, T2 machines have panic issues when booting the OS through OpenCorePkg. Although we have made some progress on this issue, panics are still occurring and there is still a significant amount of development work to do before T2 machines may even get to the install screen. We cannot provide any estimate on when T2 machines will be supported.

