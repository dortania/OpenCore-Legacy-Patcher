"""
metal_3802.py: Metal 3802 patches
"""

import packaging.version

from .base import BaseSharedPatchSet

from ..base import PatchType, DynamicPatchset

from ....datasets.os_data import os_data


class LegacyMetal3802(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.ventura.value


    def _patches_metal_3802_common(self) -> dict:
        """
        Intel Ivy Bridge, Haswell and Nvidia Kepler are Metal 3802-based GPUs
        Due to this, we need to re-add 3802 compiler support to the Metal stack
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Metal 3802 Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Sandbox/Profiles": {
                        "com.apple.mtlcompilerservice.sb": "12.5-3802",
                    }
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "Metal.framework": "12.5-3802-22" if self._xnu_major < os_data.sonoma else "12.5-3802-23",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "MTLCompiler.framework": "12.7.6-3802",
                        "GPUCompiler.framework": "12.7.6-3802",
                    },
                }
            }
        }


    def _patches_metal_3802_common_extended(self) -> dict:
        """
        Support for 3802 GPUs were broken with 13.3+
        Downgrades 31001 stack to 13.2.1, however nukes AMFI support
        """
        if self._xnu_float < self.macOS_13_3:
            return {}

        return {
            "Metal 3802 Common Extended": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "Metal.framework": f"13.2.1-{self._xnu_major}",
                        **({  "CoreImage.framework": "14.0 Beta 3" if self._xnu_major < os_data.sequoia.value else "14.0 Beta 3-24"} if self._xnu_major >= os_data.sonoma.value else {}),
                    },
                    "/System/Library/PrivateFrameworks": {
                        **({  "MTLCompiler.framework": "13.2.1" } if self._xnu_major == os_data.ventura.value else {}),
                        **({  "GPUCompiler.framework": "13.2.1" } if self._xnu_major == os_data.ventura.value else {}),
                        "RenderBox.framework": "13.2.1-3802"      if self._xnu_major == os_data.ventura.value else "14.0-3802",

                        # More issues for 3802, now with 14.2 Beta 2+...
                        # If there is a god, they clearly despise us and legacy Macs.
                        **({  "MTLCompiler.framework": "14.2 Beta 1" } if self._xnu_float >= self.macOS_14_2 else {}),
                        **({  "GPUCompiler.framework": "14.2 Beta 1" } if self._xnu_float >= self.macOS_14_2 else {}),
                    },

                },
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks/PhotosUICore.framework/Versions/A/Resources": {
                        **({  "default.metallib": "14.6.1" } if self._xnu_major == os_data.sonoma.value else {}),
                    },
                }
            }
        }


    def _patches_metal_3802_metallibs(self) -> dict:
        """
        With macOS Sequoia, a new .metallib compiler format was introduced (V27)
        Thus we need to patch all .metallib files to support 3802 GPUs using MetallibSupportPkg

        Reference:
        https://github.com/dortania/MetallibSupportPkg
        """
        if self._xnu_major < os_data.sequoia.value:
            return {}

        return {
            "Metal 3802 .metallibs": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSCore.framework/Versions/A/Resources": {
                        "default.metallib": "14.6.1",
                    },
                    "/System/Library/Frameworks/MLCompute.framework/Versions/A/Resources": {
                        "default.metallib": "14.6.1"
                    },
                    "/System/Library/PrivateFrameworks/CoreUI.framework/Versions/A/Resources": {
                        "default.metallib": "14.6.1",
                    },
                    "/System/Library/Frameworks/CoreImage.framework/Versions/A": {
                        "CoreImage.metallib": "14.6.1",
                    },
                    "/System/Library/Frameworks/CoreImage.framework/Versions/A/Resources": {
                        "default.metallib":                    "14.6.1",
                        "ci_filters.metallib":                 "14.6.1",
                        "ci_stdlib_stitchable_h.metallib":     "14.6.1",
                        "ci_stdlib_stitchable.metallib":       "14.6.1",
                        "CIPortraitBlurStitchableV3.metallib": "14.6.1",
                        "CIPortraitBlurStitchableV2.metallib": "14.6.1",
                        "ci_stdlib_h.metallib":                "14.6.1",
                        "ci_filters_stitchable.metallib":      "14.6.1",
                        "CIPortraitBlurV2.metallib":           "14.6.1",
                        "CIPortraitBlurV3.metallib":           "14.6.1",
                        "ci_stdlib.metallib":                  "14.6.1",
                    },
                    "/System/Library/PrivateFrameworks/Tungsten.framework/Versions/A/Resources": {
                        "default.metallib": "15.0 Beta 7",
                    },
                    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources": {
                        "default.metallib": "15.0 Beta 8" if packaging.version.parse(self._marketing_version) < packaging.version.parse("15.1") else "15.1 Beta 4",
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/VFX.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/VisionKitInternal.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/TSReading.framework/Versions/A/Resources": {
                        "TSDDefaultMetalLibrary.metallib": DynamicPatchset.MetallibSupportPkg,
                        "KeynoteMetalLibrary.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/WeatherUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "ForegroundEffectShaders.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/AvatarKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/Tungsten.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/TextInputUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/ActivityRingsUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/ChatKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/WeatherMaps.framework/Versions/A/Resources": {
                        "WeatherMapsMetalLib.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/HomeAccessoryControlUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/PassKitUIFoundation.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/PrivateFrameworks/MediaCoreUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/Frameworks/ARKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/Frameworks/SpriteKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/Frameworks/PencilKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/Frameworks/SwiftUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/iOSSupport/System/Library/Frameworks/SceneKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Video/Plug-Ins/AppleGVAHEVCEncoder.bundle/Contents/Resources": {
                        "AppleGVAHEVCFrameStatistics.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Video/Plug-Ins/AV1DecoderSW.bundle/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Video/Plug-Ins/AppleAVEEncoder.bundle/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/CoreServices/MTLReplayer.app/Contents/Frameworks/MTLReplayController.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/CoreImage/CIPassThrough.cifilter/Contents/Resources": {
                        "CIPassThrough.ci.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/CoreImage/PortraitFilters.cifilter/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "portrait_filters.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/ScreenCaptureKitMetal/ScreenCaptureKitMetal.bundle/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/ExtensionKit/Extensions/Monterey.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/ExtensionKit/Extensions/Drift.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/ExtensionKit/Extensions/WallpaperMacintoshExtension.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/ExtensionKit/Extensions/WallpaperSequoiaExtension.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/SetupAssistantSupportUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/GESS.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VFX.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VisionCore.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/CoreRE.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/HDRProcessing.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/AvatarKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/Resources": {
                        "SkyLightShaders.air64.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/AppleISPEmulator.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/NeutrinoCore.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/ImageHarmonizationKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VideoProcessing.framework/Versions/A/PlugIns/Codecs/VCPRealtimeEncoder.bundle/Contents/Resources": {
                        "ProcessAccelerate.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VideoProcessing.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "ProcessAccelerate.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Portrait.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VisualGeneration.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "NonMaxLineSuppress.ci.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/AccelerateGPU.framework": {
                        "GPUBLAS.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/AccelerateGPU.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/ShaderGraph.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Hydra.framework/Plugins/HydraQLThumbnailExtension.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Hydra.framework/Plugins/HydraQLPreviewExtension.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Hydra.framework/Versions/C/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/SiriUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/TextRecognition.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Leonardo.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/metal_libraries": {
                        "AlloyCommonLibrary.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/GPUToolsCapture.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/PhotoImaging.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/PhotosUICore.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/MetalTools.framework/Versions/A/Resources": {
                        "MTLLegacySVICBSupport.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLGPUDebugICBSupport.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLGPUDebugAccelerationStructureSupport.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLDebugShaders.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLLegacySVAccelerationStructureSupport.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/AppleDepth.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Human.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/CorePhotogrammetry.framework/Versions/A/Resources": {
                        "ComputerVision_Tess_Kernels.metallib": DynamicPatchset.MetallibSupportPkg,
                        "Photogrammetry_Matching_Kernels.metallib": DynamicPatchset.MetallibSupportPkg,
                        "Photogrammetry_Texturing_Kernels.metallib": DynamicPatchset.MetallibSupportPkg,
                        "Photogrammetry_MVS_Kernels.metallib": DynamicPatchset.MetallibSupportPkg,
                        "Photogrammetry_Meshing_Kernels.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/HumanUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Quagga.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/Espresso.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/CMPhoto.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/MediaAnalysis.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/AltruisticBodyPoseKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/MusicUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/FRC.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/H13ISPServices.framework/Versions/A/Resources": {
                        "CalibrateRgbIr.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/SiriUICore.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/PassKitUIFoundation.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/H16ISPServices.framework/Versions/A/Resources": {
                        "CalibrateRgbIr.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/CoreOCModules.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/PhotosensitivityProcessing.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/PrivateFrameworks/MediaCoreUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/Metal.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLMeshShaderEmulator.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLBVHBuilder.metallib": DynamicPatchset.MetallibSupportPkg,
                        "MTLECBE.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/QuartzCore.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources/ACD.plugin/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSFunctions.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSRayIntersector.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSNeuralNetwork.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSNDArray.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSImage.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSMatrix.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/MetalFX.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/ParavirtualizedGraphics.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/ImageIO.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/SpriteKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/PencilKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/CoreDisplay.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/SwiftUICore.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/SwiftUI.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/Vision.framework/Versions/A/Resources": {
                        "ImageFilters.metallib": DynamicPatchset.MetallibSupportPkg,
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/StickerKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/VideoToolbox.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/Frameworks/SceneKit.framework/Versions/A/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Library/VideoProcessors/CCPortrait.bundle/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "CoreImageKernels_only.ci.metallib": DynamicPatchset.MetallibSupportPkg,
                        "CoreImageKernels.ci.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Applications/Music.app/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Applications/Chess.app/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Applications/Freeform.app/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                        "coreimage.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                    "/System/Applications/Freeform.app/Contents/Extensions/USDRendererExtension.appex/Contents/Resources": {
                        "default.metallib": DynamicPatchset.MetallibSupportPkg,
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources": [
                        # For some reason Ivy Bridge can't tell the metallib lacks AIR64 support, and errors out
                        "archive.metallib",
                    ],
                },
            }
        }


    def patches(self) -> dict:
        """
        Dictionary of patches
        """
        return {
            **self._patches_metal_3802_common(),
            **self._patches_metal_3802_common_extended(),
            **self._patches_metal_3802_metallibs(),
        }