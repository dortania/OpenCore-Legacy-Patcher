"""
sip_data.py: System Integrity Protection Data
"""

from . import os_data


class system_integrity_protection:
    csr_values = {
        # Source: macOS 11.4 (XNU's csr.h)
        # https://opensource.apple.com/source/xnu/xnu-7195.121.3/bsd/sys/csr.h.auto.html
        "CSR_ALLOW_UNTRUSTED_KEXTS": False,  #            0x1   - Allows Unsigned Kexts           - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_UNRESTRICTED_FS": False,  #            0x2   - File System Access              - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_TASK_FOR_PID": False,  #               0x4   - Unrestricted task_for_pid()     - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_KERNEL_DEBUGGER": False,  #            0x8   - Allow Kernel Debugger           - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_APPLE_INTERNAL": False,  #             0x10  - Set AppleInternal Features      - Introduced in El Capitan  # noqa: E241
        # "CSR_ALLOW_DESTRUCTIVE_DTRACE": False,  #       0x20  - Allow destructive DTrace        - Deprecated                # noqa: E241
        "CSR_ALLOW_UNRESTRICTED_DTRACE": False,  #        0x20  - Unrestricted DTrace usage       - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_UNRESTRICTED_NVRAM": False,  #         0x40  - Unrestricted NVRAM write        - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_DEVICE_CONFIGURATION": False,  #       0x80  - Allow custom DeviceTree (iOS)   - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_ANY_RECOVERY_OS": False,  #            0x100 - Skip BaseSystem Verification    - Introduced in Sierra      # noqa: E241
        "CSR_ALLOW_UNAPPROVED_KEXTS": False,  #           0x200 - Allow Unnotarized Kexts         - Introduced in High Sierra # noqa: E241
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE": False,  # 0x400 - Override Executable Policy      - Introduced in Mojave      # noqa: E241
        "CSR_ALLOW_UNAUTHENTICATED_ROOT": False,  #       0x800 - Allow Root Volume Mounting      - Introduced in Big Sur     # noqa: E241
    }

    csr_values_extended = {
        "CSR_ALLOW_UNTRUSTED_KEXTS": {
            "name": "CSR_ALLOW_UNTRUSTED_KEXTS",
            "description": "Allows Unsigned Kexts to be hot loaded from disk",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x1,
        },
        "CSR_ALLOW_UNRESTRICTED_FS": {
            "name": "CSR_ALLOW_UNRESTRICTED_FS",
            "description": "File System Access",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x2,
        },
        "CSR_ALLOW_TASK_FOR_PID": {
            "name": "CSR_ALLOW_TASK_FOR_PID",
            "description": "Unrestricted task_for_pid()",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x4,
        },
        "CSR_ALLOW_KERNEL_DEBUGGER": {
            "name": "CSR_ALLOW_KERNEL_DEBUGGER",
            "description": "Allow Kernel Debugger",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x8,
        },
        "CSR_ALLOW_APPLE_INTERNAL": {
            "name": "CSR_ALLOW_APPLE_INTERNAL",
            "description": "Set AppleInternal Features",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x10,
        },
        # "CSR_ALLOW_DESTRUCTIVE_DTRACE": {
        #     "name": "CSR_ALLOW_DESTRUCTIVE_DTRACE",
        #     "description": "Allow destructive DTrace",
        #     "deprecated": True,
        #     "introduced": os_data.os_data.el_capitan.value,
        #     "introduced_friendly": "El Capitan",
        #     "value": 0x20,
        # },
        "CSR_ALLOW_UNRESTRICTED_DTRACE": {
            "name": "CSR_ALLOW_UNRESTRICTED_DTRACE",
            "description": "Unrestricted DTrace usage",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x20,
        },
        "CSR_ALLOW_UNRESTRICTED_NVRAM": {
            "name": "CSR_ALLOW_UNRESTRICTED_NVRAM",
            "description": "Unrestricted NVRAM write",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x40,
        },
        "CSR_ALLOW_DEVICE_CONFIGURATION": {
            "name": "CSR_ALLOW_DEVICE_CONFIGURATION",
            "description": "Allow custom DeviceTree (iOS)",
            "introduced": os_data.os_data.el_capitan.value,
            "introduced_friendly": "El Capitan",
            "value": 0x80,
        },
        "CSR_ALLOW_ANY_RECOVERY_OS": {
            "name": "CSR_ALLOW_ANY_RECOVERY_OS",
            "description": "Skip BaseSystem Verification",
            "introduced": os_data.os_data.sierra.value,
            "introduced_friendly": "Sierra",
            "value": 0x100,
        },
        "CSR_ALLOW_UNAPPROVED_KEXTS": {
            "name": "CSR_ALLOW_UNAPPROVED_KEXTS",
            "description": "Allow Unnotarized Kexts to be hot loaded from disk",
            "introduced": os_data.os_data.high_sierra.value,
            "introduced_friendly": "High Sierra",
            "value": 0x200,
        },
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE": {
            "name": "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE",
            "description": "Override Executable Policy",
            "introduced": os_data.os_data.mojave.value,
            "introduced_friendly": "Mojave",
            "value": 0x400,
        },
        "CSR_ALLOW_UNAUTHENTICATED_ROOT": {
            "name": "CSR_ALLOW_UNAUTHENTICATED_ROOT",
            "description": "Allow Root Volume Mounting",
            "introduced": os_data.os_data.big_sur.value,
            "introduced_friendly": "Big Sur",
            "value": 0x800,
        },
    }

    root_patch_sip_mojave = [
        # Variables required to root patch in Mojave and Catalina
        "CSR_ALLOW_UNTRUSTED_KEXTS",  #            0x1   - Required for hot loading modded Kexts
        "CSR_ALLOW_UNRESTRICTED_FS",  #            0x2   - Mount and Edit System Partitions
        "CSR_ALLOW_UNAPPROVED_KEXTS",  #           0x200 - Required for hot loading modded Kexts
    ]

    root_patch_sip_big_sur = [
        # Variables required to root patch in Big Sur and Monterey
        "CSR_ALLOW_UNRESTRICTED_FS",  #            0x2   - Required to mount and edit root volume, as well as load modded platform binaries
        "CSR_ALLOW_UNAUTHENTICATED_ROOT",  #       0x800 - Required to avoid KC mismatch kernel panic
    ]

    root_patch_sip_big_sur_3rd_part_kexts = [
        # Variables required to root patch in Big Sur and Monterey with 3rd party kexts
        "CSR_ALLOW_UNTRUSTED_KEXTS",  #            0x1   - Required for Aux Cache in Big Sur+
        "CSR_ALLOW_UNRESTRICTED_FS",  #            0x2   - Required to mount and edit root volume, as well as load modded platform binaries
        "CSR_ALLOW_UNAUTHENTICATED_ROOT",  #       0x800 - Required to avoid KC mismatch kernel panic
        "CSR_ALLOW_UNAPPROVED_KEXTS",  #           0x200 - Required for Aux Cache in Big Sur+
    ]

    root_patch_sip_ventura = [
        # Variables required to root patch in Ventura
        "CSR_ALLOW_UNTRUSTED_KEXTS",  #            0x1   - Required for Aux Cache in Big Sur+
        "CSR_ALLOW_UNRESTRICTED_FS",  #            0x2   - Required to mount and edit root volume, as well as load modded platform binaries
        "CSR_ALLOW_UNAUTHENTICATED_ROOT",  #       0x800 - Required to avoid KC mismatch kernel panic
    ]


    # CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE (introduced with Mojave):
    # This bit is quite strange and was originally assumed to be required for modded platform binaries
    # However after extensive testing, this doesn't seem true. In addition, this bit is never flipped via
    # 'csrutil disable'. Usage within the kernel is not present.