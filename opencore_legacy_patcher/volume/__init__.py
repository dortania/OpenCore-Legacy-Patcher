"""
volume: Volume utilities for macOS

-------------------------------------------------------------------------------

Usage - Checking if Copy on Write is supported between source and destination:

>>> from volume import can_copy_on_write

>>> source = "/path/to/source"
>>> destination = "/path/to/destination"

>>> can_copy_on_write(source, destination)
True

-------------------------------------------------------------------------------

Usage - Generating copy arguments:

>>> from volume import generate_copy_arguments

>>> source = "/path/to/source"
>>> destination = "/path/to/destination"

>>> _command = generate_copy_arguments(source, destination)
>>> _command
['/bin/cp', '-c', '/path/to/source', '/path/to/destination']

-------------------------------------------------------------------------------

Usage - Querying volume properties:

>>> from volume import PathAttributes

>>> path = "/path/to/file"
>>> obj = PathAttributes(path)

>>> obj.mount_point()
"/"

>>> obj.supports_clonefile()
True
"""

from .properties import PathAttributes
from .copy import can_copy_on_write, generate_copy_arguments