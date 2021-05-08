# Lists all models and required patches
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
SupportedSMBIOS = [
    # To be overwritten on program start
]

SupportedSMBIOS11 = [
    # MacBook
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    # MacBook Air
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
    # MacBook Pro
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    # Mac Mini
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
    # iMac
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    # Mac Pro
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    # Xserve
    "Xserve2,1",
    "Xserve3,1",
    "Dortania1,1",
]

SupportedSMBIOS12 = [

]

# CPU patches

MissingSSE42 = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "MacPro3,1",
    "Xserve2,1",
    "Dortania1,1"
]

SSEEmulator = [
    "MacPro3,1",
    "Xserve2,1",
    "Dortania1,1"
]

DualSocket = [
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve2,1",
    "Xserve3,1",
    "Dortania1,1"
]

pciSSDT = [
    "MacBookPro6,1",
    "MacBookPro6,2",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "Dortania1,1"
]

# Ethernet patches

EthernetNvidia = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "Macmini3,1",
    "iMac9,1",
    "iMac10,1",
    "Dortania1,1"
]
EthernetMarvell = [
    "MacBook4,1",
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1",
    "Dortania1,1"
]
EthernetBroadcom = [
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "Dortania1,1"
]

# Wifi patches

WifiAtheros = [
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "MacPro3,1",
    "MacPro4,1",
    "Dortania1,1"
]

WifiBCM94328 = [
    "MacBook4,1",
    "MacBookAir2,1",
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1",
    "Dortania1,1"
]

WifiBCM94322 = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "iMac9,1",
    "MacPro5,1",
    "Dortania1,1"
]

WifiBCM94331 = [
    "MacBook6,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBook7,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookAir4,1",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookAir4,2",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookAir5,1",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookAir5,2",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro6,1",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro6,2",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro8,1",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro8,2",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro8,3",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro9,1",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro9,2",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro10,1",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro10,2",  # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini4,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "Macmini5,1",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini5,2",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini5,3",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini6,1",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini6,2",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "iMac13,1",      # PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)
    "iMac13,2",      # PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)
    "iMac13,3",      # PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)
    "Dortania1,1"
]

# Audio

LegacyAudio = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "MacPro3,1",
    "Dortania1,1"
]

nvidiaHDEF = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac9,1",
    "iMac10,1"
]

# GPU

LegacyGPU = [
    "MacBook4,1",  # GMA X3100
    "MacBook5,1",  # Nvidia 9000
    "MacBook5,2",  # Nvidia 9000
    "MacBook6,1",  # Nvidia 9000
    "MacBook7,1",  # Nvidia 300
    "MacBookAir2,1",  # Nvidia 9000
    "MacBookAir3,1",  # Nvidia 300
    "MacBookAir3,2",  # Nvidia 300
    "MacBookAir4,1",  # Intel 3000
    "MacBookAir4,2",  # Intel 3000
    "MacBookPro4,1",  # Nvidia 8000
    "MacBookPro5,1",  # Nvidia 9000
    "MacBookPro5,2",  # Nvidia 9000
    "MacBookPro5,3",  # Nvidia 9000
    "MacBookPro5,4",  # Nvidia 9000
    "MacBookPro5,5",  # Nvidia 9000
    "MacBookPro6,1",  # Intel 100 + Nvidia 300
    "MacBookPro6,2",  # Intel 100 + Nvidia 300
    "MacBookPro7,1",  # Nvidia 300
    "MacBookPro8,1",  # Intel 3000
    "MacBookPro8,2",  # Intel 3000 + AMD 6000
    "MacBookPro8,3",  # Intel 3000 + AMD 6000
    "Macmini3,1",  # Nvidia 9000
    "Macmini4,1",  # Nvidia 300
    "Macmini5,1",  # Intel 3000
    "Macmini5,2",  # AMD 6000
    "Macmini5,3",  # Intel 3000
    "iMac7,1",  # AMD 2000
    "iMac8,1",  # Nvidia and AMD 2400
    "iMac9,1",  # Nvidia 9000
    "iMac10,1",  # Nvidia 9000 and AMD 4000
    "iMac11,1",  # AMD 4000
    "iMac11,2",  # AMD 4000 and 5000
    "iMac11,3",  # AMD 5000
    "iMac12,1",  # AMD 6000
    "iMac12,2",  # AMD 6000
    "Dortania1,1"  # RTX 3080
]

LegacyGPUNvidia = [
    "MacBook5,1",  # Nvidia 9000
    "MacBook5,2",  # Nvidia 9000
    "MacBook6,1",  # Nvidia 9000
    "MacBook7,1",  # Nvidia 300
    "MacBookAir2,1",  # Nvidia 9000
    "MacBookAir3,1",  # Nvidia 300
    "MacBookAir3,2",  # Nvidia 300
    "MacBookPro4,1",  # Nvidia 8000
    "MacBookPro5,1",  # Nvidia 9000
    "MacBookPro5,2",  # Nvidia 9000
    "MacBookPro5,3",  # Nvidia 9000
    "MacBookPro5,4",  # Nvidia 9000
    "MacBookPro5,5",  # Nvidia 9000
    "MacBookPro6,1",  # Intel 100 + Nvidia 300
    "MacBookPro6,2",  # Intel 100 + Nvidia 300
    "MacBookPro7,1",  # Nvidia 300
    "Macmini3,1",  # Nvidia 9000
    "Macmini4,1",  # Nvidia 300
    "iMac9,1",  # Nvidia 9000
    # "iMac10,1", # Nvidia 9000 and AMD 4000
]

