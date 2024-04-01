"""
ioreg.py: PyObjc Handling for IOKit
"""

from typing import NewType, Union
import objc

from CoreFoundation import CFRelease, kCFAllocatorDefault  # type: ignore # pylint: disable=no-name-in-module
from Foundation import NSBundle  # type: ignore # pylint: disable=no-name-in-module
from PyObjCTools import Conversion

IOKit_bundle = NSBundle.bundleWithIdentifier_("com.apple.framework.IOKit")

# pylint: disable=invalid-name
io_name_t_ref_out = b"[128c]"  # io_name_t is char[128]
const_io_name_t_ref_in = b"r*"
CFStringRef = b"^{__CFString=}"
CFDictionaryRef = b"^{__CFDictionary=}"
CFAllocatorRef = b"^{__CFAllocator=}"
# pylint: enable=invalid-name

# https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html
functions = [
    ("IORegistryEntryCreateCFProperties", b"IIo^@" + CFAllocatorRef + b"I"),
    ("IOServiceMatching", CFDictionaryRef + b"r*"),
    ("IOServiceGetMatchingServices", b"II" + CFDictionaryRef + b"o^I"),
    ("IOIteratorNext", b"II"),
    ("IORegistryEntryGetParentEntry", b"IIr*o^I"),
    ("IOObjectRelease", b"II"),
    ("IORegistryEntryGetName", b"IIo" + io_name_t_ref_out),
    ("IOObjectGetClass", b"IIo" + io_name_t_ref_out),
    ("IOObjectCopyClass", CFStringRef + b"I"),
    ("IOObjectCopySuperclassForClass", CFStringRef + CFStringRef),
    ("IORegistryEntryGetChildIterator", b"IIr*o^I"),
    ("IORegistryCreateIterator", b"IIr*Io^I"),
    ("IORegistryEntryCreateIterator", b"IIr*Io^I"),
    ("IORegistryIteratorEnterEntry", b"II"),
    ("IORegistryIteratorExitEntry", b"II"),
    ("IORegistryEntryCreateCFProperty", b"@I" + CFStringRef + CFAllocatorRef + b"I"),
    ("IORegistryEntryGetPath", b"IIr*oI"),
    ("IORegistryEntryCopyPath", CFStringRef + b"Ir*"),
    ("IOObjectConformsTo", b"II" + const_io_name_t_ref_in),
    ("IORegistryEntryGetLocationInPlane", b"II" + const_io_name_t_ref_in + b"o" + io_name_t_ref_out),
    ("IOServiceNameMatching", CFDictionaryRef + b"r*"),
    ("IORegistryEntryGetRegistryEntryID", b"IIo^Q"),
    ("IORegistryEntryIDMatching", CFDictionaryRef + b"Q"),
    ("IORegistryEntryFromPath", b"II" + const_io_name_t_ref_in),
]

variables = [("kIOMasterPortDefault", b"I")]

# pylint: disable=invalid-name
pointer = type(None)

kern_return_t = NewType("kern_return_t", int)
boolean_t = int

io_object_t = NewType("io_object_t", object)
io_name_t = bytes
io_string_t = bytes

# io_registry_entry_t = NewType("io_registry_entry_t", io_object_t)
io_registry_entry_t = io_object_t
io_iterator_t = NewType("io_iterator_t", io_object_t)

CFTypeRef = Union[int, float, bytes, dict, list]

IOOptionBits = int
mach_port_t = int
CFAllocatorType = type(kCFAllocatorDefault)

NULL = 0

kIOMasterPortDefault: mach_port_t
kNilOptions: IOOptionBits = NULL

# IOKitLib.h
kIORegistryIterateRecursively = 1
kIORegistryIterateParents = 2

# pylint: enable=invalid-name


