"""
mount: Library for mounting and unmounting the root volume and interacting with APFS snapshots.

Usage:

>>> from mount import RootVolumeMount
>>> RootVolumeMount(xnu_major).mount()
'/System/Volumes/Update/mnt1'
>>> RootVolumeMount(xnu_major).unmount()

>>> RootVolumeMount(xnu_major).create_snapshot()
>>> RootVolumeMount(xnu_major).revert_snapshot()
"""

from .mount    import RootVolumeMount
from .snapshot import APFSSnapshot