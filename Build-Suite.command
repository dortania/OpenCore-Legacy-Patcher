#!/usr/bin/env python3
"""
Build-Suite.command: Generate OpenCore-Patcher.app and OpenCore-Patcher.pkg
"""

import os
import time
import argparse

from pathlib import Path

from ci_tooling.build_module import (
    application,
    disk_images,
    package,
    sign_notarize
)


def main() -> None:
    """
    Parse Command Line Arguments
    """

    parser = argparse.ArgumentParser(description="Build OpenCore Legacy Patcher Suite")

    # Code Signing Parameters
    # - Application Signing Identity
    # - Installer Signing Identity
    parser.add_argument("--application-signing-identity", type=str, help="Application Signing Identity")
    parser.add_argument("--installer-signing-identity", type=str, help="Installer Signing Identity")


    # Notarization Parameters
    # - Notarization Apple ID
    # - Notarization Password
    # - Notarization Team ID
    parser.add_argument("--notarization-apple-id", type=str, help="Notarization Apple ID", default=None)
    parser.add_argument("--notarization-password", type=str, help="Notarization Password", default=None)
    parser.add_argument("--notarization-team-id", type=str, help="Notarization Team ID", default=None)

    # GitHub Actions CI/CD Parameters
    # - Git Branch
    # - Git Commit
    # - Git Commit Date
    parser.add_argument("--git-branch", type=str, help="Git Branch", default=None)
    parser.add_argument("--git-commit-url", type=str, help="Git Commit URL", default=None)
    parser.add_argument("--git-commit-date", type=str, help="Git Commit Date", default=None)

    # Local Build Parameters
    # - Reset payloads.dmg
    # - Clean PyInstaller Cache
    parser.add_argument("--reset-dmg-cache", action="store_true", help="Redownload PatcherSupportPkg.dmg and regenerate payloads.dmg", default=False)
    parser.add_argument("--reset-pyinstaller-cache", action="store_true", help="Clean PyInstaller Cache", default=False)

    # Analytics Parameters
    # - Key
    # - Site
    parser.add_argument("--analytics-key", type=str, help="Analytics Key", default=None)
    parser.add_argument("--analytics-endpoint", type=str, help="Analytics Endpoint", default=None)

    # Parse Arguments
    args = parser.parse_args()

    # Set 'Current Working Directory' to script directory
    os.chdir(Path(__file__).resolve().parent)

    # Prepare workspace
    disk_images.GenerateDiskImages(args.reset_dmg_cache).generate()

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

    # Build OpenCore-Patcher.pkg
    package.GeneratePackage().generate()

    # Sign OpenCore-Patcher.pkg
    sign_notarize.SignAndNotarize(
        path=Path("dist/OpenCore-Patcher.pkg"),
        signing_identity=args.installer_signing_identity,
        notarization_apple_id=args.notarization_apple_id,
        notarization_password=args.notarization_password,
        notarization_team_id=args.notarization_team_id,
    ).sign_and_notarize()


if __name__ == '__main__':
    _start = time.time()
    main()
    print(f"Build script completed in {str(round(time.time() - _start, 2))} seconds")