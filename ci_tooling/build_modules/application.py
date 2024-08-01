import sys
import time
import plistlib
import subprocess

from pathlib import Path

from opencore_legacy_patcher.volume  import generate_copy_arguments
from opencore_legacy_patcher.support import subprocess_wrapper


class GenerateApplication:
    """
    Generate OpenCore-Patcher.app
    """

    def __init__(self, reset_pyinstaller_cache: bool = False, git_branch: str = None, git_commit_url: str = None, git_commit_date: str = None, analytics_key: str = None, analytics_endpoint: str = None) -> None:
        """
        Initialize
        """
        self._pyinstaller = [sys.executable, "-m", "PyInstaller"]
        self._application_output = Path("./dist/OpenCore-Patcher.app")

        self._reset_pyinstaller_cache = reset_pyinstaller_cache

        self._git_branch = git_branch
        self._git_commit_url = git_commit_url
        self._git_commit_date = git_commit_date

        self._analytics_key = analytics_key
        self._analytics_endpoint = analytics_endpoint


    def _generate_application(self) -> None:
        """
        Generate PyInstaller Application
        """
        if self._application_output.exists():
            subprocess_wrapper.run_and_verify(["/bin/rm", "-rf", self._application_output], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("Generating OpenCore-Patcher.app")
        _args = self._pyinstaller + ["./OpenCore-Patcher-GUI.spec", "--noconfirm"]
        if self._reset_pyinstaller_cache:
            _args.append("--clean")

        subprocess_wrapper.run_and_verify(_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def _embed_analytics_key(self) -> None:
        """
        Embed analytics key
        """
        _file = Path("./opencore_legacy_patcher/support/analytics_handler.py")

        if not all([self._analytics_key, self._analytics_endpoint]):
            print("Analytics key or endpoint not provided, skipping embedding")
            return

        print("Embedding analytics data")
        if not Path(_file).exists():
            raise FileNotFoundError("analytics_handler.py not found")

        lines = []
        with open(_file, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith("SITE_KEY:         str = "):
                lines[i] = f"SITE_KEY:         str = \"{self._analytics_key}\"\n"
            elif line.startswith("ANALYTICS_SERVER: str = "):
                lines[i] = f"ANALYTICS_SERVER: str = \"{self._analytics_endpoint}\"\n"

        with open(_file, "w") as f:
            f.writelines(lines)


    def _remove_analytics_key(self) -> None:
        """
        Remove analytics key
        """
        _file = Path("./opencore_legacy_patcher/support/analytics_handler.py")

        if not all([self._analytics_key, self._analytics_endpoint]):
            return

        print("Removing analytics data")
        if not _file.exists():
            raise FileNotFoundError("analytics_handler.py not found")

        lines = []
        with open(_file, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith("SITE_KEY:         str = "):
                lines[i] = "SITE_KEY:         str = \"\"\n"
            elif line.startswith("ANALYTICS_SERVER: str = "):
                lines[i] = "ANALYTICS_SERVER: str = \"\"\n"

        with open(_file, "w") as f:
            f.writelines(lines)


    def _patch_load_command(self):
        """
        Patch LC_VERSION_MIN_MACOSX in Load Command to report 10.10

        By default Pyinstaller will create binaries supporting 10.13+
        However this limitation is entirely arbitrary for our libraries
        and instead we're able to support 10.10 without issues.

        To verify set version:
          otool -l ./dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher

              cmd LC_VERSION_MIN_MACOSX
          cmdsize 16
          version 10.13
              sdk 10.9
        """
        _file = self._application_output / "Contents" / "MacOS" / "OpenCore-Patcher"

        _find    = b'\x00\x0D\x0A\x00' # 10.13 (0xA0D)
        _replace = b'\x00\x0A\x0A\x00' # 10.10 (0xA0A)

        print("Patching LC_VERSION_MIN_MACOSX")
        with open(_file, "rb") as f:
            data = f.read()
            data = data.replace(_find, _replace, 1)

        with open(_file, "wb") as f:
            f.write(data)


    def _embed_git_data(self) -> None:
        """
        Embed git data
        """
        _file = self._application_output / "Contents" / "Info.plist"

        _git_branch = self._git_branch or "Built from source"
        _git_commit = self._git_commit_url or ""
        _git_commit_date = self._git_commit_date or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        print("Embedding git data")
        _plist = plistlib.load(_file.open("rb"))
        _plist["Github"] = {
            "Branch": _git_branch,
            "Commit URL": _git_commit,
            "Commit Date": _git_commit_date
        }
        plistlib.dump(_plist, _file.open("wb"), sort_keys=True)


    def _embed_resources(self) -> None:
        """
        Embed resources
        """
        print("Embedding resources")
        for file in Path("payloads/Icon/AppIcons").glob("*.icns"):
            subprocess_wrapper.run_and_verify(
                generate_copy_arguments(str(file), self._application_output / "Contents" / "Resources/"),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )


    def generate(self) -> None:
        """
        Generate OpenCore-Patcher.app
        """
        self._embed_analytics_key()
        self._generate_application()
        self._remove_analytics_key()

        self._patch_load_command()
        self._embed_git_data()
        self._embed_resources()
