# Validate the integrity of Apple downloaded files via .chunklist and .integrityDataV1 files
# Based off of chunklist.py:
# - https://gist.github.com/dhinakg/cbe30edf31ddc153fd0b0c0570c9b041
# Copyright (C) 2021-2022, Dhinak G, Mykola Grymalyuk

import binascii
import hashlib
from pathlib import Path

CHUNK_LENGTH = 4 + 32


def generate_chunklist_dict(chunklist):
    chunklist = Path(chunklist).read_bytes() if isinstance(chunklist, str) else chunklist

    # Ref: https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.101.4/bsd/kern/chunklist.h#L59-L69
    header = {
        "magic":       chunklist[:4],
        "length":      int.from_bytes(chunklist[4:8], "little"),
        "fileVersion": chunklist[8],
        "chunkMethod": chunklist[9],
        "sigMethod":   chunklist[10],
        "chunkCount":  int.from_bytes(chunklist[12:20], "little"),
        "chunkOffset": int.from_bytes(chunklist[20:28], "little"),
        "sigOffset":   int.from_bytes(chunklist[28:36], "little")
    }

    if header["magic"] != b"CNKL":
        return None

    all_chunks = chunklist[header["chunkOffset"]:header["chunkOffset"]+header["chunkCount"]*CHUNK_LENGTH]
    chunks = [{"length": int.from_bytes(all_chunks[i:i+4], "little"), "checksum": all_chunks[i+4:i+CHUNK_LENGTH]} for i in range(0, len(all_chunks), CHUNK_LENGTH)]

    return chunks


def chunk(file_path, chunklist, verbose):
    chunks = generate_chunklist_dict(chunklist)
    if chunks is None:
        return False
    with Path(file_path).open("rb") as f:
        for chunk in chunks:
            status = hashlib.sha256(f.read(chunk["length"])).digest()
            if not status == chunk["checksum"]:
                print(
                    f"Chunk {chunks.index(chunk) + 1} checksum status FAIL: chunk sum {binascii.hexlify(chunk['checksum']).decode()}, calculated sum {binascii.hexlify(status).decode()}")
                return False
            elif verbose:
                print(
                    f"Chunk {chunks.index(chunk) + 1} checksum status success")
    return True