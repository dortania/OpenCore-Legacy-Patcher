from __future__ import annotations

import plistlib
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Generator


@dataclass
class IORegistryEntry:
    name: str
    entry_class: str
    properties: dict
    location: str
    children: list[IORegistryEntry]
    parent: IORegistryEntry


class IOReg:
    def __init__(self):
        try:
            self.ioreg = plistlib.loads(subprocess.run("ioreg -a -l".split(), stdout=subprocess.PIPE).stdout.strip())
        except Exception:
            fd, file_path = tempfile.mkstemp(suffix=".plist")
            with open(fd, "wb") as file_obj:
                file_obj.write(subprocess.run("ioreg -a -l".split(), stdout=subprocess.PIPE).stdout.strip())

            subprocess.run("plutil -convert binary1".split() + [file_path])
            self.ioreg = plistlib.load(Path(file_path).open("rb"))
        self.tree = self.recurse(self.ioreg, None)

    def recurse(self, entry, parent):
        converted = IORegistryEntry(
            entry["IORegistryEntryName"],
            entry["IOObjectClass"],
            {
                i: v
                for i, v in entry.items()
                if i
                not in [
                    "IOServiceBusyState",
                    "IOServiceBusyTime",
                    "IOServiceState",
                    "IORegistryEntryLocation",
                    "IORegistryEntryName",
                    "IORegistryEntryID",
                    "IOObjectClass",
                    "IORegistryEntryChildren",
                    "IOObjectRetainCount",
                ]
            },
            entry.get("IORegistryEntryLocation"),
            [],
            parent,
        )

        for i in entry.get("IORegistryEntryChildren", []):
            converted.children.append(self.recurse(i, converted))

        return converted

    def parse_conditions(self, entry: IORegistryEntry, **kwargs):
        conditions = []
        if "parent" in kwargs:
            conditions.append(self.parse_conditions(entry.parent, **kwargs["parent"]))
        if "children" in kwargs:
            conditions.append(any(self.parse_conditions(i, **kwargs["children"]) for i in entry.children))
        if "name" in kwargs:
            conditions.append(kwargs["name"] == entry.name)
        if "entry_class" in kwargs:
            conditions.append(kwargs["entry_class"] == entry.entry_class)
        if "key" in kwargs:
            conditions.append(kwargs["key"] in entry.properties)
        if "property" in kwargs:
            conditions.append(kwargs["property"][0] in entry.properties and entry.properties[kwargs["property"][0]] == kwargs["property"][1])

        return all(conditions)

    def find(self, root: IORegistryEntry = None, **kwargs) -> Generator[IORegistryEntry, None, None]:
        if not root:
            root = self.tree

        if not kwargs:
            return

        if self.parse_conditions(root, **kwargs):
            yield root

        for i in root.children:
            for j in self.find(i, **kwargs):
                yield j
