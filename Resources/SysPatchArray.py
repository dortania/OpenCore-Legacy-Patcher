# Lists Root patches used by SysPatch.py
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
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
    "IOGPUFamily.kext",
]

DeleteAMDAccel11TS2 = [
    "AppleCameraInterface.kext",
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

AddNvidiaBrightness = [
    "GeForceGA.bundle",
    "GeForceTesla.kext",
    "GeForceTeslaGLDriver.bundle",
    "GeForceTeslaVADriver.bundle",
    "NVDANV50HalTesla.kext",
    "NVDAResmanTesla.kext",
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
]

AddNvidiaTeslaAccel12 = [
    "NVDAStartup.kext",
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
    "AMDRadeonX3000.kext",
    "AMDRadeonX3000GLDriver.bundle",
    "AMDShared.bundle",
    "AMDSupport.kext",
    "ATIRadeonX2000.kext",
    "ATIRadeonX2000GA.plugin",
    "ATIRadeonX2000GLDriver.bundle",
    "ATIRadeonX2000VADriver.bundle",
]

AddAMDBrightness = [
    "AMD2400Controller.kext",
    "AMD2600Controller.kext",
    "AMD3800Controller.kext",
    "AMD4600Controller.kext",
    "AMD4800Controller.kext",
    "AMD5000Controller.kext",
    "AMD6000Controller.kext",
    "AMDLegacyFramebuffer.kext",
    "AMDLegacySupport.kext",
    "AMDRadeonVADriver.bundle",
    "AMDRadeonVADriver2.bundle",
    # "AMDRadeonX3000.kext",
    # "AMDRadeonX3000GLDriver.bundle",
    "AMDShared.bundle",
    "ATIRadeonX2000.kext",
    "ATIRadeonX2000GA.plugin",
    "ATIRadeonX2000GLDriver.bundle",
    "ATIRadeonX2000VADriver.bundle",
]

AddAMDAccel11TS2 = [
    "IOSurface.kext",
    "IOAcceleratorFamily2.kext",
]

AddIntelGen1Accel = [
    "AppleIntelHDGraphics.kext",
    "AppleIntelHDGraphicsFB.kext",
    "AppleIntelHDGraphicsGA.plugin",
    "AppleIntelHDGraphicsGLDriver.bundle",
    "AppleIntelHDGraphicsVADriver.bundle",
]

AddIntelGen2Accel = [
    "AppleIntelHD3000Graphics.kext",
    "AppleIntelHD3000GraphicsGA.plugin",
    "AppleIntelHD3000GraphicsGLDriver.bundle",
    "AppleIntelHD3000GraphicsVADriver.bundle",
    "AppleIntelSNBGraphicsFB.kext",
    "AppleIntelSNBVA.bundle",
]

AddIntelGen3Accel = [
    "AppleIntelFramebufferCapri.kext",
    "AppleIntelHD4000Graphics.kext",
    "AppleIntelHD4000GraphicsGLDriver.bundle",
    "AppleIntelHD4000GraphicsMTLDriver.bundle",
    "AppleIntelHD4000GraphicsVADriver.bundle",
    "AppleIntelIVBVA.bundle",
    "AppleIntelGraphicsShared.bundle",
]

AddGeneralAccel = ["IOAcceleratorFamily2.kext", "IOSurface.kext"]

DeleteBrightness = ["AppleGraphicsControl.kext/Contents/PlugIns/AGDCBacklightControl.kext"]

AddBrightness = [
    "AppleBacklight.kext",
    "AppleBacklightExpert.kext",
]

AddVolumeControl = [
    "AppleHDA.kext",
    "IOAudioFamily.kext",
]

AddVolumeControlv2 = [
    "AppleHDA.kext",
]

DeleteVolumeControl = [
    "AppleVirtIO.kext",
    "AppleVirtualGraphics.kext",
    "AppleVirtualPlatform.kext",
    "ApplePVPanic.kext",
    "AppleVirtIOStorage.kext",
]

AddNvidiaAccelLegacy = [
    # "GeForceGA.bundle",
    "GeForceTesla.kext",
    "GeForceTeslaGLDriver.bundle",
    "GeForceTeslaVADriver.bundle",
    "NVDANV50HalTesla.kext",
    "NVDAResmanTesla.kext",
]

AddAMDAccelLegacy = [
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
    "AMDRadeonX3000.kext",
    "AMDRadeonX3000GLDriver.bundle",
    "AMDRadeonX4000HWServices.kext",
    "AMDRadeonX4000.kext",
    "AMDRadeonX4000GLDriver.bundle",
    "AMDShared.bundle",
    "AMDSupport.kext",
    "ATIRadeonX2000.kext",
    "ATIRadeonX2000GA.plugin",
    "ATIRadeonX2000GLDriver.bundle",
    "ATIRadeonX2000VADriver.bundle",
]

AddGeneralAccelCatalina = [
    "AppleGraphicsControl.kext",
    "AppleGraphicsPowerManagement.kext",
    "AppleMCCSControl.kext",
    "IOGraphicsFamily.kext",
    "IONDRVSupport.kext",
    "IOSurface.kext",
]

AddGeneralAccelMojave = [
    "IONDRVSupport.kext",
    "AppleGraphicsControl.kext",
    "AppleGraphicsPowerManagement.kext",
    "AppleMCCSControl.kext",
    "IOAccelerator2D.plugin",
    "IOAcceleratorFamily2.kext",
    "IOGraphicsFamily.kext",
]

BackupLocations = [
    "System/Library/Extensions",
    "System/Library/Frameworks/CoreDisplay.framework",
    "System/Library/Frameworks/IOSurface.framework",
    "System/Library/Frameworks/OpenGL.framework",
    "System/Library/Frameworks/WebKit.framework",
    "System/Library/LaunchDaemons",
    "System/Library/PrivateFrameworks/DisplayServices.framework",
    "System/Library/PrivateFrameworks/GPUSupport.framework",
    "System/Library/PrivateFrameworks/SkyLight.framework",
    "System/Library/PrivateFrameworks/IOAccelerator.framework",
    "System/Library/PrivateFrameworks/AppleGVA.framework",
    "System/Library/PrivateFrameworks/AppleGVACore.framework",
]