# kern_return_t IORegistryEntryCreateCFProperties(io_registry_entry_t entry, CFMutableDictionaryRef * properties, CFAllocatorRef allocator, IOOptionBits options);
def IORegistryEntryCreateCFProperties(entry: io_registry_entry_t, properties: pointer, allocator: CFAllocatorType, options: IOOptionBits) -> tuple[kern_return_t, dict]:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFMutableDictionaryRef IOServiceMatching(const char * name);
def IOServiceMatching(name: bytes) -> dict:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IOServiceGetMatchingServices(mach_port_t masterPort, CFDictionaryRef matching CF_RELEASES_ARGUMENT, io_iterator_t * existing);
def IOServiceGetMatchingServices(masterPort: mach_port_t, matching: dict, existing: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
    raise NotImplementedError


# io_object_t IOIteratorNext(io_iterator_t iterator);
def IOIteratorNext(iterator: io_iterator_t) -> io_object_t:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryGetParentEntry(io_registry_entry_t entry, const io_name_t plane, io_registry_entry_t * parent);
def IORegistryEntryGetParentEntry(entry: io_registry_entry_t, plane: io_name_t, parent: pointer) -> tuple[kern_return_t, io_registry_entry_t]:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IOObjectRelease(io_object_t object);
def IOObjectRelease(object: io_object_t) -> kern_return_t:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryGetName(io_registry_entry_t entry, io_name_t name);
def IORegistryEntryGetName(entry: io_registry_entry_t, name: pointer) -> tuple[kern_return_t, bytes]:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IOObjectGetClass(io_object_t object, io_name_t className);
def IOObjectGetClass(object: io_object_t, className: pointer) -> tuple[kern_return_t, bytes]:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFStringRef IOObjectCopyClass(io_object_t object);
def IOObjectCopyClass(object: io_object_t) -> str:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFStringRef IOObjectCopySuperclassForClass(CFStringRef classname)
def IOObjectCopySuperclassForClass(classname: str) -> str:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryGetChildIterator(io_registry_entry_t entry, const io_name_t plane, io_iterator_t * iterator);
def IORegistryEntryGetChildIterator(entry: io_registry_entry_t, plane: io_name_t, iterator: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryCreateIterator(mach_port_t masterPort, const io_name_t plane, IOOptionBits options, io_iterator_t * iterator)
def IORegistryCreateIterator(masterPort: mach_port_t, plane: io_name_t, options: IOOptionBits, iterator: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryCreateIterator(io_registry_entry_t entry, const io_name_t plane, IOOptionBits options, io_iterator_t * iterator)
def IORegistryEntryCreateIterator(entry: io_registry_entry_t, plane: io_name_t, options: IOOptionBits, iterator: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryIteratorEnterEntry(io_iterator_t iterator)
def IORegistryIteratorEnterEntry(iterator: io_iterator_t) -> kern_return_t:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryIteratorExitEntry(io_iterator_t iterator)
def IORegistryIteratorExitEntry(iterator: io_iterator_t) -> kern_return_t:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFTypeRef IORegistryEntryCreateCFProperty(io_registry_entry_t entry, CFStringRef key, CFAllocatorRef allocator, IOOptionBits options);
def IORegistryEntryCreateCFProperty(entry: io_registry_entry_t, key: str, allocator: CFAllocatorType, options: IOOptionBits) -> CFTypeRef:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryGetPath(io_registry_entry_t entry, const io_name_t plane, io_string_t path);
def IORegistryEntryGetPath(entry: io_registry_entry_t, plane: io_name_t, path: pointer) -> tuple[kern_return_t, io_string_t]:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFStringRef IORegistryEntryCopyPath(io_registry_entry_t entry, const io_name_t plane)
def IORegistryEntryCopyPath(entry: io_registry_entry_t, plane: bytes) -> str:  # pylint: disable=invalid-name
    raise NotImplementedError


# boolean_t IOObjectConformsTo(io_object_t object, const io_name_t className)
def IOObjectConformsTo(object: io_object_t, className: bytes) -> boolean_t:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryGetLocationInPlane(io_registry_entry_t entry, const io_name_t plane, io_name_t location)
def IORegistryEntryGetLocationInPlane(entry: io_registry_entry_t, plane: io_name_t, location: pointer) -> tuple[kern_return_t, bytes]:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFMutableDictionaryRef IOServiceNameMatching(const char * name);
def IOServiceNameMatching(name: bytes) -> dict:  # pylint: disable=invalid-name
    raise NotImplementedError


# kern_return_t IORegistryEntryGetRegistryEntryID(io_registry_entry_t entry, uint64_t * entryID)
def IORegistryEntryGetRegistryEntryID(entry: io_registry_entry_t, entryID: pointer) -> tuple[kern_return_t, int]:  # pylint: disable=invalid-name
    raise NotImplementedError


# CFMutableDictionaryRef IORegistryEntryIDMatching(uint64_t entryID);
def IORegistryEntryIDMatching(entryID: int) -> dict:  # pylint: disable=invalid-name
    raise NotImplementedError


# io_registry_entry_t IORegistryEntryFromPath(mach_port_t mainPort, const io_string_t path)
def IORegistryEntryFromPath(mainPort: mach_port_t, path: io_string_t) -> io_registry_entry_t:  # pylint: disable=invalid-name
    raise NotImplementedError


objc.loadBundleFunctions(IOKit_bundle, globals(), functions)  # type: ignore # pylint: disable=no-member
objc.loadBundleVariables(IOKit_bundle, globals(), variables)  # type: ignore # pylint: disable=no-member


def ioiterator_to_list(iterator: io_iterator_t):
    # items = []
    item = IOIteratorNext(iterator)  # noqa: F821
    while item:
        # items.append(next)
        yield item
        item = IOIteratorNext(iterator)  # noqa: F821
    IOObjectRelease(iterator)  # noqa: F821
    # return items


def corefoundation_to_native(collection):
    if collection is None:  # nullptr
        return None
    native = Conversion.pythonCollectionFromPropertyList(collection)
    CFRelease(collection)
    return native


def native_to_corefoundation(native):
    return Conversion.propertyListFromPythonCollection(native)


def io_name_t_to_str(name):
    return name.partition(b"\0")[0].decode()


def get_class_inheritance(io_object):
    classes = []
    cls = IOObjectCopyClass(io_object)
    while cls:
        # yield cls
        classes.append(cls)
        CFRelease(cls)
        cls = IOObjectCopySuperclassForClass(cls)
    return classes
