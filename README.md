# OpenCore Legacy Patcher

## Supported SMBIOS

```
MacBook5,1
MacBook5,2
MacBook6,1
MacBook7,1

MacBookAir2,1
MacBookAir3,1
MacBookAir3,2
MacBookAir4,1
MacBookAir4,2
MacBookAir5,1
MacBookAir5,2

MacBookPro3,1
MacBookPro4,1
MacBookPro5,1
MacBookPro5,2
MacBookPro5,3
MacBookPro5,4
MacBookPro5,5
MacBookPro6,1
MacBookPro6,2
MacBookPro7,1
MacBookPro8,1
MacBookPro8,2
MacBookPro8,3
MacBookPro9,1
MacBookPro9,2
MacBookPro10,1
MacBookPro10,2

Macmini3,1
Macmini4,1
Macmini5,1
Macmini5,2
Macmini5,3
Macmini6,1
Macmini6,2

iMac7,1
iMac8,1
iMac9,1
iMac10,1
iMac11,1
iMac11,2
iMac11,3
iMac12,1
iMac12,2
iMac13,1
iMac13,2
iMac14,1
iMac14,2
iMac14,3

MacPro3,1
MacPro4,1
MacPro5,1

Xserve3,1
```


## Hardware Patches

#### MacBook

```
MacBook5,1
MacBook5,2
	Wifi Patch - BCM4322
	AppleHDA Patch
	SSE4.1 Patch
	Ethernet Patch - Nvidia MCP79
	GPU Patch
MacBook6,1
MacBook7,1
	Wifi Patch - BCM43224
	AppleHDA Patch
	SSE4.1 Patch
	Ethernet Patch - Nvidia MCP79
	GPU Patch
```

#### MacBook Air

```
MacBookAir2,1
MacBookAir3,1
MacBookAir3,2
	Wifi Patch - BCM4322
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
MacBookAir4,1
MacBookAir4,2
	Wifi Patch - BCM4322
	AppleHDA Patch
	GPU Patch
MacBookAir5,1
MacBookAir5,2
	Wifi Patch - BCM4322
```

#### MacBook Pro

```
MacBookPro3,1
	Wifi Patch - AR5418
	Ethernet Patch - Marvell
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
MacBookPro4,1
	Wifi Patch - BCM4328
	Ethernet Patch - Marvell
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
MacBookPro5,1
MacBookPro5,2
MacBookPro5,3
MacBookPro5,4
MacBookPro5,5
	Wifi Patch - BCM4322
	Ethernet Patch - Nvidia
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
MacBookPro6,1
MacBookPro6,2
	Wifi Patch - BCM43224
	Ethernet Patch - Broadcom
	AppleHDA Patch
	GPU Patch
MacBookPro7,1
	Wifi Patch - BCM4322
	Ethernet Patch - Nvidia
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
MacBookPro8,1
MacBookPro8,2
MacBookPro8,3
	Wifi Patch - BCM4331
	Ethernet Patch - Broadcom
	AppleHDA Patch
	GPU Patch
MacBookPro9,1
MacBookPro9,2
	Wifi Patch - BCM4331
MacBookPro10,1
MacBookPro10,2
	Wifi Patch - BCM4331
```

#### Mac Mini

```
Macmini3,1
Macmini4,1
	Wifi Patch - BCM43224
	Ethernet Patch - Nvidia
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
Macmini5,1
Macmini5,2
Macmini5,3
	Wifi Patch - BCM4331
	Ethernet Patch - Broadcom
	AppleHDA Patch
	GPU Patch
Macmini6,1
Macmini6,2
	Wifi Patch - BCM4331
```

#### iMac

```
iMac7,1
iMac8,1
	Wifi Patch - BCM4328
	Ethernet Patch - Nvidia
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
iMac9,1
	Wifi Patch - BCM4322
	Ethernet Patch - Nvidia
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
iMac10,1
	Wifi Patch - Atheros
	Ethernet Patch - Nvidia
	AppleHDA Patch
	SSE4.1 Patch
	GPU Patch
iMac11,1
iMac11,2
iMac11,3
	Wifi Patch - Atheros
	Ethernet Patch - Broadcom
	AppleHDA Patch
	GPU Patch
	CPBG SSDT
iMac12,1
iMac12,2
	Wifi Patch - Atheros
	Ethernet Patch - Broadcom
	AppleHDA Patch
	GPU Patch
iMac13,1
iMac13,2
	Wifi Patch - BCM4331
iMac14,1
iMac14,2
iMac14,3
	None
```

#### Mac Pro

```
MacPro3,1
	Wifi Patch - Atheros
	AppleHDA Patch
	SSE4.1 Patch
	AppleMCEReporterDisabler for Dual Socket
MacPro4,1
	Wifi Patch - Atheros
	AppleMCEReporterDisabler for Dual Socket
MacPro5,1
	Wifi patch - BCM4322
	AppleMCEReporterDisabler for Dual Socket
```

#### Xserve

```
Xserve3,1
	AppleMCEReporterDisabler for Dual Socket
	
```