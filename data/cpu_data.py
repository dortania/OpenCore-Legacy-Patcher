import enum


class cpu_data(enum.IntEnum):
    pentium_4 = 0
    yonah = 1
    conroe = 2
    penryn = 3
    nehalem = 4  # (Westmere included)
    sandy_bridge = 5  #     2000
    ivy_bridge = 6  #       3000
    haswell = 7  #       4000
    broadwell = 8  #       5000
    skylake = 9  #       6000
    kaby_lake = 10  #       7000
    coffee_lake = 11  #     8000
    comet_lake = 12  #       9000
    ice_lake = 13  #        10000

    apple_dtk = 112  # A12
    apple_m1 = 114  # A14
    apple_m1_pro = 115
    apple_m1_max = 116
    apple_m1_ultra = 117
