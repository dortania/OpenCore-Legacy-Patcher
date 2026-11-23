"""
metal_3802.py: Metal 3802 patches
"""

import packaging.version

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class LegacyMetal3802(BaseSharedPatchSet):

    _SERVICE_PAYLOADS = {
        os_data.ventura: "13.7.8-3802",
        os_data.sonoma:  "14.8.9-3802",
        os_data.sequoia: "15.8.2-3802",
        os_data.tahoe:   "26.7.2-3802",
    }

    def _os_requires_patches(self) -> bool:
        return self._xnu_major in self._SERVICE_PAYLOADS
    

    def requires_unpatch(self, oclp_plist: dict) -> bool:
        if not oclp_plist.keys():
             return False
         
        installed_version = packaging.version.parse(oclp_plist["OpenCore Legacy Patcher"])

        if installed_version < packaging.version.parse("3.0.0"): 
            return True

        return False

    def patches(self) -> dict:
        if not self._os_requires_patches():
            return {}

        source = self._SERVICE_PAYLOADS[self._xnu_major]

        # readd the 3802 path to MTLCompilerService
        overwrite = {
            "/System/Library/Frameworks/Metal.framework/Versions/A/XPCServices": {"MTLCompilerService.xpc": source},
        }

        # readd the 3802 GPUCompiler and MTLCompiler libraries
        merge = {
            "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions": {"3802": "12.7.6"},
            "/System/Library/PrivateFrameworks/MTLCompiler.framework/Versions": {"3802": "12.7.6"},
        }

        # install the 3802 serializer, sequoia+ also needs translation for larger structs in Metal
        if self._xnu_major >= os_data.sequoia.value:
            merge["/System/Library/PrivateFrameworks/MTLCompiler.framework/Versions/3802/Libraries"] = {"libMTL3802DriverCompat.dylib": source}
        else:
            merge["/System/Library/PrivateFrameworks/MTLCompiler.framework/Versions/3802/Libraries"] = {"libMTLCompilerRestore.dylib": source}

        if self._xnu_major == os_data.ventura.value:
            # ventura's sandbox needs explicit whitelisting of our new paths, newer versions dont
            overwrite["/System/Library/Sandbox/Profiles"] = {"com.apple.mtlcompilerservice.sb": source}
            # ventura has a bug in 31001 that breaks air 2.0 downgrading for 3802
            overwrite["/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/31001/Libraries"] = {"libGPUCompilerImpl.dylib": source}

        return {
            "Metal 3802 Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: overwrite,
                PatchType.MERGE_SYSTEM_VOLUME: merge,
            },
        }