LegacyGPUAMD = [
    "MacBookPro8,2",  # Intel 3000 + AMD 6000
    "MacBookPro8,3",  # Intel 3000 + AMD 6000
    "Macmini5,2",  # AMD 6000
    "iMac7,1",  # AMD 2000
    # "iMac8,1", # Nvidia and AMD 2000
    # "iMac10,1", # Nvidia 9000 and AMD 4000
    "iMac11,1",  # AMD 4000
    "iMac11,2",  # AMD 4000 and 5000
    "iMac11,3",  # AMD 5000
    "iMac12,1",  # AMD 6000
    "iMac12,2",  # AMD 6000
]

LegacyGPUAMDIntelGen2 = [
    "MacBookPro8,2",  # Intel 3000 + AMD 6000
    "MacBookPro8,3",  # Intel 3000 + AMD 6000
    "Macmini5,2",  # AMD 6000
    "iMac12,1",  # AMD 6000
    "iMac12,2",  # AMD 6000
]

LegacyGPUIntelGen1 = [
    "MacBookPro6,1",  # Intel 100 + Nvidia 300
    "MacBookPro6,2",  # Intel 100 + Nvidia 300
]

LegacyGPUIntelGen2 = [
    "MacBookAir4,1",  # Intel 3000
    "MacBookAir4,2",  # Intel 3000
    "MacBookPro8,1",  # Intel 3000
    "MacBookPro8,2",  # Intel 3000 + AMD 6000
    "MacBookPro8,3",  # Intel 3000 + AMD 6000
    "Macmini5,1",  # Intel 3000
    "Macmini5,3",  # Intel 3000
]

LegacyBrightness = [
    "MacBook5,2",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
]

LegacyHID = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "MacPro3,1",
    "Dortania1,1"
]

NVMePatch = [
    "MacPro3,1",
    "MacPro4,1",
    "Xserve3,1",
    "Dortania1,1"
]

SidecarPatch = [
    "MacBook8,1",
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookAir6,1",
    "MacBookAir6,2",
    "MacBookAir7,1",
    "MacBookAir7,2",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    "MacBookPro11,1",
    "MacBookPro11,2",
    "MacBookPro11,3",
    "MacBookPro11,4",
    "MacBookPro11,5",
    "MacBookPro12,1",
    "Macmini6,1",
    "Macmini6,2",
    "Macmini7,1",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "iMac15,1",
    "iMac16,1",
    "iMac16,2",
    "MacPro5,1",
    "MacPro6,1",
    "Dortania1,1"
]

DualGPUPatch = [
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini5,2",
    "iMac12,1",
    "iMac12,2",
    "iMac13,1",
    "iMac13,2",
    "iMac14,2",
    "iMac14,3",
    "Dortania1,1"
]

DualGPUPatchRetina = [
    "MacBookPro10,1",
]

IntelNvidiaDRM = [
    "iMac13,1",
    "iMac13,2",
    "iMac14,2",
    "iMac14,3",
]

HiDPIpicker = [
    "MacBookPro10,1",
    "MacBookPro10,2",
    "Dortania1,1"
]

IDEPatch = [
    "MacBook4,1",
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1",
    "MacPro3,1",
    "Xserve2,1",
    "Dortania1,1"
]

# 11" Air
MacBookAir61 = [
    "MacBookAir3,1",
    "MacBookAir4,1",
    "MacBookAir5,1",
]

# MacBook and 13" Air
MacBookAir62 = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,2",
    "MacBookAir4,2",
    "MacBookAir5,2"
]

# MacBook Pro 13"

MacBookPro111 = [
    "MacBookPro5,5",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro9,2",
    "MacBookPro10,2",
]

# MacBook Pro 15" and 17"

MacBookPro113 = [
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "MacBookPro10,1",
]

# Mac Mini

Macmini71 = [
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2"
]
# iMacPro = dGPU only iMacs
iMacPro11 = [
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
]

# iMac = AMD and Nvidia GPU with iGPU
iMac151 = [
    "iMac13,2",
    "iMac14,2",
    "iMac14,3"
]
# iMac = Intel iGPU
iMac144 = [
    "iMac13,1",
    "iMac14,1"
]

# Mac Pro and Xserve
MacPro71 = [
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve2,1",
    "Xserve3,1",
    "Dortania1,1"
]

XXerve = [
    "Xserve3,1",
]

iXac = [
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
]

XacBookNormal = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
]

XacBookAir = [
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
]

XacBookPro = [
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
]

XacPro = [
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
]

Xacmini = [
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
]

ControllerTypes = [
    "",
    "-EHCI",
    "-EHC1",
    "-EHC2",
    "-XHC1",
    "-OHC1",
    "-OHC2",
    "-InternalHub-EHC1",
    "-InternalHub-EHC1-InternalHub",
    "-InternalHub-EHC2",
    "-InternalHub",
]

upgradableMXMGPUs = [
    "iMac10,1"
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "Xserve3,1",
    "Dortania1,1"
]

