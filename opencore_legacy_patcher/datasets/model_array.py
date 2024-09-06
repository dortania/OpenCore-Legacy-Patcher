"""
model_array.py: Datasets for different models
"""


SupportedSMBIOS = [
    # MacBook
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBook8,1",
    "MacBook9,1",
    "MacBook10,1",
    # MacBook Air
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookAir6,1",
    "MacBookAir6,2",
    "MacBookAir7,1",
    "MacBookAir7,2",
    # "MacBookAir8,1",
    # "MacBookAir8,2",
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
    "MacBookPro11,1",
    "MacBookPro11,2",
    "MacBookPro11,3",
    "MacBookPro11,4",
    "MacBookPro11,5",
    "MacBookPro12,1",
    "MacBookPro13,1",
    "MacBookPro13,2",
    "MacBookPro13,3",
    "MacBookPro14,1",
    "MacBookPro14,2",
    "MacBookPro14,3",
    # Mac Mini
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
    "Macmini7,1",
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
    "iMac14,4",
    "iMac15,1",
    "iMac16,1",
    "iMac16,2",
    "iMac17,1",
    "iMac18,1",
    "iMac18,2",
    "iMac18,3",
    # Mac Pro
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "MacPro6,1",
    # Xserve
    "Xserve2,1",
    "Xserve3,1",
]

# Audio

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
    # "iMac7,1",
    # "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "MacPro3,1",
    "Dortania1,1",
]

# GPU

ModernGPU = [
    "MacBook8,1", # Intel 6000
    "MacBook9,1", # Intel Skylake
    "MacBookAir5,1",  # Intel 4000
    "MacBookAir5,2",  # Intel 4000
    "MacBookAir6,1",  # Intel 5000
    "MacBookAir6,2",  # Intel 5000
    "MacBookAir7,1",  # Intel 6000
    "MacBookAir7,2",  # Intel 6000
    "MacBookPro9,1",  # Intel 4000 + Nvidia 650M
    "MacBookPro9,2",  # Intel 4000
    "MacBookPro10,1",  # Intel 4000 + Nvidia 650M
    "MacBookPro10,2",  # Intel 4000
    "MacBookPro11,1",  # Intel 5000
    "MacBookPro11,2",  # Intel 5000
    "MacBookPro11,3",  # Intel 5000 + Nvidia Kepler
    "MacBookPro11,4",  # Intel 5000
    "MacBookPro11,5",  # Intel 5000 + GCN 1
    "MacBookPro12,1",  # Intel 6000
    "MacBookPro13,1",  # Intel Skylake
    "MacBookPro13,2",  # Intel Skylake
    "MacBookPro13,3",  # Intel Skylake
    "Macmini6,1",  # Intel 4000
    "Macmini6,2",  # Intel 4000
    "Macmini7,1",  # Intel 5000
    "iMac13,1",  # Intel 4000
    "iMac13,2",  # Intel 4000 + Nvidia Kepler
    "iMac13,3",  # Intel 4000
    "iMac14,1",  # Intel 5000 + Nvidia Kepler
    "iMac14,2",  # Intel 5000 + Nvidia Kepler
    "iMac14,3",  # Intel 5000 + Nvidia Kepler
    "iMac14,4",  # Intel 5000
    "iMac15,1",  # Intel 5000 + GCN 1
    "iMac16,1",  # Intel 6000
    "iMac16,2",  # Intel 6000
    "iMac17,1",  # Intel Skylake + GCN1
    "MacPro3,1", # Lacks AVX2.0
    "MacPro4,1", # Lacks AVX2.0
    "MacPro5,1", # Lacks AVX2.0
    "MacPro6,1", # GCN 1
]

LegacyGPU = [
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
    "Dortania1,1",  # RTX 3080
]

LegacyBrightness = [
    "MacBook5,2",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
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
    "Dortania1,1",
]

IntelNvidiaDRM = [
    "iMac13,1",
    "iMac13,2",
    "iMac14,2",
    "iMac14,3",
]

# Mac Pro and Xserve
MacPro = ["MacPro3,1", "MacPro4,1", "MacPro5,1", "Xserve2,1", "Xserve3,1", "Dortania1,1"]

# MXM iMac
MXMiMac = ["iMac11,1", "iMac11,2", "iMac11,3", "iMac10,1", "iMac12,1", "iMac12,2", "Dortania1,1"]

NoAGPMSupport = ["MacBookPro4,1", "iMac7,1", "iMac8,1", "MacPro3,1", "Xserve2,1", "Dortania1,1"]

AGDPSupport = [
    "MacBookPro9,1",
    "MacBookPro10,1",
    "iMac13,1",
    "iMac13,2",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "iMac14,4",
    "iMac15,1",
    # TODO: Uncomment when dropped from macOS
    # "iMac17,1",
    # "iMac18,2",
    # "iMac18,3",
    # "iMac19,1",
    # "iMac19,2",
    # "iMac20,1",
    # "iMac20,2",
    # "iMacPro1,1",
    # "MacPro6,1",
]

Missing_USB_Map = [
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
    "MacPro4,1",
    "Xserve2,1",
    "Xserve3,1",
]

Missing_USB_Map_Ventura = [
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
    "MacPro5,1",
    "MacPro6,1",
    "Macmini6,1",
    "Macmini6,2",
    "Macmini7,1",
    "iMac13,1",
    "iMac13,2",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    "iMac14,4",
    "iMac15,1",
    "iMac15,2",
    "iMac16,1",
    "iMac16,2",
    "iMac17,1",
]
