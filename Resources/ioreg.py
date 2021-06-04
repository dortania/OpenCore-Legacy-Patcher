from dataclasses import dataclass
import plistlib
import subprocess
from typing import Any


@dataclass
class IORegistryEntry:
    name: str
    entry_class: str
    properties: dict
    location: str
    children: list
    parent: Any


class IOReg:
    def __init__(self):
        self.ioreg = plistlib.loads(subprocess.run("ioreg -a -l".split(), stdout=subprocess.PIPE).stdout.strip())
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

    def find(self, root=None, **kwargs):
        if not root:
            root = self.tree

        if not kwargs:
            return

        conditions = []

        if "name" in kwargs:
            conditions.append(kwargs["name"] == root.name)
        if "entry_class" in kwargs:
            conditions.append(kwargs["entry_class"] == root.entry_class)
        if "key" in kwargs:
            conditions.append(kwargs["key"] in root.properties)
        if "property" in kwargs:
            conditions.append(kwargs["property"][0] in root.properties and root.properties[kwargs["property"][0]] == kwargs["property"][1])

        if all(conditions):
            yield root

        for i in root.children:
            for j in self.find(i, **kwargs):
                yield j