# Reference: https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/
NVIDIAMXMGPUs = [
    "0FF6",  # Quadro K1100M
    "0FFB",  # Quadro K2000M
    "0FFC",  # Quadro K1000M
    "1198",  # GTX 880M
    "1199",  # GTX 870M
    "119A",  # GTX 860M
    "119E",  # GTX 780M
    "119F",  # GTX 880M
    "11A9",  # GTX 870M
    "11B6",  # Quadro K3100M
    "11B7",  # Quadro K4100M
    "11B8",  # Quadro K5100M
    "11BC",  # Quadro K5000M
    "11BD",  # Quadro K4000M
    "11BE",  # Quadro K3000M
    "11E1",  # GTX 765M
    "11E2",  # GTX 765M
    "11E0",  # GTX 770M
    "11FC",  # Quadro K2100M
    "12B9",  # Quadro K610M
]

AMDMXMGPUs = [
    "67EF",  # AMD RX 460
    "67E8",  # AMD WX 4130/WX 4150
    "67E0",  # AMD WX 4170
    "67C0",  # AMD WX 7100
    "67DF",  # AMD RX 480
]

BCM4360Wifi = [
    "43BA",  # BCM43602
    "43A3",  # BCM4350
    "43A0",  # BCM4360
]

BCM94331Wifi = [
    "4331",  # BCM94331
    "4353",  # BCM943224
]

BCM94322Wifi = [
    "432B",  # BCM94322
]

BCM94328Wifi = [
    "4311", # BCM4311 - never used by Apple
    "4312", # BCM4311 - never used by Apple
    "4313", # BCM4311 - never used by Apple
    "4318", # BCM4318 - never used by Apple
    "4319", # BCM4318 - never used by Apple
    "431A", # Unknown - never used by Apple
    "4320", # BCM4306 - never used by Apple
    "4324", # BCM4309 - never used by Apple
    "4325", # BCM4306 - never used by Apple
    "4328", # BCM94328
    "432C", # BCM4322 - never used by Apple
    "432D", # BCM4322 - never used by Apple
]

AtherosWifi = [
    "0030", # AR93xx
    "002A", # AR928X
    "001C", # AR242x / AR542x
    "0023", # AR5416 - never used by Apple
    "0024", # AR5418
]

NightShiftExclude = [
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    "Macmini6,1",
    "Macmini6,2",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
]

UGAtoGOP = [
    "MacBook4,1",
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1",
    "MacPro3,1",
    "Xserve2,1",
]

NoSATAPatch = [
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
]

NoAPFSsupport = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBookAir2,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "Macmini3,1",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "MacPro3,1",
    "MacPro4,1",
    "Xserve2,1",
    "Xserve3,1",
    "Dortania1,1"
]

NoRootPatch11 = [
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    "Macmini6,1",
    "Macmini6,2",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve3,1",
]

NoExFat = [
    "MacBook4,1",
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "Macmini3,1",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve2,1",
    "Xserve3,1",
    "Dortania1,1"
]

SandyIGPU = [
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
]

windows_audio = [
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
    "iMac12,1",
    "iMac12,2",
    "iMac13,1",
    "iMac13,2",
    "iMac13,3",
]

DeleteNvidiaAccel11 = [
    "AMDRadeonX4000.kext",
    "AMDRadeonX4000HWServices.kext",
    "AMDRadeonX5000.kext",
    "AMDRadeonX5000HWServices.kext",
    "AMDRadeonX6000.kext",
    "AMDRadeonX6000Framebuffer.kext",
    "AMDRadeonX6000HWServices.kext",
    "AppleIntelBDWGraphics.kext",
    "AppleIntelBDWGraphicsFramebuffer.kext",
    "AppleIntelCFLGraphicsFramebuffer.kext",
    "AppleIntelHD4000Graphics.kext",
    "AppleIntelHD5000Graphics.kext",
    "AppleIntelICLGraphics.kext",
    "AppleIntelICLLPGraphicsFramebuffer.kext",
    "AppleIntelKBLGraphics.kext",
    "AppleIntelKBLGraphicsFramebuffer.kext",
    "AppleIntelSKLGraphics.kext",
    "AppleIntelSKLGraphicsFramebuffer.kext",
    "AppleIntelFramebufferAzul.kext",
    "AppleIntelFramebufferCapri.kext",
    "AppleParavirtGPU.kext",
    "GeForce.kext",
    "IOAcceleratorFamily2.kext",
    "IOGPUFamily.kext",
]

DeleteAMDAccel11 = [
    "AMDRadeonX4000.kext",
    "AMDRadeonX4000HWServices.kext",
    "AMDRadeonX5000.kext",
    "AMDRadeonX5000HWServices.kext",
    "AMDRadeonX6000.kext",
    "AMDRadeonX6000Framebuffer.kext",
    "AMDRadeonX6000HWServices.kext",
    "AMD7000Controller.kext",  # AMDSupport Dependency
    "AMD8000Controller.kext",  # AMDSupport Dependency
    "AMD9000Controller.kext",  # AMDSupport Dependency
    "AMD9500Controller.kext",  # AMDSupport Dependency
    "AMD10000Controller.kext",  # AMDSupport Dependency
    "AppleIntelBDWGraphics.kext",
    "AppleIntelBDWGraphicsFramebuffer.kext",
    "AppleIntelCFLGraphicsFramebuffer.kext",
    "AppleIntelHD4000Graphics.kext",
    "AppleIntelHD5000Graphics.kext",
    "AppleIntelICLGraphics.kext",
    "AppleIntelICLLPGraphicsFramebuffer.kext",
    "AppleIntelKBLGraphics.kext",
    "AppleIntelKBLGraphicsFramebuffer.kext",
    "AppleIntelSKLGraphics.kext",
    "AppleIntelSKLGraphicsFramebuffer.kext",
    "AppleIntelFramebufferAzul.kext",
    "AppleIntelFramebufferCapri.kext",
    "AppleParavirtGPU.kext",
    "GeForce.kext",
    "IOAcceleratorFamily2.kext",
    "IOGPUFamily.kext",
]

