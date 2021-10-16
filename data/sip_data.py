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

    root_patch_sip_mojave = [
        # Variables required to root patch in Mojave and Catalina
        "CSR_ALLOW_UNTRUSTED_KEXTS",  #            0x1
        "CSR_ALLOW_UNRESTRICTED_FS",  #            0x2
        "CSR_ALLOW_UNAPPROVED_KEXTS",  #           0x200
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE",  # 0x400
    ]

    root_patch_sip_big_sur = [
        # Variables required to root patch in Big Sur and Monterey
        "CSR_ALLOW_UNTRUSTED_KEXTS",  #            0x1
        "CSR_ALLOW_UNRESTRICTED_FS",  #            0x2
        "CSR_ALLOW_UNAPPROVED_KEXTS",  #           0x200
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE",  # 0x400
        "CSR_ALLOW_UNAUTHENTICATED_ROOT",  #       0x800
    ]
