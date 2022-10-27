# Supported Models

Any hardware supporting SSE4.1 CPU and 64-Bit firmware work on this patcher. To check your hardware model, run the following command on the applicable machine in the terminal:

```bash
system_profiler SPHardwareDataType | grep 'Model Identifier'
```

The below table will list all supported and unsupported functions of the patcher currently:

* [MacBook](#macbook)
* [MacBook Air](#macbook-air)
* [MacBook Pro](#macbook-pro)
* [Mac mini](#mac-mini)
* [iMac](#imac)
* [Mac Pro](#mac-pro)
* [Xserve](#xserve)

Regarding OS support, see below:

* Machines listing `YES - Monterey and older` means they cannot run macOS Ventura at this time. Machines with only `YES` can run all of the supported macOS versions offered by OpenCore Legacy Patcher.

| Support Entry | Supported OSes | Description | Comment |
| :--- | :--- | :--- | :--- |
| HostOS | macOS 10.9 - macOS 13 | Refers to OSes where running OpenCore-Patcher.app are supported | Supports 10.7+ if [Python 3.9 or higher](https://www.python.org/downloads/) is manually installed, simply run the `OpenCore-Patcher.command` located in the repo |
| TargetOS | macOS 11 - macOS 13 | Refers to OSes that can be patched to run with OpenCore | May support 10.4 and newer (in a potentially broken state). No support provided. |

### MacBook

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| MacBook1,1 | Mid-2006 | <span style="color:red"> NO </span>  | 32-Bit CPU limitation |
| MacBook2,1 | Late 2006 | ^^ | 32-Bit Firmware limitation |
| MacBook3,1 | Late 2007 | ^^ | ^^ |
| MacBook4,1 | Early 2008 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - No GPU Acceleration in Mavericks and newer<br/>- No Keyboard and Trackpad<br/>- No USB |
| MacBook5,1 | Late 2008 | ^^ | - GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108))<br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md))|
| MacBook5,2 | Early 2009 | ^^ | ^^ |
| MacBook6,1 | Late 2009 | ^^ | ^^ |
| MacBook7,1 | Mid-2010 | ^^ | ^^ |
| MacBook8,1 | Mid-2015 | <span style="color:#30BCD5"> YES </span> | <span style="color:green"> Everything is supported</span> |
| MacBook9,1 | Early 2016 | ^^ | ^^ |

### MacBook Air

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| MacBookAir1,1 | Early 2008 | <span style="color:red"> NO </span> | Requires SSE4.1 CPU |
| MacBookAir2,1 | Late 2008 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108))<br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md))|
| MacBookAir3,1 | Late 2010 | ^^ | ^^ |
| MacBookAir3,2 | ^^ | ^^ | ^^ |
| MacBookAir4,1 | Mid-2011 | ^^ | ^^ |
| MacBookAir4,2 | ^^ | ^^ | ^^ |
| MacBookAir5,1 | Mid-2012 | <span style="color:#30BCD5"> YES </span> | <span style="color:green"> Everything is supported</span> |
| MacBookAir5,2 | ^^ | ^^ | ^^ |
| MacBookAir6,1 | Mid-2013, Early 2014 | ^^ | ^^ |
| MacBookAir6,2 | ^^ | ^^ | ^^ |
| MacBookAir7,1 | Early-2015, 2017 | ^^ | ^^ |
| MacBookAir7,2 | ^^ | ^^ | ^^ |

### MacBook Pro

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| MacBookPro1,1 | Early 2006 | <span style="color:red"> NO </span>  | 32-Bit CPU limitation |
| MacBookPro1,2 | ^^ | ^^ | ^^ |
| MacBookPro2,1 | Late 2006 | ^^ | 32-Bit Firmware limitation |
| MacBookPro2,2 | Late 2006 | ^^ | ^^ |
| MacBookPro3,1 | Mid-2007 | ^^ | Requires SSE4.1 CPU |
| MacBookPro4,1 | Early 2008 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108))<br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md))|
| MacBookPro5,1 | Late 2008 | ^^ | ^^ |
| MacBookPro5,2 | Early 2009 | ^^ | ^^ |
| MacBookPro5,3 | Mid-2009 | ^^ | ^^ |
| MacBookPro5,4 | ^^ | ^^ | ^^ |
| MacBookPro5,5 | ^^ | ^^ | ^^ |
| MacBookPro6,1 | Mid-2010 | ^^ | ^^ |
| MacBookPro6,2 | ^^ | ^^ | ^^ |
| MacBookPro7,1 | ^^ | ^^ | ^^ |
| MacBookPro8,1 | Early 2011 | ^^ | ^^ |
| MacBookPro8,2 | ^^ | ^^ | ^^ |
| MacBookPro8,3 | ^^ | ^^ | ^^ |
| MacBookPro9,1 | Mid-2012 | <span style="color:#30BCD5"> YES </span> | <span style="color:green"> Everything is supported</span> |
| MacBookPro9,2 | ^^ | ^^ | ^^ |
| MacBookPro10,1 | Mid-2012, Early 2013 | ^^ | ^^ |
| MacBookPro10,2 | Late 2012, Early 2013 | ^^ | ^^ |
| MacBookPro11,1 | Late 2013, Mid-2014 | ^^ | ^^ |
| MacBookPro11,2 | ^^ | ^^ | ^^ |
| MacBookPro11,3 | ^^ | ^^ | ^^ |
| MacBookPro11,4 | Mid 2015 | ^^ | ^^ |
| MacBookPro11,5 | ^^ | ^^ | ^^ |
| MacBookPro12,1 | Early 2015 | ^^ | ^^ |
| MacBookPro13,1 | Late 2016 | ^^ | ^^ |
| MacBookPro13,2 | ^^ | ^^ | ^^ |
| MacBookPro13,3 | ^^ | ^^ | ^^ |