AddNvidiaAccel11 = [
    "GeForceGA.bundle",
    "GeForceTesla.kext",
    "GeForceTeslaGLDriver.bundle",
    "GeForceTeslaVADriver.bundle",
    "NVDANV50HalTesla.kext",
    "NVDAResmanTesla.kext",
    "IOSurface.kext",
]

AddNvidiaKeplerAccel11 = [
	"GeForce.kext",
	"GeForceAIRPlugin.bundle",
	"GeForceGLDriver.bundle",
	"GeForceMTLDriver.bundle",
	"GeForceVADriver.bundle",
	"NVDAGF100Hal.kext",
	"NVDAGK100Hal.kext",
	"NVDAResman.kext",
	"NVDAStartup.kext",
	"NVSMU.kext",
]

AddAMDAccel11 = [
    "AMD2400Controller.kext",
    "AMD2600Controller.kext",
    "AMD3800Controller.kext",
    "AMD4600Controller.kext",
    "AMD4800Controller.kext",
    "AMD5000Controller.kext",
    "AMD6000Controller.kext",
    "AMDFramebuffer.kext",
    "AMDLegacyFramebuffer.kext",
    "AMDLegacySupport.kext",
    "AMDRadeonVADriver.bundle",
    "AMDRadeonVADriver2.bundle",
    # "AMDRadeonX3000.kext", # __ZN22IOAccelDisplayMachine210gMetaClassE link issues
    # "AMDRadeonX3000GLDriver.bundle",
    "AMDShared.bundle",
    "AMDSupport.kext",
    "ATIRadeonX2000.kext",
    "ATIRadeonX2000GA.plugin",
    "ATIRadeonX2000GLDriver.bundle",
    "ATIRadeonX2000VADriver.bundle",
    "IOSurface.kext",
]

AddAMDTeraScale2Brightness11 = [
    "AMD5000Controller.kext",
    "AMD6000Controller.kext",
    "AMDLegacyFramebuffer.kext",
    "AMDLegacySupport.kext",
    "AMDRadeonX3000.kext",
    "AMDRadeonX3000GLDriver.bundle",
    "IOAcceleratorFamily2.kext"
]

AddIntelGen1Accel = [
    "AppleIntelHDGraphics.kext",
    "AppleIntelHDGraphicsFB.kext",
    "AppleIntelHDGraphicsGA.plugin",
    "AppleIntelHDGraphicsGLDriver.bundle",
    "AppleIntelHDGraphicsVADriver.bundle",
    "IOSurface.kext",
]

AddIntelGen2Accel = [
    "AppleIntelHD3000Graphics.kext",
    "AppleIntelHD3000GraphicsGA.plugin",
    "AppleIntelHD3000GraphicsGLDriver.bundle",
    "AppleIntelHD3000GraphicsVADriver.bundle",
    "AppleIntelSNBGraphicsFB.kext",
    "AppleIntelSNBVA.bundle",
    "IOSurface.kext",
]

AddIntelGen3Accel = [
	"AppleIntelFramebufferCapri.kext",
	"AppleIntelHD4000Graphics.kext",
	"AppleIntelHD4000GraphicsGLDriver.bundle",
	"AppleIntelHD4000GraphicsMTLDriver.bundle",
	"AppleIntelHD4000GraphicsVADriver.bundle",
]

DeleteBrightness = [
    "AppleGraphicsControl.kext/Contents/PlugIns/AGDCBacklightControl.kext"
]

AddBrightness = [
    "AppleBacklight.kext",
    "AppleBacklightExpert.kext",
]

AddVolumeControl = [
    "IOAudioFamily.kext",
]

# List supported IDs

TeraScale1pciid = [
    "9400",
    "9401",
    "9402",
    "9403",
    "9581",
    "9583",
    "9588",
    "94C8",
    "94C9",
    "9500",
    "9501",
    "9505",
    "9507",
    "9504",
    "9506",
    "9598",
    "9488",
    "9599",
    "9591",
    "9593",
    "9440",
    "9442",
    "944A",
    "945A",
    "9490",
    "949E",
    "9480",
    "9540",
    "9541",
    "954E",
    "954F",
    "9552",
    "9553",
    "94A0",
]

TeraScale2pciid = [
    "6738",
    "6739",
    "6720",
    "6722",
    "6768",
    "6770",
    "6779",
    "6760",
    "6761",
    "68E0",
    "6898",
    "6899",
    "68B8",
    "68B0",
    "68B1",
    "68A0",
    "68A1",
    "6840",
    "6841",
    "68D8",
    "68C0",
    "68C1",
    "68D9",
    "6750",
    "6758",
    "6759",
    "6740",
    "6741",
    "6745",
]

IronLakepciid = [
    "0044",
    "0046",
]

SandyBridgepiciid = [
    "0106",
    "0601",
    "0116",
    "0102",
    "0126",
]

IvyBridgepciid = [
	"0152",
	"0156",
	"0162",
	"0166",
]

