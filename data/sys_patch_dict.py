# Dictionary defining patch sets used during Root Volume patching (sys_patch.py)
# Copyright (C) 2022, Mykola Grymalyuk

# Schema for sys_patch_dict.py:
# Supports 6 types of higher level keys:
#  - OS Support:         Supported OSes by patches   - Dictionary of Min/Max Kernel Major and Minor versions
#  - Install:            Install to root volume      - Dictionary of strings with string value of source
#  - Install Non-Root:   Install to data partition   - Dictionary of strings with string value of source
#  - Remove:             Files to remove             - Array of strings
#  - Processes:          Additional processes to run - Dictionary of strings with boolean value of requires root
#  - Display Name:       User-friendly name          - String

# File Storage is based off the origin, ie. '10.13.6/System/Library/Extensions/IOSurface.kext'
# Stubbed binaries are OS specific, they use the 'os_major' variable to denounce which folder to use

from data import os_data

def SystemPatchDictionary(os_major, os_minor, non_metal_os_support):
    # @os_major:               XNU Kernel Major (int)
    # @os_minor:               XNU Kernel Minor (int)
    # @non_metal_os_support:   Array of supported OSes (XNU Kernel Majors (int))
    sys_patch_dict = {
        "Graphics": {
            "Non-Metal Common": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": non_metal_os_support[0],
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": non_metal_os_support[-1],
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "IOSurface.kext": "10.15.7",
                    },
                    "/System/Library/Frameworks": {
                        "OpenGL.framework":       "10.14.3",
                        "CoreDisplay.framework": f"10.14.4-{os_major}",
                        "IOSurface.framework":   f"10.15.7-{os_major}",
                        "QuartzCore.framework":  f"10.15.7-{os_major}",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUSupport.framework": "10.14.3",
                        "SkyLight.framework":  f"10.14.6-{os_major}",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
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
                        "AppleAfterburner.kext",
                    ],
                },
                "Install Non-Root": {
                    "/Library/Application Support/SkyLightPlugins": {
                        **({ "DropboxHack.dylib":    "SkyLightPlugins" } if os_major >= os_data.os_data.monterey else {}),
                        **({ "DropboxHack.txt":      "SkyLightPlugins" } if os_major >= os_data.os_data.monterey else {}),
                        **({ "CatalystButton.dylib": "SkyLightPlugins" } if os_major >= os_data.os_data.monterey else {}),
                        **({ "CatalystButton.txt":   "SkyLightPlugins" } if os_major >= os_data.os_data.monterey else {}),
                    },
                },
                "Processes": {
                    # 'When Space Allows' option introduced in 12.4 (XNU 21.5)
                    **({"defaults write /Library/Preferences/.GlobalPreferences.plist ShowDate -int 1": True } if os_data.os_conversion.is_os_newer(os_data.os_data.monterey, 4, os_major, os_minor) else {}),
                },
            },
            "Non-Metal IOAccelerator Common": {
                # TeraScale 2 and Nvidia Web Drivers broke in Mojave due to mismatched structs in
                # the IOAccelerator stack
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": non_metal_os_support[0],
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": non_metal_os_support[-1],
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "IOAcceleratorFamily2.kext":     "10.13.6",
                        "IOSurface.kext":                "10.14.6",
                    },
                    "/System/Library/Frameworks": {
                        "IOSurface.framework": f"10.14.6-{os_major}",
                        "OpenCL.framework":     "10.13.6",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUSupport.framework":     "10.13.6",
                        "IOAccelerator.framework": f"10.13.6-{os_major}",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        "AppleCameraInterface.kext"
                    ],
                },
            },

            "Non-Metal CoreDisplay Common": {
                # Nvidia Web Drivers require an older build of CoreDisplay
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": non_metal_os_support[0],
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": non_metal_os_support[-1],
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "CoreDisplay.framework": f"10.13.6-{os_major}",
                    },
                },
            },

            "Non-Metal Enforcement": {
                # Forces Metal kexts from High Sierra to run in the fallback non-Metal mode
                # Verified functional with HD4000 and Iris Plus 655
                # Only used for internal development purposes, not suitable for end users

                # Note: Metal kexts in High Sierra rely on IOAccelerator, thus 'Non-Metal IOAccelerator Common'
                # is needed for proper linking
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": non_metal_os_support[0],
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": non_metal_os_support[-1],
                        "OS Minor": 99
                    },
                },
                "Processes": {
                    "defaults write /Library/Preferences/com.apple.CoreDisplay useMetal -boolean no": True,
                    "defaults write /Library/Preferences/com.apple.CoreDisplay useIOP -boolean no":   True,
                },
            },

            # AMD GCN and Nvidia Kepler require Metal Downgrade in Ventura
            # The patches are required due to struct issues in the Metal stack
            # - AMD GCN will break on BronzeMtlDevice
            # - See Nvidia Kepler patchset for more info
            "Metal Common": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "Metal.framework":                   "12.5",
                        "MetalPerformanceShaders.framework": "12.5",
                    },
                },
            },

            # Temporary work-around for Kepler GPUs on Ventura
            # We removed the reliance on Metal.framework downgrade, however the new Kepler
            # patchset breaks with the old Metal. Thus we need to ensure stock variant is used
            # Remove this when OCLP is merged onto mainline
            "Revert Metal Downgrade": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 99
                    },
                },
                "Remove": {
                    "/System/Library/Frameworks/Metal.framework/Versions/A/": [
                        "Metal",
                        "MetalOld.dylib",
                    ],
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSCore.framework/Versions/A": [
                        "MPSCore",
                    ],
                },
            },

            # Monterey has a WebKit sandboxing issue where many UI elements fail to render
            # This patch simple replaces the sandbox profile with one supporting our GPUs
            # Note: Neither Big Sur nor Ventura have this issue
            "WebKit Monterey Common": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "WebKit.framework":  "11.6"
                    },
                },
                "Install Non-Root": {
                    "/Library/Apple/System/Library/StagedFrameworks/Safari": {
                        "WebKit.framework":  "11.6"
                    },
                },
            },

            # Intel Ivy Bridge, Haswell and Nvidia Kepler are Metal 3802-based GPUs
            # Due to this, we need to re-add 3802 compiler support to the Metal stack
            "Metal 3802 Common": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "Metal.framework": "12.5-3802",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "MTLCompiler.framework": "12.5-3802",
                        "GPUCompiler.framework": "12.5-3802",
                    },
                    "/System/Library/Sandbox/Profiles": {
                        "com.apple.mtlcompilerservice.sb": "12.5-3802",
                    }
                },
            },

            # For GPUs last natively supported in Catalina/Big Sur
            # Restores DRM support
            "Catalina GVA": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/PrivateFrameworks": {
                        "AppleGVA.framework":     "10.15.7",
                        "AppleGVACore.framework": "10.15.7",
                    },
                },
            },

            # For GPUs last natively supported in Monterey
            # Restores DRM support
            "Monterey GVA": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/PrivateFrameworks": {
                        "AppleGVA.framework":     "12.5",
                        "AppleGVACore.framework": "12.5",
                    },
                },
            },

            "High Sierra GVA": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": non_metal_os_support[0],
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/PrivateFrameworks": {
                        "AppleGVA.framework":     "10.13.6",
                        "AppleGVACore.framework": "10.15.7",
                    },
                },
            },

            "Big Sur OpenCL": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "OpenCL.framework": "11.6",
                    },
                },
            },

            "Monterey OpenCL": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "OpenCL.framework": "12.5",
                    },
                },
            },

            # In Ventura, Apple added AVX2.0 code to AMD's OpenCL/GL compilers
            "AMD OpenCL": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Frameworks": {
                        "OpenCL.framework": "12.5 non-AVX2.0",
                        "OpenGL.framework": "12.5 non-AVX2.0",
                    },
                },
            },

            "Nvidia Tesla": {
                "Display Name": "Graphics: Nvidia Tesla",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "GeForceGA.bundle":            "10.13.6",
                        "GeForceTesla.kext":           "10.13.6",
                        "GeForceTeslaGLDriver.bundle": "10.13.6",
                        "GeForceTeslaVADriver.bundle": "10.13.6",
                        "NVDANV50HalTesla.kext":       "10.13.6",
                        "NVDAResmanTesla.kext":        "10.13.6",
                        # Apple dropped NVDAStartup in 12.0 Beta 7 (XNU 21.1)
                        **({ "NVDAStartup.kext":       "12.0 Beta 6" } if os_data.os_conversion.is_os_newer(os_data.os_data.monterey, 0, os_major, os_minor) else {})
                    },
                },
            },
            "Nvidia Kepler": {
                "Display Name": "Graphics: Nvidia Kepler",
                "OS Support": {
                    "Minimum OS Support": {
                        # 12.0 beta 7 (XNU 21.1)
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 1
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "GeForce.kext":            "12.0 Beta 6",
                        "NVDAGF100Hal.kext":       "12.0 Beta 6",
                        "NVDAGK100Hal.kext":       "12.0 Beta 6",
                        "NVDAResman.kext":         "12.0 Beta 6",
                        "NVDAStartup.kext":        "12.0 Beta 6",
                        "GeForceAIRPlugin.bundle": "11.0 Beta 3",
                        "GeForceGLDriver.bundle":  "11.0 Beta 3",
                        "GeForceMTLDriver.bundle": "11.0 Beta 3" if os_major <= os_data.os_data.monterey else f"11.0 Beta 3-{os_major}",
                        "GeForceVADriver.bundle":  "12.0 Beta 6",
                    },
                    "/System/Library/Frameworks": {
                        # XNU 21.6 (macOS 12.5)
                        **({ "Metal.framework": "12.5 Beta 2"} if (os_data.os_conversion.is_os_newer(os_data.os_data.monterey, 5, os_major, os_minor) and os_major < os_data.os_data.ventura) else {}),
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUCompiler.framework": "11.6",
                    },
                },
            },
            "Nvidia Web Drivers": {
                "Display Name": "Graphics: Nvidia Web Drivers",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "GeForceAIRPluginWeb.bundle":     "WebDriver-387.10.10.10.40.140",
                        "GeForceGLDriverWeb.bundle":      "WebDriver-387.10.10.10.40.140",
                        "GeForceMTLDriverWeb.bundle":     "WebDriver-387.10.10.10.40.140",
                        "GeForceVADriverWeb.bundle":      "WebDriver-387.10.10.10.40.140",

                        # Tesla-only files
                        "GeForceTeslaGAWeb.bundle":       "WebDriver-387.10.10.10.40.140",
                        "GeForceTeslaGLDriverWeb.bundle": "WebDriver-387.10.10.10.40.140",
                        "GeForceTeslaVADriverWeb.bundle": "WebDriver-387.10.10.10.40.140",
                    },
                },
                "Install Non-Root": {
                     "/Library/Extensions": {
                        "GeForceWeb.kext":                "WebDriver-387.10.10.10.40.140",
                        "NVDAGF100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAGK100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAGM100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAGP100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDAResmanWeb.kext":             "WebDriver-387.10.10.10.40.140",
                        "NVDAStartupWeb.kext":            "WebDriver-387.10.10.10.40.140",

                        # Tesla-only files
                        "GeForceTeslaWeb.kext":           "WebDriver-387.10.10.10.40.140",
                        "NVDANV50HalTeslaWeb.kext":       "WebDriver-387.10.10.10.40.140",
                        "NVDAResmanTeslaWeb.kext":        "WebDriver-387.10.10.10.40.140",
                    },

                    # Disabled due to issues with Pref pane stripping 'nvda_drv' NVRAM
                    # variables
                    # "/Library/PreferencePanes": {
                    #     "NVIDIA Driver Manager.prefPane": "WebDriver-387.10.10.10.40.140",
                    # },
                    #  "/Library/LaunchAgents": {
                    #     "com.nvidia.nvagent.plist":       "WebDriver-387.10.10.10.40.140",
                    # },
                    # "/Library/LaunchDaemons": {
                    #     "com.nvidia.nvroothelper.plist":  "WebDriver-387.10.10.10.40.140",
                    # },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        # Due to how late the Auxiliary cache loads, NVDAStartup will match first and then the Web Driver kexts.
                        # This has no effect for Maxwell and Pascal, however for development purposes, Tesla and Kepler are partially supported.
                        "NVDAStartup.kext",
                    ],
                },
            },
            "AMD TeraScale Common": {
                "Display Name": "",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AMDFramebuffer.kext":           "10.13.6",
                        "AMDLegacyFramebuffer.kext":     "10.13.6",
                        "AMDLegacySupport.kext":         "10.13.6",
                        "AMDShared.bundle":              "10.13.6",
                        "AMDSupport.kext":               "10.13.6",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        "AMD7000Controller.kext",
                        "AMD8000Controller.kext",
                        "AMD9000Controller.kext",
                        "AMD9500Controller.kext",
                        "AMD10000Controller.kext",
                    ],
                },
            },

            "AMD TeraScale 1": {
                "Display Name": "Graphics: AMD TeraScale 1",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AMD2400Controller.kext":        "10.13.6",
                        "AMD2600Controller.kext":        "10.13.6",
                        "AMD3800Controller.kext":        "10.13.6",
                        "AMD4600Controller.kext":        "10.13.6",
                        "AMD4800Controller.kext":        "10.13.6",
                        "ATIRadeonX2000.kext":           "10.13.6",
                        "ATIRadeonX2000GA.plugin":       "10.13.6",
                        "ATIRadeonX2000GLDriver.bundle": "10.13.6",
                        "ATIRadeonX2000VADriver.bundle": "10.13.6",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        # Following removals are a work around for 0.4.3 and older root patches
                        # Previously TS1 and TS2 patch sets were shared, now they're split off
                        # Due to this, updating to 0.4.4 or newer can break kmutil linking
                        "AMD5000Controller.kext",
                        "AMD6000Controller.kext",
                        "AMDRadeonVADriver.bundle",
                        "AMDRadeonVADriver2.bundle",
                        "AMDRadeonX3000.kext",
                        "AMDRadeonX3000GLDriver.bundle",
                    ],
                },
            },
            "AMD TeraScale 2": {
                "Display Name": "Graphics: AMD TeraScale 2",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AMD5000Controller.kext":        "10.13.6",
                        "AMD6000Controller.kext":        "10.13.6",
                        "AMDRadeonVADriver.bundle":      "10.13.6",
                        "AMDRadeonVADriver2.bundle":     "10.13.6",
                        "AMDRadeonX3000.kext":           "10.13.6",
                        "AMDRadeonX3000GLDriver.bundle": "10.13.6",
                    },
                },
            },
            "AMD Legacy GCN": {
                "Display Name": "Graphics: AMD Legacy GCN",
                 "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AMD7000Controller.kext":        "12.5",
                        "AMD8000Controller.kext":        "12.5",
                        "AMD9000Controller.kext":        "12.5",
                        "AMD9500Controller.kext":        "12.5",
                        "AMDRadeonX4000.kext":           "12.5",
                        "AMDRadeonX4000HWServices.kext": "12.5",
                        "AMDFramebuffer.kext":           "12.5",
                        "AMDSupport.kext":               "12.5",

                        "AMDRadeonX4000GLDriver.bundle": "12.5",
                        "AMDMTLBronzeDriver.bundle":     "12.5",
                        "AMDShared.bundle":              "12.5",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        # Due to downgraded AMDSupport.kext
                        # In the future, we will have to downgrade the entire AMD stack
                        # to support non-AVX2.0 machines with Vega or newer
                        "AMD10000Controller.kext",
                    ],
                },
            },
            "Intel Ironlake": {
                "Display Name": "Graphics: Intel Ironlake",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleIntelHDGraphics.kext":           "10.13.6",
                        "AppleIntelHDGraphicsFB.kext":         "10.13.6",
                        "AppleIntelHDGraphicsGA.plugin":       "10.13.6",
                        "AppleIntelHDGraphicsGLDriver.bundle": "10.13.6",
                        "AppleIntelHDGraphicsVADriver.bundle": "10.13.6",
                    },
                },
            },
            "Intel Sandy Bridge": {
                "Display Name": "Graphics: Intel Sandy Bridge",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleIntelHD3000Graphics.kext":           "10.13.6",
                        "AppleIntelHD3000GraphicsGA.plugin":       "10.13.6",
                        "AppleIntelHD3000GraphicsGLDriver.bundle": "10.13.6",
                        "AppleIntelHD3000GraphicsVADriver.bundle": "10.13.6",
                        "AppleIntelSNBGraphicsFB.kext":            "10.13.6",
                        "AppleIntelSNBVA.bundle":                  "10.13.6",
                    },
                },
            },
            "Intel Ivy Bridge": {
                "Display Name": "Graphics: Intel Ivy Bridge",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Processes": {
                    "defaults write com.apple.coremedia hardwareVideoDecoder -string enable": False,
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleIntelHD4000GraphicsGLDriver.bundle":  "11.0 Beta 6",
                        "AppleIntelHD4000GraphicsMTLDriver.bundle": "11.0 Beta 6",
                        "AppleIntelHD4000GraphicsVADriver.bundle":  "11.3 Beta 1",
                        "AppleIntelFramebufferCapri.kext":          "11.4",
                        "AppleIntelHD4000Graphics.kext":            "11.4",
                        "AppleIntelIVBVA.bundle":                   "11.4",
                        "AppleIntelGraphicsShared.bundle":          "11.4", # libIGIL-Metal.dylib pulled from 11.0 Beta 6
                    },
                },
            },
            "Intel Haswell": {
                "Display Name": "Graphics: Intel Haswell",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleIntelFramebufferAzul.kext":           "12.5",
                        "AppleIntelHD5000Graphics.kext":            "12.5",
                        "AppleIntelHD5000GraphicsGLDriver.bundle":  "12.5",
                        "AppleIntelHD5000GraphicsMTLDriver.bundle": "12.5",
                        "AppleIntelHD5000GraphicsVADriver.bundle":  "12.5",
                        "AppleIntelHSWVA.bundle":                   "12.5",
                        "AppleIntelGraphicsShared.bundle":          "12.5",
                    },
                },
            },
            "Intel Broadwell": {
                "Display Name": "Graphics: Intel Broadwell",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleIntelBDWGraphics.kext":            "12.5",
                        "AppleIntelBDWGraphicsFramebuffer.kext": "12.5",
                        "AppleIntelBDWGraphicsGLDriver.bundle":  "12.5",
                        "AppleIntelBDWGraphicsMTLDriver.bundle": "12.5",
                        "AppleIntelBDWGraphicsVADriver.bundle":  "12.5",
                        "AppleIntelBDWGraphicsVAME.bundle":      "12.5",
                        "AppleIntelGraphicsShared.bundle":       "12.5",
                    },
                },
            },
            "Intel Skylake": {
                "Display Name": "Graphics: Intel Skylake",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.ventura,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleIntelSKLGraphics.kext":            "12.5",
                        "AppleIntelSKLGraphicsFramebuffer.kext": "12.5",
                        "AppleIntelSKLGraphicsGLDriver.bundle":  "12.5",
                        "AppleIntelSKLGraphicsMTLDriver.bundle": "12.5",
                        "AppleIntelSKLGraphicsVADriver.bundle":  "12.5",
                        "AppleIntelSKLGraphicsVAME.bundle":      "12.5",
                        "AppleIntelGraphicsShared.bundle":       "12.5",
                    },
                },
            },
        },
        "Audio": {
            "Legacy Realtek": {
                "Display Name": "Audio: Legacy Realtek",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.sierra,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                # For iMac7,1 and iMac8,1 units with legacy Realtek HD Audio
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext":      "10.11.6",
                        "IOAudioFamily.kext": "10.11.6",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        "AppleVirtIO.kext",
                        "AppleVirtualGraphics.kext",
                        "AppleVirtualPlatform.kext",
                        "ApplePVPanic.kext",
                        "AppleVirtIOStorage.kext",
                    ],
                },
            },
            # For Mac Pros with non-UGA/GOP GPUs
            "Legacy Non-GOP": {
                "Display Name": "Audio: Legacy non-GOP",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.mojave,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext": "10.13.6",
                    },
                },
            },
        },
        "Networking": {
            "Legacy Wireless": {
                "Display Name": "Networking: Legacy Wireless",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.monterey,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/usr/libexec": {
                        "airportd": "11.5.2",
                    },
                    "/System/Library/CoreServices": {
                        "WiFiAgent.app": "11.5.2",
                    },
                },
                "Install Non-Root": {
                    "/Library/Application Support/SkyLightPlugins": {
                        **({ "CoreWLAN.dylib": "SkyLightPlugins" } if os_major >= os_data.os_data.monterey else {}),
                        **({ "CoreWLAN.txt": "SkyLightPlugins" } if os_major >= os_data.os_data.monterey else {}),
                    },
                },
            },
        },
        "Brightness": {
            "Legacy Backlight Control": {
                "Display Name": "Brightness: Legacy Backlight Control",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.high_sierra,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions": {
                        "AppleBacklight.kext":       "10.12.6",
                        "AppleBacklightExpert.kext": "10.12.6",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "DisplayServices.framework": "10.12.6",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": [
                        "AGDCBacklightControl.kext",
                    ],
                },
            },
        },
        "Miscellaneous": {
            "Legacy GMUX": {
                "Display Name": "Miscellaneous: Legacy GMUX",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": os_data.os_data.high_sierra,
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": os_data.os_data.max_os,
                        "OS Minor": 99
                    },
                },
                "Install": {
                    "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": {
                        "AppleMuxControl.kext": "10.12.6",
                    },
                },
                "Remove": {
                    "/System/Library/Extensions": [
                        "AppleBacklight.kext",
                    ],
                    "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": [
                        "AGDCBacklightControl.kext",
                        "AppleMuxControl.kext",
                    ],
                },
            },
            "Legacy Keyboard Backlight": {
                "Display Name": "Miscellaneous: Legacy Keyboard Backlight",
                "OS Support": {
                    "Minimum OS Support": {
                        "OS Major": non_metal_os_support[0],
                        "OS Minor": 0
                    },
                    "Maximum OS Support": {
                        "OS Major": non_metal_os_support[-1],
                        "OS Minor": 99
                    },
                },
                "Processes": {
                    "defaults write /Library/Preferences/.GlobalPreferences.plist Moraea_BacklightHack -bool true": True,
                },
            },
        },
    }

    return sys_patch_dict