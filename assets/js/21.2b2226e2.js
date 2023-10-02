(window.webpackJsonp=window.webpackJsonp||[]).push([[21],{407:function(e,a,o){e.exports=o.p+"assets/img/macos-monterey.854c5d62.png"},462:function(e,a,o){"use strict";o.r(a);var t=o(25),r=Object(t.a)({},(function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("ContentSlotsDistributor",{attrs:{"slot-key":e.$parent.slotKey}},[t("p",[t("img",{attrs:{src:o(407),alt:""}})]),e._v(" "),t("p",[e._v("With OpenCore Legacy Patcher v0.1.7 and newer, we've implemented beta macOS Monterey support for users. Please note that Apple has dropped a lot of hardware with this release as well as broken many of our previous patch sets. This page will be used to inform users regarding current issues and will be updated as new patch sets are developed and added to our patcher.")]),e._v(" "),t("h2",{attrs:{id:"newly-dropped-hardware"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#newly-dropped-hardware"}},[e._v("#")]),e._v(" Newly dropped hardware")]),e._v(" "),t("p",[e._v("With Monterey, Apple continues their their somewhat ruthless march of dropping Intel hardware. This release saw the removal, and thus addition into OpenCore Legacy Patcher, of the following models:")]),e._v(" "),t("ul",[t("li",[e._v("iMac14,4")]),e._v(" "),t("li",[e._v("iMac15,1")]),e._v(" "),t("li",[e._v("MacBook8,1")]),e._v(" "),t("li",[e._v("MacBookAir6,1")]),e._v(" "),t("li",[e._v("MacBookAir6,2")]),e._v(" "),t("li",[e._v("MacBookPro11,1")]),e._v(" "),t("li",[e._v("MacBookPro11,2")]),e._v(" "),t("li",[e._v("MacBookPro11,3")])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("Model names")]),e._v(" "),t("ul",[t("li",[e._v("iMac (21.5-inch, Mid 2014)")]),e._v(" "),t("li",[e._v("iMac (Retina 5K, 27-inch, Late 2014)")]),e._v(" "),t("li",[e._v("MacBook (Retina, 12-inch, Early 2015)")]),e._v(" "),t("li",[e._v("MacBook Air (11-inch, Mid 2013)")]),e._v(" "),t("li",[e._v("MacBook Air (13-inch, Mid 2013)")]),e._v(" "),t("li",[e._v("MacBook Air (11-inch, Early 2014)")]),e._v(" "),t("li",[e._v("MacBook Air (13-inch, Early 2014)")]),e._v(" "),t("li",[e._v("MacBook Pro (Retina, 13-inch, Late 2013)")]),e._v(" "),t("li",[e._v("MacBook Pro (Retina, 15-inch, Late 2013)")]),e._v(" "),t("li",[e._v("MacBook Pro (Retina, 13-inch, Mid 2014)")]),e._v(" "),t("li",[e._v("MacBook Pro (Retina, 15-inch, Mid 2014)")])])]),e._v(" "),t("p",[e._v("All of these models now have support in OpenCore Legacy Patcher.")]),e._v(" "),t("h2",{attrs:{id:"current-monterey-issues"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#current-monterey-issues"}},[e._v("#")]),e._v(" Current Monterey Issues")]),e._v(" "),t("h3",{attrs:{id:"macbookpro11-3-booting-issue-without-kepler-acceleration"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#macbookpro11-3-booting-issue-without-kepler-acceleration"}},[e._v("#")]),e._v(" MacBookPro11,3 booting issue without Kepler acceleration")]),e._v(" "),t("p",[e._v("Due to the display being routed through the NVIDIA Kepler card and macOS being rendered on the Intel iGPU, users have been experiencing issues booting without post-install patches applied ("),t("a",{attrs:{href:"https://github.com/dortania/OpenCore-Legacy-Patcher/issues/522",target:"_blank",rel:"noopener noreferrer"}},[e._v("see here for more info"),t("OutboundLink")],1),e._v(".) Currently the only workaround is to install the patches in safe mode, by holding down "),t("code",[e._v("Shift+Enter")]),e._v(" when you select macOS in the OCLP boot picker.")]),e._v(" "),t("h2",{attrs:{id:"previously-broken-hardware"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#previously-broken-hardware"}},[e._v("#")]),e._v(" Previously Broken Hardware")]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("iMac15,1 5K Display Output Issue (Resolved in 0.3.2 and newer)")]),e._v(" "),t("ul",[t("li",[e._v("Documentation:\n"),t("ul",[t("li",[t("a",{attrs:{href:"https://khronokernel.github.io/macos/2021/12/08/5K-UEFI.html",target:"_blank",rel:"noopener noreferrer"}},[e._v("5K iMac and UEFI: Fixing the dreaded output limitation"),t("OutboundLink")],1)])])]),e._v(" "),t("li",[e._v("Associated Github Issue:\n"),t("ul",[t("li",[t("a",{attrs:{href:"https://github.com/dortania/OpenCore-Legacy-Patcher/issues/359",target:"_blank",rel:"noopener noreferrer"}},[e._v('5k Output issues on iMac15,1 (27" 5k iMac - 2014) #359'),t("OutboundLink")],1)])])])])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("macOS 12.0 Beta 4 issue on 2012 to early 2013 machines (Resolved in 0.2.5 and newer)")]),e._v(" "),t("p",[e._v("Currently in macOS 12.0 Beta 4, many Ivy Bridge Macs have experienced Bluetooth issues relating to their BCM20702 chipset. Currently the exact issue is unknown however is assumed to be a bug on Apple's end. Recommend downgrading to macOS 12.0 Beta 3 till resolved:")]),e._v(" "),t("ul",[t("li",[t("a",{attrs:{href:"http://swcdn.apple.com/content/downloads/02/08/071-63739-A_G5RYVW5JHT/dfz5gp3s0jm9vl7m30oewq141zkpv8edr8/InstallAssistant.pkg",target:"_blank",rel:"noopener noreferrer"}},[e._v("12.0 Beta 3 (21A5284e) InstallAssistant (Direct)"),t("OutboundLink")],1)]),e._v(" "),t("li",[t("a",{attrs:{href:"https://archive.org/details/12.0-21a5284e-beta-3",target:"_blank",rel:"noopener noreferrer"}},[e._v("12.0 Beta 3 (21A5284e) InstallAssistant (archive.org)"),t("OutboundLink")],1)])]),e._v(" "),t("p",[e._v("A temporary fix is to restart the BlueTool and bluetoothd process with each boot, note it may not work for all users:")]),e._v(" "),t("div",{staticClass:"language-sh extra-class"},[t("pre",{pre:!0,attrs:{class:"language-sh"}},[t("code",[t("span",{pre:!0,attrs:{class:"token function"}},[e._v("sudo")]),e._v(" "),t("span",{pre:!0,attrs:{class:"token function"}},[e._v("killall")]),e._v(" -9 BlueTool bluetoothd\n")])])])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("Wireless Support Dropped (Resolved in 0.2.5 and newer)")]),e._v(" "),t("ul",[t("li",[e._v("Broadcom BCM94328, BCM94322 and Atheros Wireless Chipsets lost support")])]),e._v(" "),t("p",[e._v("The following models lost Wifi support in macOS Monterey due to their legacy Wireless chipset:")]),e._v(" "),t("ul",[t("li",[e._v("iMac12,x and older")]),e._v(" "),t("li",[e._v("Macmini3,1 and older")]),e._v(" "),t("li",[e._v("MacBook5,x and older")]),e._v(" "),t("li",[e._v("MacBookAir2,1 and older")]),e._v(" "),t("li",[e._v("MacBookPro7,1 and older\n"),t("ul",[t("li",[e._v("MacBookPro6,x is exempt")])])]),e._v(" "),t("li",[e._v("MacPro5,1 and older")])]),e._v(" "),t("p",[e._v("Note: BCM943224, BCM94331, BCM94360 and BCM943602 are still fully supported by OpenCore Legacy Patcher")])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("Bluetooth Support Dropped (Resolved in 0.2.5 and newer)")]),e._v(" "),t("ul",[t("li",[e._v("BRCM2046 and BRCM2070 Bluetooth Chipsets lost support")])]),e._v(" "),t("p",[e._v("The following models lost Bluetooth support in macOS Monterey due to their legacy Bluetooth chipset:")]),e._v(" "),t("ul",[t("li",[e._v("iMac12,x and older")]),e._v(" "),t("li",[e._v("Macmini5,1 and older")]),e._v(" "),t("li",[e._v("MacBook7,1 and older")]),e._v(" "),t("li",[e._v("MacBookAir4,1 and older")]),e._v(" "),t("li",[e._v("MacBookPro8,1 and older")]),e._v(" "),t("li",[e._v("MacPro5,1 and older")])]),e._v(" "),t("p",[e._v("Note: Native BRCM20702 and BRCM20703 are still fully supported by OpenCore Legacy Patcher")]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("Dropped Firmwares")]),e._v(" "),t("p",[e._v("Here are the firmwares macOS Monterey Dropped (previously located within IOBluetoothUSBDFU.kext):")]),e._v(" "),t("ul",[t("li",[e._v("2046_820F.dfu")]),e._v(" "),t("li",[e._v("2046_8210.dfu")]),e._v(" "),t("li",[e._v("2046_8213.dfu")]),e._v(" "),t("li",[e._v("2046_8215.dfu")]),e._v(" "),t("li",[e._v("2046_8216.dfu")]),e._v(" "),t("li",[e._v("2046_8217.dfu")]),e._v(" "),t("li",[e._v("2070_821A.dfu")]),e._v(" "),t("li",[e._v("2070_821B.dfu")]),e._v(" "),t("li",[e._v("2070_8218.dfu")]),e._v(" "),t("li",[e._v("20702_821D.dfu")]),e._v(" "),t("li",[e._v("20702_821F.dfu")]),e._v(" "),t("li",[e._v("20702_828A.dfu")]),e._v(" "),t("li",[e._v("20702_828B.dfu")]),e._v(" "),t("li",[e._v("20702_828C.dfu")]),e._v(" "),t("li",[e._v("20702_8281.dfu")]),e._v(" "),t("li",[e._v("20702_8286.dfu")])])])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("Ivy Bridge iGPU Acceleration (Resolved in 0.1.7 and newer)")]),e._v(" "),t("ul",[t("li",[e._v("Intel HD4000 iGPUs lost support")])]),e._v(" "),t("p",[e._v("By default these machines require root volume patches to gain graphics acceleration in Monterey. OpenCore Legacy Patcher supports readding support however SIP can no longer be enabled due to root patching:")]),e._v(" "),t("ul",[t("li",[e._v("Macmini6,x")]),e._v(" "),t("li",[e._v("MacBookAir5,x")]),e._v(" "),t("li",[e._v("MacBookPro9,x")]),e._v(" "),t("li",[e._v("MacBookPro10,x")])])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("NVIDIA Kepler dGPU Acceleration (Resolved in 0.2.5 and newer)")]),e._v(" "),t("ul",[t("li",[e._v("NVIDIA Kepler dGPUs lost support")])]),e._v(" "),t("p",[e._v("By default these machines require root volume patches to gain graphics acceleration in Monterey. OpenCore Legacy Patcher supports readding support however SIP can no longer be enabled due to root patching:")]),e._v(" "),t("ul",[t("li",[e._v("MacBookPro9,1")]),e._v(" "),t("li",[e._v("MacBookPro10,1")]),e._v(" "),t("li",[e._v("MacBookPro11,3")]),e._v(" "),t("li",[e._v("iMac13,x")]),e._v(" "),t("li",[e._v("iMac14,x")])])]),e._v(" "),t("details",{staticClass:"custom-block details"},[t("summary",[e._v("Non-Metal Acceleration (Resolved in 0.2.5 and newer)")]),e._v(" "),t("ul",[t("li",[e._v("Non-Metal GPUs no longer have working acceleration patches:\n"),t("ul",[t("li",[e._v("Intel Ironlake and Sandy Bridge iGPUs")]),e._v(" "),t("li",[e._v("NVIDIA Tesla and Fermi GPUs")]),e._v(" "),t("li",[e._v("AMD TeraScale 1 and 2 GPUs")])])])]),e._v(" "),t("p",[e._v("The following machines cannot gain graphics acceleration at all in Monterey, only basic framebuffer and brightness control (iMac8,1/9,1 and MacBook5,2 excluded):")]),e._v(" "),t("ul",[t("li",[e._v("iMac12,x and older")]),e._v(" "),t("li",[e._v("Macmini5,x and older")]),e._v(" "),t("li",[e._v("MacBook7,1 and older")]),e._v(" "),t("li",[e._v("MacBookAir4,x and older")]),e._v(" "),t("li",[e._v("MacBookPro8,x and older")])]),e._v(" "),t("p",[e._v("Note: iMac10,1 through iMac12,x can be upgraded with Metal GPUs, "),t("a",{attrs:{href:"https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/",target:"_blank",rel:"noopener noreferrer"}},[e._v("see here for more info"),t("OutboundLink")],1)])])])}),[],!1,null,null,null);a.default=r.exports}}]);