# Courteous of envytools:
# https://envytools.readthedocs.io/en/latest/hw/pciid.html
NvidiaTeslapciid = [
    	# G84
	"0400", # G84 [8600 GTS]
	"0401", # G84 [8600 GT]
	"0402", # G84 [8600 GT]
	"0403", # G84 [8600 GS]
	"0404", # G84 [8400 GS]
	"0405", # G84 [9500M GS]
	"0406", # G84 [8300 GS]
	"0407", # G84 [8600M GT]
	"0408", # G84 [9650M GS]
	"0409", # G84 [8700M GT]
	"040A", # G84 [FX 370]
	"040B", # G84 [NVS 320M]
	"040C", # G84 [FX 570M]
	"040D", # G84 [FX 1600M]
	"040E", # G84 [FX 570]
	"040F", # G84 [FX 1700]
	# G86
	"0420", # G86 [8400 SE]
	"0421", # G86 [8500 GT]
	"0422", # G86 [8400 GS]
	"0423", # G86 [8300 GS]
	"0424", # G86 [8400 GS]
	"0425", # G86 [8600M GS]
	"0426", # G86 [8400M GT]
	"0427", # G86 [8400M GS]
	"0428", # G86 [8400M G]
	"0429", # G86 [NVS 140M]
	"042A", # G86 [NVS 130M]
	"042B", # G86 [NVS 135M]
	"042C", # G86 [9400 GT]
	"042D", # G86 [FX 360M]
	"042E", # G86 [9300M G]
	"042F", # G86 [NVS 290]
	# G92
	"0410", # G92 [GT 330]
	"0600", # G92 [8800 GTS 512]
	"0601", # G92 [9800 GT]
	"0602", # G92 [8800 GT]
	"0603", # G92 [GT 230]
	"0604", # G92 [9800 GX2]
	"0605", # G92 [9800 GT]
	"0606", # G92 [8800 GS]
	"0607", # G92 [GTS 240]
	"0608", # G92 [9800M GTX]
	"0609", # G92 [8800M GTS]
	"060A", # G92 [GTX 280M]
	"060B", # G92 [9800M GT]
	"060C", # G92 [8800M GTX]
	"060F", # G92 [GTX 285M]
	"0610", # G92 [9600 GSO]
	"0611", # G92 [8800 GT]
	"0612", # G92 [9800 GTX/9800 GTX+]
	"0613", # G92 [9800 GTX+]
	"0614", # G92 [9800 GT]
	"0615", # G92 [GTS 250]
	"0617", # G92 [9800M GTX]
	"0618", # G92 [GTX 260M]
	"0619", # G92 [FX 4700 X2]
	"061A", # G92 [FX 3700]
	"061B", # G92 [VX 200]
	"061C", # G92 [FX 3600M]
	"061D", # G92 [FX 2800M]
	"061E", # G92 [FX 3700M]
	"061F", # G92 [FX 3800M]
	# G94
	"0621", # G94 [GT 230]
	"0622", # G94 [9600 GT]
	"0623", # G94 [9600 GS]
	"0625", # G94 [9600 GSO 512]
	"0626", # G94 [GT 130]
	"0627", # G94 [GT 140]
	"0628", # G94 [9800M GTS]
	"062A", # G94 [9700M GTS]
	"062B", # G94 [9800M GS]
	"062C", # G94 [9800M GTS ]
	"062D", # G94 [9600 GT]
	"062E", # G94 [9600 GT]
	"0631", # G94 [GTS 160M]
	"0635", # G94 [9600 GSO]
	"0637", # G94 [9600 GT]
	"0638", # G94 [FX 1800]
	"063A", # G94 [FX 2700M]
	# G96
	"0640", # G96 [9500 GT]
	"0641", # G96 [9400 GT]
	"0643", # G96 [9500 GT]
	"0644", # G96 [9500 GS]
	"0645", # G96 [9500 GS]
	"0646", # G96 [GT 120]
	"0647", # G96 [9600M GT]
	"0648", # G96 [9600M GS]
	"0649", # G96 [9600M GT]
	"064A", # G96 [9700M GT]
	"064B", # G96 [9500M G]
	"064C", # G96 [9650M GT]
	"0651", # G96 [G 110M]
	"0652", # G96 [GT 130M]
	"0653", # G96 [GT 120M]
	"0654", # G96 [GT 220M]
	"0655", # G96 [GT 120]
	"0656", # G96 [GT 120 ]
	"0658", # G96 [FX 380]
	"0659", # G96 [FX 580]
	"065A", # G96 [FX 1700M]
	"065B", # G96 [9400 GT]
	"065C", # G96 [FX 770M]
	"065F", # G96 [G210]
	# G98
	"06E0", # G98 [9300 GE]
	"06E1", # G98 [9300 GS]
	"06E2", # G98 [8400]
	"06E3", # G98 [8400 SE]
	"06E4", # G98 [8400 GS]
	"06E6", # G98 [G100]
	"06E7", # G98 [9300 SE]
	"06E8", # G98 [9200M GS]
	"06E9", # G98 [9300M GS]
	"06EA", # G98 [NVS 150M]
	"06EB", # G98 [NVS 160M]
	"06EC", # G98 [G 105M]
	"06EF", # G98 [G 103M]
	"06F1", # G98 [G105M]
	"06F8", # G98 [NVS 420]
	"06F9", # G98 [FX 370 LP]
	"06FA", # G98 [NVS 450]
	"06FB", # G98 [FX 370M]
	"06FD", # G98 [NVS 295]
	"06FF", # G98 [HICx16]
	# G200
	"05E0", # G200 [GTX 295]
	"05E1", # G200 [GTX 280]
	"05E2", # G200 [GTX 260]
	"05E3", # G200 [GTX 285]
	"05E6", # G200 [GTX 275]
	"05E7", # G200 [C1060]
	"05E9", # G200 [CX]
	"05EA", # G200 [GTX 260]
	"05EB", # G200 [GTX 295]
	"05ED", # G200 [FX 5800]
	"05EE", # G200 [FX 4800]
	"05EF", # G200 [FX 3800]
	# MCP77 GPU
	"0840", # MCP77 GPU [8200M]
	"0844", # MCP77 GPU [9100M G]
	"0845", # MCP77 GPU [8200M G]
	"0846", # MCP77 GPU [9200]
	"0847", # MCP77 GPU [9100]
	"0848", # MCP77 GPU [8300]
	"0849", # MCP77 GPU [8200]
	"084A", # MCP77 GPU [730A]
	"084B", # MCP77 GPU [9200]
	"084C", # MCP77 GPU [980A/780A SLI]
	"084D", # MCP77 GPU [750A SLI]
	"084F", # MCP77 GPU [8100 / 720A]
	# MCP79 GPU
	"0860", # MCP79 GPU [9400]
	"0861", # MCP79 GPU [9400]
	"0862", # MCP79 GPU [9400M G]
	"0863", # MCP79 GPU [9400M]
	"0864", # MCP79 GPU [9300]
	"0865", # MCP79 GPU [ION]
	"0866", # MCP79 GPU [9400M G]
	"0867", # MCP79 GPU [9400]
	"0868", # MCP79 GPU [760i SLI]
	"0869", # MCP79 GPU [9400]
	"086A", # MCP79 GPU [9400]
	"086C", # MCP79 GPU [9300 / 730i]
	"086D", # MCP79 GPU [9200]
	"086E", # MCP79 GPU [9100M G]
	"086F", # MCP79 GPU [8200M G]
	"0870", # MCP79 GPU [9400M]
	"0871", # MCP79 GPU [9200]
	"0872", # MCP79 GPU [G102M]
	"0873", # MCP79 GPU [G102M]
	"0874", # MCP79 GPU [ION]
	"0876", # MCP79 GPU [ION]
	"087A", # MCP79 GPU [9400]
	"087D", # MCP79 GPU [ION]
	"087E", # MCP79 GPU [ION LE]
	"087F", # MCP79 GPU [ION LE]
	# GT215
	"0CA0", # GT215 [GT 330]
	"0CA2", # GT215 [GT 320]
	"0CA3", # GT215 [GT 240]
	"0CA4", # GT215 [GT 340]
	"0CA5", # GT215 [GT 220]
	"0CA7", # GT215 [GT 330]
	"0CA9", # GT215 [GTS 250M]
	"0CAC", # GT215 [GT 220]
	"0CAF", # GT215 [GT 335M]
	"0CB0", # GT215 [GTS 350M]
	"0CB1", # GT215 [GTS 360M]
	"0CBC", # GT215 [FX 1800M]
	# GT216
	"0A20", # GT216 [GT 220]
	"0A22", # GT216 [315]
	"0A23", # GT216 [210]
	"0A26", # GT216 [405]
	"0A27", # GT216 [405]
	"0A28", # GT216 [GT 230M]
	"0A29", # GT216 [GT 330M]
	"0A2A", # GT216 [GT 230M]
	"0A2B", # GT216 [GT 330M]
	"0A2C", # GT216 [NVS 5100M]
	"0A2D", # GT216 [GT 320M]
	"0A32", # GT216 [GT 415]
	"0A34", # GT216 [GT 240M]
	"0A35", # GT216 [GT 325M]
	"0A38", # GT216 [400]
	"0A3C", # GT216 [FX 880M]
	# GT218
	"0A60", # GT218 [G210]
	"0A62", # GT218 [205]
	"0A63", # GT218 [310]
	"0A64", # GT218 [ION]
	"0A65", # GT218 [210]
	"0A66", # GT218 [310]
	"0A67", # GT218 [315]
	"0A68", # GT218 [G105M]
	"0A69", # GT218 [G105M]
	"0A6A", # GT218 [NVS 2100M]
	"0A6C", # GT218 [NVS 3100M]
	"0A6E", # GT218 [305M]
	"0A6F", # GT218 [ION]
	"0A70", # GT218 [310M]
	"0A71", # GT218 [305M]
	"0A72", # GT218 [310M]
	"0A73", # GT218 [305M]
	"0A74", # GT218 [G210M]
	"0A75", # GT218 [310M]
	"0A76", # GT218 [ION]
	"0A78", # GT218 [FX 380 LP]
	"0A7A", # GT218 [315M]
	"0A7C", # GT218 [FX 380M]
	"10C0", # GT218 [9300 GS]
	"10C3", # GT218 [8400GS]
	"10C5", # GT218 [405]
	"10D8", # GT218 [NVS 300]
	# MCP89 GPU
	"08A0", # MCP89 GPU [320M]
	"08A2", # MCP89 GPU [320M]
	"08A3", # MCP89 GPU [320M]
	"08A4", # MCP89 GPU [320M]
]

