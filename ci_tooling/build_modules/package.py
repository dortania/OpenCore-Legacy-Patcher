"""
package.py: Generate packages (Installer, Uninstaller, AutoPkg-Assets)
"""

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
        self._autopkg_files = {
            "./payloads/Launch Services/com.dortania.opencore-legacy-patcher.auto-patch.plist": "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist",
        }
        self._autopkg_files.update(self._files)


    def _generate_installer_welcome(self) -> str:
        """
        Generate Welcome message for installer PKG
        """
        _welcome = ""

        _welcome += "# Overview\n"
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


    def _generate_uninstaller_welcome(self) -> str:
        """
        Generate Welcome message for uninstaller PKG
        """
        _welcome = ""

        _welcome += "# Application Uninstaller\n"
        _welcome += "This package will uninstall the OpenCore Legacy Patcher application and its Privileged Helper Tool from your system."
        _welcome += "\n\n"
        _welcome += "This will not remove any root patches or OpenCore configurations that you may have installed using OpenCore Legacy Patcher."
        _welcome += "\n\n"
        _welcome += f"For more information on OpenCore Legacy Patcher, see our [documentation]({constants.Constants().guide_link}) and [GitHub repository]({constants.Constants().repo_link})."

        return _welcome


    def generate(self) -> None:
        """
        Generate OpenCore-Patcher.pkg
        """
        print("Generating OpenCore-Patcher-Uninstaller.pkg")
        assert macos_pkg_builder.Packages(
            pkg_output="./dist/OpenCore-Patcher-Uninstaller.pkg",
            pkg_bundle_id="com.dortania.opencore-legacy-patcher-uninstaller",
            pkg_version=constants.Constants().patcher_version,
            pkg_background="./ci_tooling/installation_pkg/PkgBackgroundUninstaller.png",
            pkg_preinstall_script="./ci_tooling/installation_pkg/uninstall.sh",
            pkg_as_distribution=True,
            pkg_title="OpenCore Legacy Patcher Uninstaller",
            pkg_welcome=self._generate_uninstaller_welcome(),
        ).build() is True

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
            pkg_welcome=self._generate_installer_welcome(),
        ).build() is True

        print("Generating AutoPkg-Assets.pkg")
        assert macos_pkg_builder.Packages(
            pkg_output="./dist/AutoPkg-Assets.pkg",
            pkg_bundle_id="com.dortania.pkg.AutoPkg-Assets",
            pkg_version=constants.Constants().patcher_version,
            pkg_allow_relocation=False,
            pkg_as_distribution=True,
            pkg_background="./ci_tooling/autopkg/PkgBackground.png",
            pkg_preinstall_script="./ci_tooling/autopkg/preinstall.sh",
            pkg_postinstall_script="./ci_tooling/autopkg/postinstall.sh",
            pkg_file_structure=self._autopkg_files,
            pkg_title="AutoPkg Assets",
            pkg_welcome="# DO NOT RUN AUTOPKG-ASSETS MANUALLY!\n\n## THIS CAN BREAK YOUR SYSTEM'S INSTALL!\n\nThis package should only ever be invoked by the Patcher itself, never downloaded or run by the user. Download the OpenCore-Patcher.pkg on the Github Repository.\n\n[OpenCore Legacy Patcher GitHub Release](https://github.com/dortania/OpenCore-Legacy-Patcher/releases/)",
        ).build() is True
