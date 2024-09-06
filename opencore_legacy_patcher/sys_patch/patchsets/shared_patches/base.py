"""
base.py: Base class for shared patch sets
"""

from ..base import BasePatchset


class BaseSharedPatchSet(BasePatchset):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__()
        self._xnu_major = xnu_major
        self._xnu_minor = xnu_minor
        self._marketing_version = marketing_version

        self._xnu_float = float(f"{self._xnu_major}.{self._xnu_minor}")


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires patches
        """
        raise NotImplementedError


    def patches(self) -> dict:
        """
        Dictionary of patches
        """
        raise NotImplementedError