NvidiaFermipciid = [
    	# GF100
	"06C0", # GF100 [GTX 480]
	"06C4", # GF100 [GTX 465]
	"06CA", # GF100 [GTX 480M]
	"06CB", # GF100 [GTX 480]
	"06CD", # GF100 [GTX 470]
	"06D1", # GF100 [C2050 / C2070]
	"06D2", # GF100 [M2070]
	"06D8", # GF100 [6000]
	"06D9", # GF100 [5000]
	"06DA", # GF100 [5000M]
	"06DC", # GF100 [6000]
	"06DD", # GF100 [4000]
	"06DE", # GF100 [T20]
	"06DF", # GF100 [M2070-Q]
	# GF104
	"0E22", # GF104 [GTX 460]
	"0E23", # GF104 [GTX 460 SE]
	"0E24", # GF104 [GTX 460 OEM]
	"0E30", # GF104 [GTX 470M]
	"0E31", # GF104 [GTX 485M]
	"0E3A", # GF104 [3000M]
	"0E3B", # GF104 [4000M]
	# GF114
	"1200", # GF114 [GTX 560 Ti]
	"1201", # GF114 [GTX 560]
	"1202", # GF114 [GTX 560 Ti OEM]
	"1203", # GF114 [GTX 460 SE v2]
	"1205", # GF114 [GTX 460 v2]
	"1206", # GF114 [GTX 555]
	"1207", # GF114 [GT 645 OEM]
	"1208", # GF114 [GTX 560 SE]
	"1210", # GF114 [GTX 570M]
	"1211", # GF114 [GTX 580M]
	"1212", # GF114 [GTX 675M]
	"1213", # GF114 [GTX 670M]
	# GF106
	"0DC0", # GF106 [GT 440]
	"0DC4", # GF106 [GTS 450]
	"0DC5", # GF106 [GTS 450]
	"0DC6", # GF106 [GTS 450]
	"0DCD", # GF106 [GT 555M]
	"0DCE", # GF106 [GT 555M]
	"0DD1", # GF106 [GTX 460M]
	"0DD2", # GF106 [GT 445M]
	"0DD3", # GF106 [GT 435M]
	"0DD6", # GF106 [GT 550M]
	"0DD8", # GF106 [2000]
	"0DDA", # GF106 [2000M]
	# GF116
	"1241", # GF116 [GT 545 OEM]
	"1243", # GF116 [GT 545]
	"1244", # GF116 [GTX 550 Ti]
	"1245", # GF116 [GTS 450 Rev. 2]
	"1246", # GF116 [GT 550M]
	"1247", # GF116 [GT 635M]
	"1248", # GF116 [GT 555M]
	"1249", # GF116 [GTS 450 Rev. 3]
	"124B", # GF116 [GT 640 OEM]
	"124D", # GF116 [GT 555M]
	"1251", # GF116 [GTX 560M]
	# GF108
	"0DE0", # GF108 [GT 440]
	"0DE1", # GF108 [GT 430]
	"0DE2", # GF108 [GT 420]
	"0DE3", # GF108 [GT 635M]
	"0DE4", # GF108 [GT 520]
	"0DE5", # GF108 [GT 530]
	"0DE8", # GF108 [GT 620M]
	"0DE9", # GF108 [GT 630M]
	"0DEA", # GF108 [610M]
	"0DEB", # GF108 [GT 555M]
	"0DEC", # GF108 [GT 525M]
	"0DED", # GF108 [GT 520M]
	"0DEE", # GF108 [GT 415M]
	"0DEF", # GF108 [NVS 5400M]
	"0DF0", # GF108 [GT 425M]
	"0DF1", # GF108 [GT 420M]
	"0DF2", # GF108 [GT 435M]
	"0DF3", # GF108 [GT 420M]
	"0DF4", # GF108 [GT 540M]
	"0DF5", # GF108 [GT 525M]
	"0DF6", # GF108 [GT 550M]
	"0DF7", # GF108 [GT 520M]
	"0DF8", # GF108 [600]
	"0DF9", # GF108 [500M]
	"0DFA", # GF108 [1000M]
	"0DFC", # GF108 [NVS 5200M]
	"0F00", # GF108 [GT 630]
	"0F01", # GF108 [GT 620]
	# GF110
	"1080", # GF110 [GTX 580]
	"1081", # GF110 [GTX 570]
	"1082", # GF110 [GTX 560 Ti]
	"1084", # GF110 [GTX 560]
	"1086", # GF110 [GTX 570]
	"1087", # GF110 [GTX 560 Ti]
	"1088", # GF110 [GTX 590]
	"1089", # GF110 [GTX 580]
	"108B", # GF110 [GTX 580]
	"1091", # GF110 [M2090]
	"109A", # GF110 [5010M]
	"109B", # GF110 [7000]
	# GF119
	"1040", # GF119 [GT 520]
	"1042", # GF119 [510]
	"1048", # GF119 [605]
	"1049", # GF119 [GT 620]
	"104A", # GF119 [GT 610]
	"1050", # GF119 [GT 520M]
	"1051", # GF119 [GT 520MX]
	"1052", # GF119 [GT 520M]
	"1054", # GF119 [410M]
	"1055", # GF119 [410M]
	"1056", # GF119 [NVS 4200M]
	"1057", # GF119 [NVS 4200M]
	"1058", # GF119 [610M]
	"1059", # GF119 [610M]
	"105A", # GF119 [610M]
	"107D", # GF119 [NVS 310]
	# GF117
	"1140", # GF117 [GT 620M]
]

