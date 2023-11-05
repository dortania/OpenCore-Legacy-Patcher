# Supported Models
Any Intel-based Mac listed below can install and make use of OpenCore Legacy Patcher. To check your hardware model, open System Information and look for the `Model Identifier` key.
* This applies even if Apple supports the model natively.
* OpenCore Legacy Patcher does not support PowerPC- or Apple Silicon-based Macs.
* If your model is not listed below, it is not supported by this patcher.

The below tables can be used to reference issues with a particular model, and see which OS would work best on your machine.
* [MacBook](#macbook)
* [MacBook Air](#macbook-air)
* [MacBook Pro](#macbook-pro)
* [Mac mini](#mac-mini)
* [iMac](#imac)
* [Mac Pro](#mac-pro)
* [Xserve](#xserve)

::: details OpenCore Patcher application
The patcher application requires **OS X Yosemite 10.10** or later to run.
* **OS X El Capitan 10.11** or later is required to make installers for macOS Ventura and later.

The patcher is designed to target **macOS Big Sur 11.x to macOS Sonoma 14.x**.
* Other versions may work, albeit in a broken state. No support is provided for any version outside of the above.
:::


### MacBook

| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| MacBook (13-inch, Aluminum, Late 2008) | `MacBook5,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)|
| MacBook (13-inch, Early 2009)<br>MacBook (13-inch, Mid 2009) | `MacBook5,2` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)<br>- Trackpad gestures are partially broken |
| MacBook (13-inch, Late 2009) | `MacBook6,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021) |
| MacBook (13-inch, Mid 2010) | `MacBook7,1` | ^^ |
| MacBook (Retina, 12-inch, Early 2015) | `MacBook8,1` | - [Legacy Metal (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| MacBook (Retina, 12-inch, Early 2016) | `MacBook9,1` | ^^ |
| MacBook (Retina, 12-inch, 2017) | `MacBook10,1` | - Supported by OpenCore Legacy Patcher |

### MacBook Air

| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| MacBook Air (13-inch, Late 2008)<br>MacBook Air (13-inch, Mid 2009) | `MacBookAir2,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)|
| MacBook Air (11-inch, Late 2010) | `MacBookAir3,1` | ^^ |
| MacBook Air (13-inch, Late 2010) | `MacBookAir3,2` | ^^ |
| MacBook Air (11-inch, Mid 2011) | `MacBookAir4,1` | ^^ |
| MacBook Air (13-inch, Mid 2011) | `MacBookAir4,2` | ^^ |
| MacBook Air (11-inch, Mid 2012) | `MacBookAir5,1` | - [Legacy Metal (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| MacBook Air (13-inch, Mid 2012) | `MacBookAir5,2` | ^^ |
| MacBook Air (11-inch, Mid 2013)<br>MacBook Air (11-inch, Early 2014) | `MacBookAir6,1` | ^^ |
| MacBook Air (13-inch, Mid 2013)<br>MacBook Air (13-inch, Early 2014) | `MacBookAir6,2` | ^^ |
| MacBook Air (11-inch, Early 2015) | `MacBookAir7,1` | ^^ |
| MacBook Air (13-inch, Early 2015)<br>MacBook Air (13-inch, 2017) | `MacBookAir7,2` | ^^ |
| MacBook Air (Retina, 13-inch, 2018) | `MacBookAir8,1` | - Supported by Apple |
| MacBook Air (Retina, 13-inch, 2019) | `MacBookAir9,1` | ^^ |
| MacBook Air (Retina, 13-inch, 2020) | `MacBookAir10,1` | ^^ |

### MacBook Pro

| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| MacBook Pro (15-inch, Early 2008)<br>MacBook Pro (17-inch, Early 2008) | `MacBookPro4,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)|
| MacBook Pro (15-inch, Late 2008) | `MacBookPro5,1` | ^^ |
| MacBook Pro (17-inch, Early 2009)<br>MacBook Pro (17-inch, Mid 2009) | `MacBookPro5,2` | ^^ |
| MacBook Pro (15-inch, Mid 2009) | `MacBookPro5,3` | ^^ |
| MacBook Pro (13-inch, Mid 2009) | `MacBookPro5,5` | ^^ |
| MacBook Pro (17-inch, Mid 2010) | `MacBookPro6,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108) |
| MacBook Pro (15-inch, Mid 2010) | `MacBookPro6,2` | ^^ |
| MacBook Pro (13-inch, Mid 2010) | `MacBookPro7,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021) |
| MacBook Pro (13-inch, Early 2011)<br>MacBook Pro (13-inch, Late 2011) | `MacBookPro8,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108) |
| MacBook Pro (15-inch, Early 2011)<br>MacBook Pro (15-inch, Late 2011) | `MacBookPro8,2` | ^^ |
| MacBook Pro (17-inch, Early 2011)<br> | `MacBookPro8,3` | ^^ |
| MacBook Pro (15-inch, Mid 2012) | `MacBookPro9,1` | - [Legacy Metal (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| MacBook Pro (13-inch, Mid 2012) | `MacBookPro9,2` | ^^ |
| MacBook Pro (Retina, 15-inch, Mid 2012)<br>MacBook Pro (Retina, 15-inch, Early 2013) | `MacBookPro10,1` | ^^ |
| MacBook Pro (Retina, 13-inch, Late 2012)<br>MacBook Pro (Retina, 13-inch, Early 2013) | `MacBookPro10,2` | ^^ |
| MacBook Pro (Retina, 13-inch, Late 2013)<br>MacBook Pro (Retina, 13-inch, Mid 2014) | `MacBookPro11,1` | ^^ |
| MacBook Pro (Retina, 15-inch, Late 2013)<br>MacBook Pro (Retina, 15-inch, Mid 2014) | `MacBookPro11,2`<br>`MacBookPro11,3` | ^^ |
| MacBook Pro (Retina, 15-inch, Mid 2015) | `MacBookPro11,4`<br>`MacBookPro11,5` | ^^ |
| MacBook Pro (Retina, 13-inch, Early 2015) | `MacBookPro12,1` | ^^ |
| MacBook Pro (13-inch, 2016, 2 Thunderbolt 3 ports) | `MacBookPro13,1` | ^^ |
| MacBook Pro (13-inch, 2016, 4 Thunderbolt 3 ports) | `MacBookPro13,2` | ^^ |
| MacBook Pro (15-inch, 2016) | `MacBookPro13,3` | ^^ |
| MacBook Pro (13-inch, 2017, 2 Thunderbolt 3 ports) | `MacBookPro14,1` | - Supported by OpenCore Legacy Patcher |
| MacBook Pro (13-inch, 2017, 4 Thunderbolt 3 ports) | `MacBookPro14,2` | ^^ |
| MacBook Pro (15-inch, 2017) | `MacBookPro14,3` | - [Legacy Metal (macOS 14+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| MacBook Pro (13-inch, 2018, 4 Thunderbolt 3 ports)<br>MacBook Pro (13-inch, 2019, 4 Thunderbolt 3 ports) | `MacBookPro15,2` | - Supported by Apple |
| MacBook Pro (15-inch, 2018)<br>MacBook Pro (15-inch, 2019) | `MacBookPro15,1` | ^^ |
| MacBook Pro (13-inch, 2019, 2 Thunderbolt 3 ports) | `MacBookPro15,4` | ^^ |
| MacBook Pro (16-inch, 2019) | `MacBookPro16,1`<br>`MacBookPro16,4` | ^^ |
| MacBook Pro (13-inch, 2020, 4 Thunderbolt 3 ports) | `MacBookPro16,2` | ^^ |
| MacBook Pro (13-inch, 2020, 2 Thunderbolt 3 ports) | `MacBookPro16,3` | ^^ |

### Mac mini

| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| Mac mini (Early 2009) | `Macmini3,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021) |
| Mac mini (Mid 2010) | `Macmini4,1` | ^^ |
| Mac mini (Mid 2011) | `Macmini5,1`<br>`Macmini5,2`<br>`Macmini5,3` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108) |
| Mac mini (Late 2012) | `Macmini6,1`<br>`Macmini6,2` | - [Legacy Metal (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| Mac mini (Late 2014) | `Macmini7,1` | ^^ |
| Mac mini (Late 2018) | `Macmini8,1` | - Supported by Apple |

### iMac
| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| iMac (20-inch, Mid 2007)<br>iMac (24-inch, Mid 2007) | `iMac7,1` | - [Requires SSE4.1 CPU](https://lowendmac.com/2018/penryn-t9300-9500-cpu-upgrades-for-the-2007-imac/)<br>- [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)<br>- Remove stock Bluetooth to prevent panics |
| iMac (20-inch, Early 2008)<br>iMac (24-inch, Early 2008) | `iMac8,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021) |
| iMac (20-inch, Early 2009)<br>iMac (24-inch, Early 2009)<br>iMac (20-inch, Mid 2009) | `iMac9,1` | - [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)<br>- [Recommend upgrading to Metal GPU](https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/?post=17425857#post-17425857) |
| iMac (21.5-inch, Late 2009)<br>iMac (27-inch, Late 2009)| `iMac10,1` | ^^ |
| iMac (27-inch, Late 2009) | `iMac11,1` | ^^ |
| iMac (21.5-inch, Mid 2010) | `iMac11,2` | ^^ |
| iMac (27-inch, Mid 2010) | `iMac11,3` | ^^ |
| iMac (21.5-inch, Mid 2011)<br>iMac (21.5-inch, Late 2011) | `iMac12,1` | ^^ |
| iMac (27-inch, Mid 2011) | `iMac12,2` | ^^ |
| iMac (21.5-inch, Late 2012) | `iMac13,1` | - [Legacy Metal (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| iMac (27-inch, Late 2012) | `iMac13,2` | ^^ |
| iMac (21.5-inch, Early 2013) | `iMac13,3` | ^^ |
| iMac (21.5-inch, Late 2013) | `iMac14,1` | ^^ |
| iMac (27-inch, Late 2013) | `iMac14,2`<br>`iMac14,3` | ^^ |
| iMac (21.5-inch, Mid 2014) | `iMac14,4` | ^^ |
| iMac (Retina 5K, 27-inch, Late 2014)<br>iMac (Retina 5K, 27-inch, Mid 2015) | `iMac15,1` | ^^ |
| iMac (21.5-inch, Late 2015) | `iMac16,1` | ^^ |
| iMac (Retina 4K, 21.5-inch, Late 2015) | `iMac16,2` | ^^ |
| iMac (Retina 5K, 27-inch, Late 2015) | `iMac17,1` | ^^ |
| iMac (21.5-inch, 2017) | `iMac18,1` | - Supported by OpenCore Legacy Patcher |
| iMac (Retina 4K, 21.5-inch, 2017) | `iMac18,2` | ^^ |
| iMac (Retina 5K, 27-inch, 2017) | `iMac18,3` | ^^ |
| iMac (Retina 5K, 27-inch, 2019) | `iMac19,1` | - Supported by Apple |
| iMac (Retina 4K, 21.5-inch, 2019) | `iMac19,2` | ^^ |
| iMac (Retina 5K, 27-inch, 2020) | `iMac20,1`<br>`iMac20,2` | ^^ |
| iMac Pro (2017) | `iMacPro1,1` | ^^ |

### Mac Pro

| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| Mac Pro (Early 2008) | `MacPro3,1` | -  [Recommend upgrade to Metal GPU](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008)<br>- [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)<br>- Remove stock Bluetooth to prevent panics |
| Mac Pro (Early 2009) | `MacPro4,1` | - [Recommend upgrade to Metal GPU](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008)<br>- [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021) |
| Mac Pro (Mid 2010)<br>Mac Pro (Mid 2012) | `MacPro5,1` | ^^ |
| Mac Pro (Late 2013) | `MacPro6,1` | - [Legacy Metal (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) |
| Mac Pro (2019) | `MacPro7,1` | - Supported by Apple |

### Xserve

| Model Name | Identifier | Tagged Issues |
| :--- | :--- | :--- |
| Xserve (Early 2008) | `Xserve2,1` | - Recommend upgrade to Metal GPU<br>- [non-Metal GPU (macOS 11+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)<br>- [USB 1.1 (macOS 13+)](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)
| Xserve (Early 2009) | `Xserve3,1` | ^^ |

# Once you've verified your hardware is supported, head to [Download and build macOS Installers](./INSTALLER.md)
