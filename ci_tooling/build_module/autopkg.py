from pathlib import Path

from opencore_legacy_patcher.support import subprocess_wrapper

class GenerateAutoPkg:

    def __init__(self) -> None:
        self._package_build_bin = "/usr/local/bin/packagesbuild"
        self._autopkg_config    = "./ci_tooling/autopkg/AutoPkg-Assets-Setup.pkgproj"


    def generate(self) -> None:
        """
        Generate AutoPkg Assets
        """
        print("Generating AutoPkg Assets")
        subprocess_wrapper.run_and_verify([self._package_build_bin, self._autopkg_config])