NvidiaKeplerpciid = [
	# GK104
	"1180", # GK104 [GTX 680]
	"1183", # GK104 [GTX 660 Ti]
	"1185", # GK104 [GTX 660]
	"1188", # GK104 [GTX 690]
	"1189", # GK104 [GTX 670]
	"1199", # GK104 [GTX 870M]
	"119F", # GK104 [GTX 780M]
	"11A0", # GK104 [GTX 680M]
	"11A1", # GK104 [GTX 670MX]
	"11A2", # GK104 [GTX 675MX]
	"11A3", # GK104 [GTX 680MX]
	"11A7", # GK104 [GTX 675MX]
	"11BA", # GK104 [K5000]
	"11BC", # GK104 [K5000M]
	"11BD", # GK104 [K4000M]
	"11BE", # GK104 [K3000M]
	"11BF", # GK104 [GRID K2]
	# GK106
	"11C0", # GK106 [GTX 660]
	"11C6", # GK106 [GTX 650 Ti]
	"11E0", # GK106 [GTX 770M]
	"11FA", # GK106 [K4000]
	# GK107
	"0FC0", # GK107 [GT 640]
	"0FC1", # GK107 [GT 640]
	"0FC2", # GK107 [GT 630]
	"0FC6", # GK107 [GTX 650]
	"0FD1", # GK107 [GT 650M]
	"0FD2", # GK107 [GT 640M]
	"0FD3", # GK107 [GT 640M LE]
	"0FD4", # GK107 [GTX 660M]
	"0FD5", # GK107 [GT 650M]
	"0FD8", # GK107 [GT 640M]
	"0FD9", # GK107 [GT 645M]
	"0FE0", # GK107 [GTX 660M]
	"0FE9", # GK107 [GT 750M Mac Edition]
	"0FF9", # GK107 [K2000D]
	"0FFA", # GK107 [K600]
	"0FFB", # GK107 [K2000M]
	"0FFC", # GK107 [K1000M]
	"0FFD", # GK107 [NVS 510]
	"0FFE", # GK107 [K2000]
	"0FFF", # GK107 [410]
	# GK110
	"1003", # GK110 [GTX Titan LE]
	"1004", # GK110 [GTX 780]
	"1005", # GK110 [GTX Titan]
	"101F", # GK110 [TEslA K20]
	"1020", # GK110 [TEslA K2]
	"1021", # GK110 [TEslA K2m]
	"1022", # GK110 [TEslA K20C]
	"1026", # GK110 [TEslA K20s]
	"1028", # GK110 [TEslA K20m]
	# GK208
	"1280", # GK208 [GT 635]
	"1282", # GK208 [GT 640 REv. 2]
	"1284", # GK208 [GT 630 REv. 2]
	"1290", # GK208 [GT 730M]
	"1291", # GK208 [GT 735M]
	"1292", # GK208 [GT 740M]
	"1293", # GK208 [GT 730M]
	"1294", # GK208 [GT 740M]
	"1295", # GK208 [710M]
	"12B9", # GK208 [K610M]
	"12BA", # GK208 [K510M]
]

