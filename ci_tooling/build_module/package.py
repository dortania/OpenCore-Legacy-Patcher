import macos_pkg_builder
from opencore_legacy_patcher import constants


class GeneratePackage:
    """
    Generate OpenCore-Patcher.pkg
    """

    def __init__(self) -> None:
        """
        Initialize
        """
        self._files = {
            "./dist/OpenCore-Patcher.app": "/Library/Application Support/Dortania/OpenCore-Patcher.app",
            "./ci_tooling/privileged_helper_tool/com.dortania.opencore-legacy-patcher.privileged-helper": "/Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper",
        }


    def _generate_welcome(self) -> str:
        """
        Generate Welcome message for PKG
        """
        _welcome = ""

        _welcome = "# Overview\n"
        _welcome += f"This package will install the OpenCore Legacy Patcher application (v{constants.Constants().patcher_version}) on your system."

        _welcome += "\n\nAdditionally, a shortcut for OpenCore Legacy Patcher will be added in the '/Applications' folder."
        _welcome += "\n\nThis package will not 'Build and Install OpenCore' or install any 'Root Patches' on your machine. If required, you can run OpenCore Legacy Patcher to install any patches you may need."
        _welcome += f"\n\nFor more information on OpenCore Legacy Patcher usage, see our [documentation]({constants.Constants().guide_link}) and [GitHub repository]({constants.Constants().repo_link})."
        _welcome += "\n\n"

        _welcome += "## Files Installed"
        _welcome += "\n\nInstallation of this package will add the following files to your system:"
        for key, value in self._files.items():
            _welcome += f"\n\n- `{value}`"

        return _welcome


    def generate(self) -> None:
        """
        Generate OpenCore-Patcher.pkg
        """
        print("Generating OpenCore-Patcher.pkg")
        assert macos_pkg_builder.Packages(
            pkg_output="./dist/OpenCore-Patcher.pkg",
            pkg_bundle_id="com.dortania.opencore-legacy-patcher",
            pkg_version=constants.Constants().patcher_version,
            pkg_allow_relocation=False,
            pkg_as_distribution=True,
            pkg_background="./ci_tooling/installation_pkg/PkgBackground.png",
            pkg_preinstall_script="./ci_tooling/installation_pkg/preinstall.sh",
            pkg_postinstall_script="./ci_tooling/installation_pkg/postinstall.sh",
            pkg_file_structure=self._files,
            pkg_title="OpenCore Legacy Patcher",
            pkg_welcome=self._generate_welcome(),
        ).build() is True