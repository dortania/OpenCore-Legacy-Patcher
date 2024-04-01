"""
amfi_data.py: AppleMobileFileIntegrity Bitmask Data
"""

"""
Within AppleMobileFileIntegrity.kext, Apple has a bitmask-based boot-arg (ex. amfi=128)
Below information is from reversed values in 13.0 Beta 6's AppleMobileFileIntegrity.kext
Currently only 'amfi=3' has been used by Apple publicly
- 0x3 used in 11.0.1 dyld source:
  - https://github.com/apple-oss-distributions/dyld/blob/5c9192436bb195e7a8fe61f22a229ee3d30d8222/testing/test-cases/kernel-hello-world.dtest/main.c#L2
"""

import enum


class AppleMobileFileIntegrity(enum.IntEnum):
    # Names set are solely for readability
    # Internal names are unknown
    AMFI_ALLOW_TASK_FOR_PID:      int = 0x1   # Allow Task for PID (alt. amfi_unrestrict_task_for_pid=0x1)
    AMFI_ALLOW_INVALID_SIGNATURE: int = 0x2   # Reduce sig enforcement (alt. amfi_allow_any_signature=0x1)
    AMFI_LV_ENFORCE_THIRD_PARTY:  int = 0x4   # Don't mark external binaries as platform binaries
    AMFI_UNKNOWN_1:               int = 0x8
    AMFI_UNKNOWN_2:               int = 0x10
    AMFI_UNKNOWN_3:               int = 0x20
    AMFI_UNKNOWN_4:               int = 0x40
    AMFI_ALLOW_EVERYTHING:        int = 0x80  # Disable sig enforcement and Library Validation (alt. amfi_get_out_of_my_way=0x1)

"""
Internally within AMFI.kext, Apple references 0x2 and 0x80 as both 'Disable signature enforcement'
However 0x80 is a higher privilege than 0x2, and breaks TCC support in OS (ex. Camera, Microphone, etc prompts)

Supported boot-args within AMFI.kext, last compared against 13.0 Beta 6

  Within _initializeAppleMobileFileIntegrity():
    - amfi_unrestrict_task_for_pid=0x1
    - amfi_dev_mode_policy=0x1
    - amfi_allow_any_signature=0x1
    - amfi_get_out_of_my_way=0x1
    - amfi_unrestricted_local_signing=0x1
    - pmap_cs_unrestricted_local_signing=0x1
    - amfi_ready_to_roll=0x1
    - cs_enforcement_disable=0x1

  Within AMFIInitializeLocalSigningPublicKey():
    - -restore

  Within macOSPolicyConfigurationInit():
    - amfi_force_policy=0x1
    - amfi_block_unsigned_code=0x1
    - amfi_force_cs_kill=0x1
    - amfi_hsp_disable=0x1
    - amfi_hsp_logging=0x1
    - amfi_allow_bni_as_platform=0x1
    - amfi_allow_non_platform=0x1
    - amfi_prevent_old_entitled_platform_binaries=0x1
    - amfi_allow_only_tc=0x1
    - amfi_allow_only_tc_override=0x1

  Within configurationSettingsInit()
    - amfi_enforce_launch_constraints=0x1
    - amfi_allow_3p_launch_constraints=0x1
    - BATS_TESTPLAN_ID="Custom Team ID"
"""