AMDGCNpciid = [
    # AMDRadeonX4000
	# AMDBonaireGraphicsAccelerator
	"6640",
	"6641",
	"6646",
	"6647",
	"6650",
	"6651",
	"665C",
	"665D",
	# AMDFijiGraphicsAccelerator
	"7300",
	"730F",
	# AMDHawaiiGraphicsAccelerator
	"67B0",
	# AMDPitcairnGraphicsAccelerator
	"6800",
	"6801",
	"6806",
	"6808",
	"6810",
	"6818",
	"6819",
	# AMDTahitiGraphicsAccelerator
	"6790",
	"6798",
	"679A",
	"679E",
	"6780",
	# AMDTongaGraphicsAccelerator
	"6920",
	"6921",
	"6930",
	"6938",
	"6939",
	# AMDVerdeGraphicsAccelerator
	"6820",
	"6821",
	"6823",
	"6825",
	"6827",
	"682B",
	"682D",
	"682F",
	"6835",
	"6839",
	"683B",
	"683D",
	"683F",
]

AMDPolarispciid = [
	# AMDRadeonX4000
	# AMDBaffinGraphicsAccelerator
	"67E0",
	"67E3",
	"67E8",
	"67EB",
	"67EF",
	"67FF",
	"67E1",
	"67E7",
	"67E9",
	# AMDEllesmereGraphicsAccelerator
	"67C0",
	"67C1",
	"67C2",
	"67C4",
	"67C7",
	"67DF",
	"67D0",
	"67C8",
	"67C9",
	"67CA",
	"67CC",
	"67CF",
]

AMDVegapciid = [
	# AMDRadeonX5000
	# AMDVega10GraphicsAccelerator
	"6860",
	"6861",
	"6862",
	"6863",
	"6864",
	"6867",
	"6868",
	"6869",
	"686A",
	"686B",
	"686C",
	"686D",
	"686E",
	"686F",
	"687F",
	# AMDVega12GraphicsAccelerator
	"69A0",
	"69A1",
	"69A2",
	"69A3",
	"69AF",
	# AMDVega20GraphicsAccelerator
	"66A0",
	"66A1",
	"66A2",
	"66A3",
	"66A7",
	"66AF",
]

AMDNavipciid = [
	# AMDRadeonX6000
	# AMDNavi10GraphicsAccelerator
	"7310",
	"7312",
	"7318",
	"7319",
	"731A",
	"731B",
	"731F",
	# AMDNavi12GraphicsAccelerator
	"7360",
	# AMDNavi14GraphicsAccelerator
	"7340",
	"7341",
	"7343",
	"7347",
	"734F",
	# AMDNavi21GraphicsAccelerator
	"73A2",
	"73AB",
	"73BF",
]