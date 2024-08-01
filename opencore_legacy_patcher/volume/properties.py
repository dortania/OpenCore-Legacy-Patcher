"""
properties.py: Query volume properties for a given path using macOS's getattrlist.
"""

import ctypes


class attrreference_t(ctypes.Structure):
    _fields_ = [
        ("attr_dataoffset", ctypes.c_int32),
        ("attr_length",     ctypes.c_uint32)
    ]

class attrlist_t(ctypes.Structure):
    _fields_ = [
        ("bitmapcount", ctypes.c_ushort),
        ("reserved",    ctypes.c_uint16),
        ("commonattr",  ctypes.c_uint),
        ("volattr",     ctypes.c_uint),
        ("dirattr",     ctypes.c_uint),
        ("fileattr",    ctypes.c_uint),
        ("forkattr",    ctypes.c_uint)
    ]

class volattrbuf(ctypes.Structure):
    _fields_ = [
        ("length",          ctypes.c_uint32),
        ("mountPoint",      attrreference_t),
        ("volCapabilities", ctypes.c_uint64),
        ("mountPointSpace", ctypes.c_char * 1024),
    ]


class PathAttributes:

    def __init__(self, path: str) -> None:
        self._path = path
        if not isinstance(self._path, str):
            try:
                self._path = str(self._path)
            except:
                raise ValueError(f"Invalid path: {path}")

        _libc = ctypes.CDLL("/usr/lib/libc.dylib")

        # Reference:
        # https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/getattrlist.2.html
        try:
            self._getattrlist = _libc.getattrlist
        except AttributeError:
            return

        self._getattrlist.argtypes = [
            ctypes.c_char_p,             # Path
            ctypes.POINTER(attrlist_t),  # Attribute list
            ctypes.c_void_p,             # Attribute buffer
            ctypes.c_ulong,              # Attribute buffer size
            ctypes.c_ulong               # Options
        ]
        self._getattrlist.restype = ctypes.c_int

        # Reference:
        # https://github.com/apple-oss-distributions/xnu/blob/xnu-10063.121.3/bsd/sys/attr.h
        ATTR_BIT_MAP_COUNT     = 0x00000005
        ATTR_VOL_MOUNTPOINT    = 0x00001000
        ATTR_VOL_CAPABILITIES  = 0x00020000

        attrList = attrlist_t()
        attrList.bitmapcount = ATTR_BIT_MAP_COUNT
        attrList.volattr     = ATTR_VOL_MOUNTPOINT | ATTR_VOL_CAPABILITIES

        volAttrBuf = volattrbuf()

        if self._getattrlist(self._path.encode(), ctypes.byref(attrList), ctypes.byref(volAttrBuf), ctypes.sizeof(volAttrBuf), 0) != 0:
            return

        self._volAttrBuf = volAttrBuf


    def supports_clonefile(self) -> bool:
        """
        Verify if path provided supports Apple's clonefile function.

        Equivalent to checking for Copy on Write support.
        """
        VOL_CAP_INT_CLONE = 0x00010000

        if not hasattr(self, "_volAttrBuf"):
            return False

        if self._volAttrBuf.volCapabilities & VOL_CAP_INT_CLONE:
            return True

        return False


    def mount_point(self) -> str:
        """
        Return mount point of path.
        """

        if not hasattr(self, "_volAttrBuf"):
            return ""

        mount_point_ptr = ctypes.cast(
            ctypes.addressof(self._volAttrBuf.mountPoint) + self._volAttrBuf.mountPoint.attr_dataoffset,
            ctypes.POINTER(ctypes.c_char * self._volAttrBuf.mountPoint.attr_length)
        )

        return mount_point_ptr.contents.value.decode()