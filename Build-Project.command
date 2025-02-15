#!/usr/bin/env python3
"""
Build-Project.command: Generate OpenCore-Patcher.app and OpenCore-Patcher.pkg
"""

import os
import sys
import time
import argparse

from pathlib import Path

from ci_tooling.build_modules import (
    application,
    disk_images,
    package,
    sign_notarize
)


def main() -> None:
    """
    Parse Command Line Arguments
    """

    parser = argparse.ArgumentParser(description="Build OpenCore Legacy Patcher Suite", add_help=False)

    # Signing Parameters
    parser.add_argument("--application-signing-identity", type=str, help="Application Signing Identity")
    parser.add_argument("--installer-signing-identity", type=str, help="Installer Signing Identity")


    # Notarization Parameters
    parser.add_argument("--notarization-apple-id", type=str, help="Notarization Apple ID", default=None)
    parser.add_argument("--notarization-password", type=str, help="Notarization Password", default=None)
    parser.add_argument("--notarization-team-id", type=str, help="Notarization Team ID", default=None)

    # GitHub Actions CI/CD Parameters
    parser.add_argument("--git-branch", type=str, help="Git Branch", default=None)
    parser.add_argument("--git-commit-url", type=str, help="Git Commit URL", default=None)
    parser.add_argument("--git-commit-date", type=str, help="Git Commit Date", default=None)

    # Local Build Parameters
    parser.add_argument("--reset-dmg-cache", action="store_true", help="Redownload PatcherSupportPkg.dmg and regenerate payloads.dmg", default=False)
    parser.add_argument("--reset-pyinstaller-cache", action="store_true", help="Clean PyInstaller Cache", default=False)

    # CI/CD Parameters for individual steps
    # If not specified, will run all steps
    parser.add_argument("--run-as-individual-steps", action="store_true", help="CI: Run as individual steps", default=False)
    parser.add_argument("--prepare-application", action="store_true", help="CI: Prepare Application", default=False)
    parser.add_argument("--prepare-package", action="store_true", help="CI: Prepare Package", default=False)
    parser.add_argument("--prepare-assets", action="store_true", help="CI: Prepare Assets", default=False)

    # Analytics Parameters
    parser.add_argument("--analytics-key", type=str, help="Analytics Key", default=None)
    parser.add_argument("--analytics-endpoint", type=str, help="Analytics Endpoint", default=None)

    # Help
    parser.add_argument("--help", action="store_true", help="Show this help message and exit", default=False)

    # Parse Arguments
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        print("\n\nIf running outside of CI/CD, simply run the following command:")
        print("$ python3 Build-Project.command")
        sys.exit(0)

    # Set 'Current Working Directory' to script directory
    os.chdir(Path(__file__).resolve().parent)


    if (args.run_as_individual_steps is False) or (args.run_as_individual_steps and args.prepare_assets):
        # Prepare workspace
        disk_images.GenerateDiskImages(args.reset_dmg_cache).generate()

    if (args.run_as_individual_steps is False) or (args.run_as_individual_steps and args.prepare_application):
        # Prepare Privileged Helper Tool
        sign_notarize.SignAndNotarize(
            path=Path("./ci_tooling/privileged_helper_tool/com.dortania.opencore-legacy-patcher.privileged-helper"),
            signing_identity=args.application_signing_identity,
            notarization_apple_id=args.notarization_apple_id,
            notarization_password=args.notarization_password,
            notarization_team_id=args.notarization_team_id,
        ).sign_and_notarize()

        # Build OpenCore-Patcher.app
        application.GenerateApplication(
            reset_pyinstaller_cache=args.reset_pyinstaller_cache,
            git_branch=args.git_branch,
            git_commit_url=args.git_commit_url,
            git_commit_date=args.git_commit_date,
            analytics_key=args.analytics_key,
            analytics_endpoint=args.analytics_endpoint,
        ).generate()

        # Sign OpenCore-Patcher.app
        sign_notarize.SignAndNotarize(
            path=Path("dist/OpenCore-Patcher.app"),
            signing_identity=args.application_signing_identity,
            notarization_apple_id=args.notarization_apple_id,
            notarization_password=args.notarization_password,
            notarization_team_id=args.notarization_team_id,
            entitlements=Path("./ci_tooling/entitlements/entitlements.plist"),
        ).sign_and_notarize()


    if (args.run_as_individual_steps is False) or (args.run_as_individual_steps and args.prepare_package):
        # Build OpenCore-Patcher.pkg and OpenCore-Patcher-Uninstaller.pkg
        package.GeneratePackage().generate()

        # Sign OpenCore-Patcher.pkg
        sign_notarize.SignAndNotarize(
            path=Path("dist/OpenCore-Patcher.pkg"),
            signing_identity=args.installer_signing_identity,
            notarization_apple_id=args.notarization_apple_id,
            notarization_password=args.notarization_password,
            notarization_team_id=args.notarization_team_id,
        ).sign_and_notarize()

        # Sign OpenCore-Patcher-Uninstaller.pkg
        sign_notarize.SignAndNotarize(
            path=Path("dist/OpenCore-Patcher-Uninstaller.pkg"),
            signing_identity=args.installer_signing_identity,
            notarization_apple_id=args.notarization_apple_id,
            notarization_password=args.notarization_password,
            notarization_team_id=args.notarization_team_id,
        ).sign_and_notarize()


if __name__ == '__main__':
    _start = time.time()
    main()
    print(f"Build script completed in {str(round(time.time() - _start, 2))} seconds")