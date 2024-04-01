"""
cpu_data.py: CPU Generation Data
"""

import enum


class CPUGen(enum.IntEnum):
    pentium_4     = 0
    yonah         = 1
    conroe        = 2
    penryn        = 3
    nehalem       = 4    # (Westmere included)
    sandy_bridge  = 5    # 2000
    ivy_bridge    = 6    # 3000
    haswell       = 7    # 4000
    broadwell     = 8    # 5000
    skylake       = 9    # 6000
    kaby_lake     = 10   # 7000
    coffee_lake   = 11   # 8000/9000
    comet_lake    = 12   # 10000
    ice_lake      = 13   # 10000

    apple_dtk     = 100  # A12
    apple_silicon = 101  # A14 and newer (not tracked beyond this point)