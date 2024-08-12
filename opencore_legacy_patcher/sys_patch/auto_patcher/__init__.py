"""
auto_patcher: Automatic system volume patching after updates, etc.

Usage:

>>> # Installing launch services
>>> from auto_patcher import InstallAutomaticPatchingServices
>>> InstallAutomaticPatchingServices(self.constants).install_auto_patcher_launch_agent()


>>> # When patching the system volume (ex. launch service)
>>> from auto_patcher import StartAutomaticPatching
>>> StartAutomaticPatching(self.constants).start_auto_patch()
"""

from .install import InstallAutomaticPatchingServices
from .start   import StartAutomaticPatching