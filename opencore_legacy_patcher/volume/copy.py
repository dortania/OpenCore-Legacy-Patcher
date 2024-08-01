"""
copy.py: Generate performant '/bin/cp' arguments for macOS
"""

from pathlib import Path

from .properties import PathAttributes


def can_copy_on_write(source: str, destination: str) -> bool:
    """
    Check if Copy on Write is supported between source and destination
    """
    source_obj = PathAttributes(source)
    return source_obj.mount_point() == PathAttributes(str(Path(destination).parent)).mount_point() and source_obj.supports_clonefile()


def generate_copy_arguments(source: str, destination: str) -> list:
    """
    Generate performant '/bin/cp' arguments for macOS
    """
    _command = ["/bin/cp", source, destination]
    if not Path(source).exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    if not Path(destination).parent.exists():
        raise FileNotFoundError(f"Destination directory not found: {destination}")

    # Check if Copy on Write is supported.
    if can_copy_on_write(source, destination):
        _command.insert(1, "-c")

    if Path(source).is_dir():
        _command.insert(1, "-R")

    return _command