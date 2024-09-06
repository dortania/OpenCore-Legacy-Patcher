"""
utilities.py: Supporting functions for file handling during root volume patching
"""

import logging
import subprocess

from pathlib import Path

from ..patchsets.base import PatchType

from ...volume  import generate_copy_arguments
from ...support import subprocess_wrapper


def install_new_file(source_folder: Path, destination_folder: Path, file_name: str, method: PatchType) -> None:
    """
    Installs a new file to the destination folder

    File handling logic:
    - PatchType.MERGE_* are merged with the destination folder
    - Other files are deleted and replaced

    Parameters:
        source_folder      (Path): Path to the source folder
        destination_folder (Path): Path to the destination folder
        file_name           (str): Name of the file to install
    """

    file_name_str = str(file_name)

    if not Path(destination_folder).exists():
        logging.info(f"  - Skipping {file_name}, cannot locate {source_folder}")
        return

    if method in [PatchType.MERGE_SYSTEM_VOLUME, PatchType.MERGE_DATA_VOLUME]:
        # merge with rsync
        logging.info(f"  - Installing: {file_name}")
        subprocess_wrapper.run_as_root(["/usr/bin/rsync", "-r", "-i", "-a", f"{source_folder}/{file_name}", f"{destination_folder}/"], stdout=subprocess.PIPE)
        fix_permissions(destination_folder + "/" + file_name)
    elif Path(source_folder + "/" + file_name_str).is_dir():
        # Applicable for .kext, .app, .plugin, .bundle, all of which are directories
        if Path(destination_folder + "/" + file_name).exists():
            logging.info(f"  - Found existing {file_name}, overwriting...")
            subprocess_wrapper.run_as_root_and_verify(["/bin/rm", "-R", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            logging.info(f"  - Installing: {file_name}")
        subprocess_wrapper.run_as_root_and_verify(generate_copy_arguments(f"{source_folder}/{file_name}", destination_folder), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        fix_permissions(destination_folder + "/" + file_name)
    else:
        # Assume it's an individual file, replace as normal
        if Path(destination_folder + "/" + file_name).exists():
            logging.info(f"  - Found existing {file_name}, overwriting...")
            subprocess_wrapper.run_as_root_and_verify(["/bin/rm", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            logging.info(f"  - Installing: {file_name}")
        subprocess_wrapper.run_as_root_and_verify(generate_copy_arguments(f"{source_folder}/{file_name}", destination_folder), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        fix_permissions(destination_folder + "/" + file_name)


def remove_file(destination_folder: Path, file_name: str) -> None:
    """
    Removes a file from the destination folder

    Parameters:
        destination_folder (Path): Path to the destination folder
        file_name           (str): Name of the file to remove
    """

    if Path(destination_folder + "/" + file_name).exists():
        logging.info(f"  - Removing: {file_name}")
        if Path(destination_folder + "/" + file_name).is_dir():
            subprocess_wrapper.run_as_root_and_verify(["/bin/rm", "-R", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            subprocess_wrapper.run_as_root_and_verify(["/bin/rm", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def fix_permissions(destination_file: Path) -> None:
    """
    Fix file permissions for a given file or directory
    """

    chmod_args = ["/bin/chmod",      "-Rf", "755", destination_file]
    chown_args = ["/usr/sbin/chown", "-Rf", "root:wheel", destination_file]
    if not Path(destination_file).is_dir():
        # Strip recursive arguments
        chmod_args.pop(1)
        chown_args.pop(1)
    subprocess_wrapper.run_as_root_and_verify(chmod_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess_wrapper.run_as_root_and_verify(chown_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
