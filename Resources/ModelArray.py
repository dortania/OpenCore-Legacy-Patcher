# Lists all models and required patches

SupportedSMBIOS11 = [
    # MacBook
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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    # Mac Pro
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    # Xserve
    "Xserve3,1",
    "Dortania1,1"
]

SupportedSMBIOS12 = [

]

## CPU patches

MissingSSE42 = [
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
    "Dortania1,1"
]

SSEEmulator = [
    "MacPro3,1",
    "Dortania1,1"
]

DualSocket = [
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
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

## Ethernet patches

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
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac9,1",
    "iMac10,1",
    "Dortania1,1"
]
EthernetMarvell = [
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1",
    "Dortania1,1"
]
EthernetBroadcom = [
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
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

## Wifi patches

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
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Dortania1,1"
]

WifiBCM943224 = [
    "MacBook6,1",
    "MacBook7,1",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "Macmini3,1",
    "Macmini4,1",
    "Dortania1,1"
]

WifiBCM94331 = [
    "MacBook5,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBook5,2",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBook6,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBook7,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookAir3,1", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookAir3,2", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookAir4,1", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookAir4,2", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookAir5,1", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookAir5,2", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro5,1", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookPro5,2", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookPro5,3", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookPro5,4", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookPro5,5", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookPro6,1", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro6,2", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro7,1", # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "MacBookPro8,1", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro8,2", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro8,3", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro9,1", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro9,2", # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro10,1",# PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "MacBookPro10,2",# PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini3,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "Macmini4,1",    # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "Macmini5,1",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini5,2",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini5,3",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini6,1",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    "Macmini6,2",    # PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
    #"iMac9,1",       # PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)
    "iMac13,1",      # PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)
    "iMac13,2",      # PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)
    "MacPro5,1",     # PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)
    "Dortania1,1"
]

## Audio

LegacyAudio = [
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

## GPU

LegacyGPU = [
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
    "Dortania1,1"
]

LegacyHID = [
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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "Dortania1,1"
]

DualGPUPatch = [
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "Macmini5,2",
    "iMac12,1",
    "iMac12,2",
    "iMac13,2",
    "iMac14,2",
    "iMac14,3",
    "Dortania1,1"
]

DualGPUPatchRetina = [
    "MacBookPro10,1",
]

HiDPIpicker = [
    "MacBookPro10,1",
    "MacBookPro10,2",
    "Dortania1,1"
]

IDEPatch = [
    "MacPro3,1",
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

# iMac = AMD and Nvidia GPU
iMac151 = [
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
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
    "Xserve3,1",
    "Dortania1,1"
]

# Maps

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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
]

XacBookNormal = [
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

EHCI = [
    "MacPro3,1"
]

EHC1 = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
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
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "MacPro4,1",
    "MacPro5,1",
]

EHC2 = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
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
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "MacPro4,1",
    "MacPro5,1",
]

OHC1 = [
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
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
]

IHEHC1 = [
    "iMac13,1",
    "iMac13,2",
    "iMac13,3"
]

IHEHC2 = [
    "MacBookPro9,1"
]

IH = [
    "MacPro6,1"
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
    "0x12b9",#Quadro K610M
    "0x0ff6",#Quadro K1100M
    "0x11fc",#Quadro K2100M
    "0x0ffc",#Quadro K1000M
    "0x0ffb",#Quadro K2000M
    "0x11b6",#Quadro K3100M
    "0x11b7",#Quadro K4100M
    "0x11bc",#Quadro K5000M
    "0x11b8",#Quadro K5100M
    "0x11e1",#GTX 765M
    "0x11e2",#GTX 765M
    "0x11e0",#GTX 770M
    "0x119e",#GTX 780M Mac Edition
    "0x119e",#GTX 780M
    "0x119f",#GTX 880M
    "0x119a",#GTX 860M
    "0x1392",#GTX 860M
    "0x1199",#GTX 870M
    "0x11a9",#GTX 870M
]

AMDMXMGPUs = [
    "0x67EF",#AMD RX 460
    "0x67e8",#AMD WX 4130/WX 4150
    "0x67e0",#AMD WX 4170
    "0x67c0",#AMD WX 7100
]

nativeWifi = [
    "ba430000",#BCM43602
    "a3430000",#BCM4350
    "a0430000",#BCM4360
]

X86PP = [
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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
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
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
]

UGAtoGOP = [
    "MacBookPro4,1",
    "MacPro3,1"
]

NoSATAPatch = [
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    "iMac13,1",
    "iMac13,2",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
]

NoAPFSsupport = [
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
    "Xserve3,1",
    "Dortania1,1"
]