### Mac mini

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| Macmini1,1 | Early 2006 | <span style="color:red"> NO </span> | 32-Bit CPU limitation |
| Macmini2,1 | Mid-2007 | ^^ | 32-Bit Firmware limitation |
| Macmini3,1 | Early 2009 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)) <br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md)) |
| Macmini4,1 | Mid-2010 | ^^ | ^^ |
| Macmini5,1 | Mid-2011 | ^^ | ^^ |
| Macmini5,2 | ^^ | ^^ | ^^ |
| Macmini5,3 | ^^ | ^^ | ^^ |
| Macmini6,1 | Late 2012 | <span style="color:#30BCD5"> YES </span> | <span style="color:green"> Everything is supported</span> |
| Macmini6,2 | ^^ | ^^ | ^^ |
| Macmini7,1 | Mid-2014 | ^^ | ^^ |

### iMac

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| iMac4,1 | Early 2006 | <span style="color:red"> NO </span> | 32-Bit CPU limitation |
| iMac4,2 | Mid-2006 | ^^ | ^^ |
| iMac5,1 | Late 2006 | ^^ | 32-Bit Firmware limitation |
| iMac5,2 | ^^ | ^^ | ^^ |
| iMac6,1 | ^^ | ^^ | ^^ |
| iMac7,1 | Mid-2007 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - Requires an [SSE4.1 CPU Upgrade](https://lowendmac.com/2018/penryn-t9300-9500-cpu-upgrades-for-the-2007-imac/)<br/>- GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108))<br/>- Stock Bluetooth 2.0 card non-functional<br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md)) |
| iMac8,1 | Early 2008 | ^^ | - GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)))<br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md))|
| iMac9,1 | Early 2009 | ^^ | ^^ |
| iMac10,1 | Late 2009 | ^^ | - GPU is socketed, [recommend upgrading to Metal GPU](https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/?post=17425857#post-17425857) <br/>- GPU Acceleration in Public Beta, see current issues ([#108](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)) <br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md))|
| iMac11,1 | ^^ | ^^ | ^^ |
| iMac11,2 | Mid-2010 | ^^ | ^^ |
| iMac11,3 | ^^ | ^^ | ^^ |
| iMac12,1 | Mid-2011 | ^^ | ^^ |
| iMac12,2 | ^^ | ^^ | ^^ |
| iMac13,1 | Late 2012 | <span style="color:#30BCD5"> YES </span> | <span style="color:green"> Everything is supported</span> |
| iMac13,2 | ^^ | ^^ | ^^ |
| iMac13,3 | ^^ | ^^ | ^^ |
| iMac14,1 | Late 2013 | ^^ | ^^ |
| iMac14,2 | ^^ | ^^ | ^^ |
| iMac14,3 | ^^ | ^^ | ^^ |
| iMac14,4 | Mid-2014 | ^^ | ^^ |
| iMac15,1 | Late 2014, Mid-2015 | ^^ | ^^ |
| iMac16,1 | Late 2014, Mid-2015 | ^^ | ^^ |
| iMac16,2 | Late 2014, Mid-2015 | ^^ | ^^ |
| iMac17,1 | Late 2015, Early-2016 | ^^ | ^^ |

* For iMac10,1 through iMac12,x, we highly recommend users upgrade the GPU to a Metal supported model. See here for more information: [iMac late 2009 to mid-2011 Graphics Card Upgrade Guide](https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/?post=17425857#post-17425857)

### Mac Pro

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| MacPro1,1 | Mid-2006 | <span style="color:red"> NO </span> | 32-Bit Firmware limitation |
| MacPro2,1 | Mid-2007 | ^^ | ^^ |
| MacPro3,1 | Early 2008 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - Potential boot issues with built-in USB 1.1 ports (recommend using a USB 2.0 hub or dedicated USB PCIe controller) <br/>- Potential boot issues with stock Bluetooth card, recommend removing to avoid kernel panics |
| MacPro4,1 | Early 2009 | ^^ | - Everything is supported as long as GPU is Metal capable <br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md)) |
| MacPro5,1 | Mid-2010, Mid-2012 | ^^ | ^^ |
| MacPro6,1 | Late 2013 | ^^ | - CPU Power Management currently unsupported<br/> - No DRM support |

### Xserve

| SMBIOS | Year | Supported | Comment |
| :--- | :--- | :--- | :--- |
| Xserve1,1 | Mid-2006 | <span style="color:red"> NO </span> | 32-Bit Firmware limitation |
| Xserve2,1 | Early 2008 | <span style="color:#30BCD5"> YES - Monterey and older</span> | - Everything is supported as long as GPU is Metal capable <br/> - Supports macOS Monterey and older ([Ventura support in development](./VENTURA-DROP.md))|
| Xserve3,1 | Early 2009 | ^^ | ^^ |

# Once you've verified your hardware is supported, head to [Download and build macOS Installers](./INSTALLER.md)
