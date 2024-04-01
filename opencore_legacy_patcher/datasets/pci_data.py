"""
pci_data.py: PCI Device IDs for different vendors and devices
"""


class nvidia_ids:
    # Courteous of envytools as well as MacRumors:
    # https://envytools.readthedocs.io/en/latest/hw/pciid.html
    # https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/
    # https://pci-ids.ucw.cz/read/PC/10de
    curie_ids = [
        0x0040,  # NV40 [GeForce 6800 Ultra]
        0x00f0,  # BR02
        0x0220,  # NV44A
        0x0140,  # NV43 [GeForce 6600 GT]
        0x0160,  # NV44 [GeForce 6500]
        0x0090,  # G70 [GeForce 7800 GTX]
        0x01d0,  # G72 [GeForce 7350 LE]
        0x0390,  # G73 [GeForce 7650 GS]
        0x0290,  # G71 [GeForce 7900 GTX]
    ]

    tesla_ids = [
        # G80
        0x0190,  # G80 [GeForce 8800 GTS / 8800 GTX]
        0x0191,  # G80 [GeForce 8800 GTX]
        0x0193,  # G80 [GeForce 8800 GTS]
        0x0194,  # G80 [GeForce 8800 Ultra]
        0x019E,  # G80GL [Quadro FX 4600]
        0x019D,  # G80GL [Quadro FX 5600]
        # G84
        0x0400,  # G84 [8600 GTS]
        0x0401,  # G84 [8600 GT]
        0x0402,  # G84 [8600 GT]
        0x0403,  # G84 [8600 GS]
        0x0404,  # G84 [8400 GS]
        0x0405,  # G84 [9500M GS]
        0x0406,  # G84 [8300 GS]
        0x0407,  # G84 [8600M GT]
        0x0408,  # G84 [9650M GS]
        0x0409,  # G84 [8700M GT]
        0x040A,  # G84 [FX 370]
        0x040B,  # G84 [NVS 320M]
        0x040C,  # G84 [FX 570M]
        0x040D,  # G84 [FX 1600M]
        0x040E,  # G84 [FX 570]
        0x040F,  # G84 [FX 1700]
        # G86
        0x0420,  # G86 [8400 SE]
        0x0421,  # G86 [8500 GT]
        0x0422,  # G86 [8400 GS]
        0x0423,  # G86 [8300 GS]
        0x0424,  # G86 [8400 GS]
        0x0425,  # G86 [8600M GS]
        0x0426,  # G86 [8400M GT]
        0x0427,  # G86 [8400M GS]
        0x0428,  # G86 [8400M G]
        0x0429,  # G86 [NVS 140M]
        0x042A,  # G86 [NVS 130M]
        0x042B,  # G86 [NVS 135M]
        0x042C,  # G86 [9400 GT]
        0x042D,  # G86 [FX 360M]
        0x042E,  # G86 [9300M G]
        0x042F,  # G86 [NVS 290]
        # G92
        0x0410,  # G92 [GT 330]
        0x0600,  # G92 [8800 GTS 512]
        0x0601,  # G92 [9800 GT]
        0x0602,  # G92 [8800 GT]
        0x0603,  # G92 [GT 230]
        0x0604,  # G92 [9800 GX2]
        0x0605,  # G92 [9800 GT]
        0x0606,  # G92 [8800 GS]
        0x0607,  # G92 [GTS 240]
        0x0608,  # G92 [9800M GTX]
        0x0609,  # G92 [8800M GTS]
        0x060A,  # G92 [GTX 280M]
        0x060B,  # G92 [9800M GT]
        0x060C,  # G92 [8800M GTX]
        0x060F,  # G92 [GTX 285M]
        0x0610,  # G92 [9600 GSO]
        0x0611,  # G92 [8800 GT]
        0x0612,  # G92 [9800 GTX/9800 GTX+]
        0x0613,  # G92 [9800 GTX+]
        0x0614,  # G92 [9800 GT]
        0x0615,  # G92 [GTS 250]
        0x0617,  # G92 [9800M GTX]
        0x0618,  # G92 [GTX 260M]
        0x0619,  # G92 [FX 4700 X2]
        0x061A,  # G92 [FX 3700]
        0x061B,  # G92 [VX 200]
        0x061C,  # G92 [FX 3600M]
        0x061D,  # G92 [FX 2800M]
        0x061E,  # G92 [FX 3700M]
        0x061F,  # G92 [FX 3800M]
        # G94
        0x0621,  # G94 [GT 230]
        0x0622,  # G94 [9600 GT]
        0x0623,  # G94 [9600 GS]
        0x0624,  # G94 [9600 GT Green Edition]
        0x0625,  # G94 [9600 GSO 512]
        0x0626,  # G94 [GT 130]
        0x0627,  # G94 [GT 140]
        0x0628,  # G94 [9800M GTS]
        0x062A,  # G94 [9700M GTS]
        0x062B,  # G94 [9800M GS]
        0x062C,  # G94 [9800M GTS ]
        0x062D,  # G94 [9600 GT]
        0x062E,  # G94 [9600 GT]
        0x062F,  # G94 [9800 S]
        0x0631,  # G94 [GTS 160M]
        0x0635,  # G94 [9600 GSO]
        0x0637,  # G94 [9600 GT]
        0x0638,  # G94 [FX 1800]
        0x063A,  # G94 [FX 2700M]
        # G96
        0x0640,  # G96 [9500 GT]
        0x0641,  # G96 [9400 GT]
        0x0643,  # G96 [9500 GT]
        0x0644,  # G96 [9500 GS]
        0x0645,  # G96 [9500 GS]
        0x0646,  # G96 [GT 120]
        0x0647,  # G96 [9600M GT]
        0x0648,  # G96 [9600M GS]
        0x0649,  # G96 [9600M GT]
        0x064A,  # G96 [9700M GT]
        0x064B,  # G96 [9500M G]
        0x064C,  # G96 [9650M GT]
        0x0651,  # G96 [G 110M]
        0x0652,  # G96 [GT 130M]
        0x0653,  # G96 [GT 120M]
        0x0654,  # G96 [GT 220M]
        0x0655,  # G96 [GT 120]
        0x0656,  # G96 [GT 120 ]
        0x0658,  # G96 [FX 380]
        0x0659,  # G96 [FX 580]
        0x065A,  # G96 [FX 1700M]
        0x065B,  # G96 [9400 GT]
        0x065C,  # G96 [FX 770M]
        0x065F,  # G96 [G210]
        # G98
        0x06E0,  # G98 [9300 GE]
        0x06E1,  # G98 [9300 GS]
        0x06E2,  # G98 [8400]
        0x06E3,  # G98 [8400 SE]
        0x06E4,  # G98 [8400 GS]
        0x06E5,  # G98M [9300M GS]
        0x06E6,  # G98 [G100]
        0x06E7,  # G98 [9300 SE]
        0x06E8,  # G98 [9200M GS]
        0x06E9,  # G98 [9300M GS]
        0x06EA,  # G98 [NVS 150M]
        0x06EB,  # G98 [NVS 160M]
        0x06EC,  # G98 [G 105M]
        0x06ED,  # G98 [9600 GT / 9800 GT]
        0x06EF,  # G98 [G 103M]
        0x06F1,  # G98 [G105M]
        0x06F8,  # G98 [NVS 420]
        0x06F9,  # G98 [FX 370 LP]
        0x06FA,  # G98 [NVS 450]
        0x06FB,  # G98 [FX 370M]
        0x06FD,  # G98 [NVS 295]
        0x06FF,  # G98 [HICx16]
        # GT200
        0x05E0,  # GT200 [GTX 295]
        0x05E1,  # GT200 [GTX 280]
        0x05E2,  # GT200 [GTX 260]
        0x05E3,  # GT200 [GTX 285]
        0x05E6,  # GT200 [GTX 275]
        0x05E7,  # GT200 [C1060]
        0x05E9,  # GT200 [CX]
        0x05EA,  # GT200 [GTX 260]
        0x05EB,  # GT200 [GTX 295]
        0x05ED,  # GT200 [FX 5800]
        0x05EE,  # GT200 [FX 4800]
        0x05EF,  # GT200 [FX 3800]
        0x05FD,  # GT200GL [Quadro FX 5800]
        0x05FE,  # GT200GL [Quadro FX 4800]
        0x05FF,  # GT200GL [Quadro FX 3800]
        # MCP77 GPU
        0x0840,  # MCP77 GPU [8200M]
        0x0844,  # MCP77 GPU [9100M G]
        0x0845,  # MCP77 GPU [8200M G]
        0x0846,  # MCP77 GPU [9200]
        0x0847,  # MCP77 GPU [9100]
        0x0848,  # MCP77 GPU [8300]
        0x0849,  # MCP77 GPU [8200]
        0x084A,  # MCP77 GPU [730A]
        0x084B,  # MCP77 GPU [9200]
        0x084C,  # MCP77 GPU [980A/780A SLI]
        0x084D,  # MCP77 GPU [750A SLI]
        0x084F,  # MCP77 GPU [8100 / 720A]
        # MCP79 GPU
        0x0860,  # MCP79 GPU [9400]
        0x0861,  # MCP79 GPU [9400]
        0x0862,  # MCP79 GPU [9400M G]
        0x0863,  # MCP79 GPU [9400M]
        0x0864,  # MCP79 GPU [9300]
        0x0865,  # MCP79 GPU [ION]
        0x0866,  # MCP79 GPU [9400M G]
        0x0867,  # MCP79 GPU [9400]
        0x0868,  # MCP79 GPU [760i SLI]
        0x0869,  # MCP79 GPU [9400]
        0x086A,  # MCP79 GPU [9400]
        0x086C,  # MCP79 GPU [9300 / 730i]
        0x086D,  # MCP79 GPU [9200]
        0x086E,  # MCP79 GPU [9100M G]
        0x086F,  # MCP79 GPU [8200M G]
        0x0870,  # MCP79 GPU [9400M]
        0x0871,  # MCP79 GPU [9200]
        0x0872,  # MCP79 GPU [G102M]
        0x0873,  # MCP79 GPU [G102M]
        0x0874,  # MCP79 GPU [ION]
        0x0876,  # MCP79 GPU [ION]
        0x087A,  # MCP79 GPU [9400]
        0x087D,  # MCP79 GPU [ION]
        0x087E,  # MCP79 GPU [ION LE]
        0x087F,  # MCP79 GPU [ION LE]
        # GT215
        0x0CA0,  # GT215 [GT 330]
        0x0CA2,  # GT215 [GT 320]
        0x0CA3,  # GT215 [GT 240]
        0x0CA4,  # GT215 [GT 340]
        0x0CA5,  # GT215 [GT 220]
        0x0CA7,  # GT215 [GT 330]
        0x0CA9,  # GT215 [GTS 250M]
        0x0CAC,  # GT215 [GT 220]
        0x0CAF,  # GT215 [GT 335M]
        0x0CB0,  # GT215 [GTS 350M]
        0x0CB1,  # GT215 [GTS 360M]
        0x0CBC,  # GT215 [FX 1800M]
        # GT216
        0x0A20,  # GT216 [GT 220]
        0x0A22,  # GT216 [315]
        0x0A23,  # GT216 [210]
        0x0A26,  # GT216 [405]
        0x0A27,  # GT216 [405]
        0x0A28,  # GT216 [GT 230M]
        0x0A29,  # GT216 [GT 330M]
        0x0A2A,  # GT216 [GT 230M]
        0x0A2B,  # GT216 [GT 330M]
        0x0A2C,  # GT216 [NVS 5100M]
        0x0A2D,  # GT216 [GT 320M]
        0x0A32,  # GT216 [GT 415]
        0x0A34,  # GT216 [GT 240M]
        0x0A35,  # GT216 [GT 325M]
        0x0A38,  # GT216 [400]
        0x0A3C,  # GT216 [FX 880M]
        # GT218
        0x0A60,  # GT218 [G210]
        0x0A62,  # GT218 [205]
        0x0A63,  # GT218 [310]
        0x0A64,  # GT218 [ION]
        0x0A65,  # GT218 [210]
        0x0A66,  # GT218 [310]
        0x0A67,  # GT218 [315]
        0x0A68,  # GT218 [G105M]
        0x0A69,  # GT218 [G105M]
        0x0A6A,  # GT218 [NVS 2100M]
        0x0A6C,  # GT218 [NVS 3100M]
        0x0A6E,  # GT218 [305M]
        0x0A6F,  # GT218 [ION]
        0x0A70,  # GT218 [310M]
        0x0A71,  # GT218 [305M]
        0x0A72,  # GT218 [310M]
        0x0A73,  # GT218 [305M]
        0x0A74,  # GT218 [G210M]
        0x0A75,  # GT218 [310M]
        0x0A76,  # GT218 [ION]
        0x0A78,  # GT218 [FX 380 LP]
        0x0A7A,  # GT218 [315M]
        0x0A7C,  # GT218 [FX 380M]
        0x10C0,  # GT218 [9300 GS]
        0x10C3,  # GT218 [8400GS]
        0x10C5,  # GT218 [405]
        0x10D8,  # GT218 [NVS 300]
        # MCP89 GPU
        0x08A0,  # MCP89 GPU [320M]
        0x08A2,  # MCP89 GPU [320M]
        0x08A3,  # MCP89 GPU [320M]
        0x08A4,  # MCP89 GPU [320M]
    ]

    fermi_ids = [
        # GF100
        0x06C0,  # GF100 [GTX 480]
        0x06C4,  # GF100 [GTX 465]
        0x06CA,  # GF100 [GTX 480M]
        0x06CB,  # GF100 [GTX 480]
        0x06CD,  # GF100 [GTX 470]
        0x06D1,  # GF100 [C2050 / C2070]
        0x06D2,  # GF100 [M2070]
        0x06D8,  # GF100 [6000]
        0x06D9,  # GF100 [5000]
        0x06DA,  # GF100 [5000M]
        0x06DC,  # GF100 [6000]
        0x06DD,  # GF100 [4000]
        0x06DE,  # GF100 [T20]
        0x06DF,  # GF100 [M2070-Q]
        # GF104
        0x0E22,  # GF104 [GTX 460]
        0x0E23,  # GF104 [GTX 460 SE]
        0x0E24,  # GF104 [GTX 460 OEM]
        0x0E30,  # GF104 [GTX 470M]
        0x0E31,  # GF104 [GTX 485M]
        0x0E3A,  # GF104 [3000M]
        0x0E3B,  # GF104 [4000M]
        # GF114
        0x1200,  # GF114 [GTX 560 Ti]
        0x1201,  # GF114 [GTX 560]
        0x1202,  # GF114 [GTX 560 Ti OEM]
        0x1203,  # GF114 [GTX 460 SE v2]
        0x1205,  # GF114 [GTX 460 v2]
        0x1206,  # GF114 [GTX 555]
        0x1207,  # GF114 [GT 645 OEM]
        0x1208,  # GF114 [GTX 560 SE]
        0x1210,  # GF114 [GTX 570M]
        0x1211,  # GF114 [GTX 580M]
        0x1212,  # GF114 [GTX 675M]
        0x1213,  # GF114 [GTX 670M]
        # GF106
        0x0DC0,  # GF106 [GT 440]
        0x0DC4,  # GF106 [GTS 450]
        0x0DC5,  # GF106 [GTS 450]
        0x0DC6,  # GF106 [GTS 450]
        0x0DCD,  # GF106 [GT 555M]
        0x0DCE,  # GF106 [GT 555M]
        0x0DD1,  # GF106 [GTX 460M]
        0x0DD2,  # GF106 [GT 445M]
        0x0DD3,  # GF106 [GT 435M]
        0x0DD6,  # GF106 [GT 550M]
        0x0DD8,  # GF106 [2000]
        0x0DDA,  # GF106 [2000M]
        # GF116
        0x1241,  # GF116 [GT 545 OEM]
        0x1243,  # GF116 [GT 545]
        0x1244,  # GF116 [GTX 550 Ti]
        0x1245,  # GF116 [GTS 450 Rev. 2]
        0x1246,  # GF116 [GT 550M]
        0x1247,  # GF116 [GT 635M]
        0x1248,  # GF116 [GT 555M]
        0x1249,  # GF116 [GTS 450 Rev. 3]
        0x124B,  # GF116 [GT 640 OEM]
        0x124D,  # GF116 [GT 555M]
        0x1251,  # GF116 [GTX 560M]
        # GF108
        0x0DE0,  # GF108 [GT 440]
        0x0DE1,  # GF108 [GT 430]
        0x0DE2,  # GF108 [GT 420]
        0x0DE3,  # GF108 [GT 635M]
        0x0DE4,  # GF108 [GT 520]
        0x0DE5,  # GF108 [GT 530]
        0x0DE8,  # GF108 [GT 620M]
        0x0DE9,  # GF108 [GT 630M]
        0x0DEA,  # GF108 [610M]
        0x0DEB,  # GF108 [GT 555M]
        0x0DEC,  # GF108 [GT 525M]
        0x0DED,  # GF108 [GT 520M]
        0x0DEE,  # GF108 [GT 415M]
        0x0DEF,  # GF108 [NVS 5400M]
        0x0DF0,  # GF108 [GT 425M]
        0x0DF1,  # GF108 [GT 420M]
        0x0DF2,  # GF108 [GT 435M]
        0x0DF3,  # GF108 [GT 420M]
        0x0DF4,  # GF108 [GT 540M]
        0x0DF5,  # GF108 [GT 525M]
        0x0DF6,  # GF108 [GT 550M]
        0x0DF7,  # GF108 [GT 520M]
        0x0DF8,  # GF108 [600]
        0x0DF9,  # GF108 [500M]
        0x0DFA,  # GF108 [1000M]
        0x0DFC,  # GF108 [NVS 5200M]
        0x0F00,  # GF108 [GT 630]
        0x0F01,  # GF108 [GT 620]
        0x0F02,  # GF108 [GT 730]
        # GF110
        0x1080,  # GF110 [GTX 580]
        0x1081,  # GF110 [GTX 570]
        0x1082,  # GF110 [GTX 560 Ti]
        0x1084,  # GF110 [GTX 560]
        0x1086,  # GF110 [GTX 570]
        0x1087,  # GF110 [GTX 560 Ti]
        0x1088,  # GF110 [GTX 590]
        0x1089,  # GF110 [GTX 580]
        0x108B,  # GF110 [GTX 580]
        0x1091,  # GF110 [M2090]
        0x1096,  # GF110GL [Tesla C2050 / C2075]
        0x109A,  # GF110 [5010M]
        0x109B,  # GF110 [7000]
        # GF119
        0x1040,  # GF119 [GT 520]
        0x1042,  # GF119 [510]
        0x1048,  # GF119 [605]
        0x1049,  # GF119 [GT 620]
        0x104A,  # GF119 [GT 610]
        0x104B,  # GF119 [GT 625 OEM]
        0x104C,  # GF119 [GT 705]
        0x1050,  # GF119 [GT 520M]
        0x1051,  # GF119 [GT 520MX]
        0x1052,  # GF119 [GT 520M]
        0x1054,  # GF119 [410M]
        0x1055,  # GF119 [410M]
        0x1056,  # GF119 [NVS 4200M]
        0x1057,  # GF119 [NVS 4200M]
        0x1058,  # GF119 [610M]
        0x1059,  # GF119 [610M]
        0x105A,  # GF119 [610M]
        0x105B,  # GF119M [705M]
        0x107C,  # GF119 [NVS 315]
        0x107D,  # GF119 [NVS 310]
        # GF117
        0x1140,  # GF117 [GT 620M]
    ]

    kepler_ids = [
        # GK104
        0x1180,  # GK104 [GTX 680]
        0x1182,  # GK104 [GTX 760 Ti]
        0x1183,  # GK104 [GTX 660 Ti]
        0x1184,  # GK104 [GTX 770]
        0x1185,  # GK104 [GTX 660]
        0x1186,  # GK104 [GTX 660 Ti]
        0x1187,  # GK104 [GTX 760]
        0x1188,  # GK104 [GTX 690]
        0x1189,  # GK104 [GTX 670]
        0x118a,  # GK104GL [GRID K520]
        0x118b,  # GK104GL [GRID K2 GeForce USM]
        0x118c,  # GK104 [GRID K2 NVS USM]
        0x118d,  # GK104GL [GRID K200 vGPU]
        0x118E,  # GK104 [GTX 760 OEM]
        0x118F,  # GK104GL [Tesla K10]
        0x1191,  # GK104 [GTX 760 Rev. 2]
        0x1193,	 # GK104 [GTX 760 Ti OEM]
        0x1194,  # GK104GL [Tesla K8]
        0x1195,  # GK104 [GTX 660 Rev. 2]
        0x1198,  # GK104M [GTX 880M]
        0x1199,  # GK104M [GTX 870M]
        0x119A,  # GK104M [GTX 860M]
        0x119D,  # GK104M [GTX 775M Mac Edition]
        0x119E,  # GK104M [GTX 780M Mac Edition]
        0x119F,  # GK104 [GTX 780M]
        0x11A0,  # GK104 [GTX 680M]
        0x11A1,  # GK104 [GTX 670MX]
        0x11A2,  # GK104 [GTX 675MX Mac Edition]
        0x11A3,  # GK104 [GTX 680MX]
        0x11A7,  # GK104 [GTX 675MX]
        0x11A8,  # GK104GLM [Quadro K5100M]
        0x11A9,  # GK104M [GTX 870M]
        0x11AF,  # GK104GLM [GRID IceCube]
        0x11B0,  # GK104GL [GRID K240Q / K260Q vGPU]
        0x11B1,  # GK104GL [GRID K2 Tesla USM]
        0x11B4,  # GK104GL [Quadro K4200]
        0x11B6,  # GK104GLM [Quadro K3100M]
        0x11B7,  # GK104GLM [Quadro K4100M]
        0x11B8,  # GK104GLM [Quadro K5100M]
        0x11B9,  # GK104GLM
        0x11BA,  # GK104GL [Quadro K5000]
        0x11BC,  # GK104GLM [Quadro K5000M]
        0x11BD,  # GK104GLM [Quadro K4000M]
        0x11BE,  # GK104GLM [Quadro K3000M]
        0x11BF,  # GK104 [GRID K2]
        # GK106
        0x11C0,  # GK106 [GTX 660]
        0x11C2,  # GK106 [GTX 650 Ti BOOST]
        0x11c3,  # GK106 [GTX 650 Ti OEM]
        0x11c4,  # GK106 [GTX 645 OEM]
        0x11c5,  # GK106 [GT 740]
        0x11C6,  # GK106 [GTX 650 Ti]
        0x11C7,  # GK106 [GTX 750 Ti]
        0x11C8,  # GK106 [GTX 650 OEM]
        0x11E0,  # GK106 [GTX 770M]
        0x11CB,  # GK106 [GT 740]
        0x11E0,  # GK106M [GTX 770M]
        0x11E1,  # GK106M [GTX 765M]
        0x11E2,  # GK106M [GTX 765M]
        0x11E3,  # GK106M [GTX 760M]
        0x11E7,  # GK106M
        0x11FA,  # GK106GL [Quadro K4000]
        0x11FC,  # GL106GLM [Quadro K2100M]
        # GK107
        0x0FC0,  # GK107 [GT 640]
        0x0FC1,  # GK107 [GT 640]
        0x0FC2,  # GK107 [GT 630]
        0x0FC5,  # GK107 [GT 1030]
        0x0FC6,  # GK107 [GTX 650]
        0x0FC8,  # GK107 [GT 740]
        0x0FC9,  # GK107 [GT 730]
        0x0FCD,  # GK107M [GT 755M]
        0x0FCE,  # GK107M [GT 640M LE]
        0x0FD1,  # GK107 [GT 650M]
        0x0FD2,  # GK107 [GT 640M]
        0x0FD3,  # GK107 [GT 640M LE]
        0x0FD4,  # GK107 [GTX 660M]
        0x0FD5,  # GK107 [GT 650M]
        0x0FD6,  # GK107M
        0x0FD8,  # GK107 [GT 640M]
        0x0FD9,  # GK107 [GT 645M]
        0x0FDB,  # GK107M
        0x0FDF,  # GK107M [GT 740M]
        0x0FE0,  # GK107 [GTX 660M]
        0x0FE1,  # GK107M [GT 730M]
        0x0FE2,  # GK107M [GT 745M]
        0x0FE3,  # GK107M [GT 745M]
        0x0FE4,  # GK107M [GT 750M]
        0x0FE5,  # GK107 [GeForce K340 USM]
        0x0FE6,  # GK107 [GRID K1 NVS USM]
        0x0FE7,  # GK107GL [GRID K100 vGPU]
        0x0FE8,  # GK107M [N14P-GS]
        0x0FE9,  # GK107 [GT 750M Mac Edition]
        0x0FEA,  # GK107M [GT 755M Mac Edition]
        0x0FEC,  # GK107M [710A]
        0x0FEE,  # GK107M [810M]
        0x0FED,  # GK107M [820M]
        0x0FEF,  # GK107GL [GRID K340]
        0x0FF1,  # GK107 [NVS 1000]
        0x0FF2,  # GK107GL [GRID K1]
        0x0FF3,  # GK107GL [Quadro K420]
        0x0FF5,  # GK107GL [GRID K1 Tesla USM]
        0x0FF6,  # GK107GLM [Quadro K1100M]
        0x0FF7,  # GK107GL [GRID K140Q vGPU]
        0x0FF8,  # GK107GLM [Quadro K500M]
        0x0FF9,  # GK107 [K2000D]
        0x0FFA,  # GK107 [K600]
        0x0FFB,  # GK107 [K2000M]
        0x0FFC,  # GK107 [K1000M]
        0x0FFD,  # GK107 [NVS 510]
        0x0FFE,  # GK107 [Quadro K2000]
        0x0FFF,  # GK107 [Quadro 410]
        # GK110
        0x1001,  # GK110B [GTX TITAN Z]
        0x1003,  # GK110 [GTX Titan LE]
        0x1004,  # GK110 [GTX 780]
        0x1005,  # GK110 [GTX Titan]
        0x1007,  # GK110 [GTX 780 Rev. 2]
        0x1008,  # GK110 [GTX 780 Ti 6GB]
        0x100A,  # GK110B [GTX 780 Ti]
        0x100C,  # GK110B [GTX TITAN Black]
        0x101E,  # GK110GL [Tesla K20X]
        0x101F,  # GK110GL [Tesla K20]
        0x1020,  # GK110GL [Tesla K20X]
        0x1021,  # GK110GL [Tesla K20Xm]
        0x1022,  # GK110GL [Tesla K20C]
        0x1023,  # GK110BGL [Tesla K40m]
        0x1026,  # GK110GL [Tesla K20s]
        0x1027,  # GK110BGL [Tesla K40st]
        0x1028,  # GK110GL [Tesla K20m]
        0x1029,  # GK110BGL [Tesla K40s]
        0x102A,  # GK110BGL [Tesla K40t]
        0x102E,  # GK110BGL [Tesla K40d]
        0x102F,  # GK110BGL [Tesla Stella Solo]
        0x103A,  # GK110GL [Quadro K6000]
        0x103C,  # GK110GL [Quadro K5200]
        0x103F,  # GK110BGL [Tesla Stella SXM]
        # GK180
        0x1024,  # GK180GL [Tesla K40c]
        # GK208
        0x1280,  # GK208 [GT 635]
        0x1281,  # GK208 [GT 710]
        0x1282,  # GK208 [GT 640 REv. 2]
        0x1284,  # GK208 [GT 630 REv. 2]
        0x1286,  # GK208 [GT 720]
        0x1287,  # GK208B [GT 730]
        0x1288,  # GK208B [GT 720]
        0x1289,  # GK208 [GT 710]
        0x128A,  # GK208B
        0x128B,  # GK208B [GT 710]
        0x128C,  # GK208B
        0x1290,  # GK208 [GT 730M]
        0x1291,  # GK208 [GT 735M]
        0x1292,  # GK208 [GT 740M]
        0x1293,  # GK208 [GT 730M]
        0x1294,  # GK208 [GT 740M]
        0x1295,  # GK208 [710M]
        0x1296,  # GK208M [825M]
        0x1298,  # GK208M [GT 720M]
        0x1299,  # GK208BM [920M]
        0x129A,  # GK208BM [910M]
        0x12A0,  # GK208
        0x12B9,  # GK208 [K610M]
        0x12BA,  # GK208 [K510M]
        # GK210
        0x102D,  # GK210GL [Tesla K80]
    ]


    maxwell_ids = [
        0x1340,	# GM108M [GeForce 830M]
        0x1341,	# GM108M [GeForce 840M]
        0x1344,	# GM108M [GeForce 845M]
        0x1346,	# GM108M [GeForce 930M]
        0x1347,	# GM108M [GeForce 940M]
        0x1348,	# GM108M [GeForce 945M / 945A]
        0x1349,	# GM108M [GeForce 930M]
        0x134b,	# GM108M [GeForce 940MX]
        0x134d,	# GM108M [GeForce 940MX]
        0x134e,	# GM108M [GeForce 930MX]
        0x134f,	# GM108M [GeForce 920MX]
        0x137a,	# GM108GLM [Quadro K620M / Quadro M500M]
        0x137b,	# GM108GLM [Quadro M520 Mobile]
        0x137d,	# GM108M [GeForce 940A]
        0x174d, # GM108M [GeForce MX130]
        0x174e, # GM108M [GeForce MX110]

        0x1380,	# GM107 [GTX 750 Ti]
        0x1381,	# GM107 [GTX 750]
        0x1382,	# GM107 [GTX 745]
        0x1389,	# GM107GL [GRID M30]
        0x1390,	# GM107M [GeForce 845M]
        0x1391,	# GM107M [GTX 850M]
        0x1392,	# GM107M [GTX 860M]
        0x1393,	# GM107M [GeForce 840M]
        0x1398,	# GM107M [GeForce 845M]
        0x1399,	# GM107M [GeForce 945M]
        0x139a,	# GM107M [GTX 950M]
        0x139b,	# GM107M [GTX 960M]
        0x139c,	# GM107M [GeForce 940M]
        0x139d,	# GM107M [GTX 750 Ti]
        0x13b0,	# GM107GLM [Quadro M2000M]
        0x13b1,	# GM107GLM [Quadro M1000M]
        0x13b2,	# GM107GLM [Quadro M600M]
        0x13b3,	# GM107GLM [Quadro K2200M]
        0x13b4,	# GM107GLM [Quadro M620 Mobile]
        0x13b6,	# GM107GLM [Quadro M1200 Mobile]
        0x13b9,	# GM107GL [NVS 810]
        0x13ba,	# GM107GL [Quadro K2200]
        0x13bb,	# GM107GL [Quadro K620]
        0x13bc,	# GM107GL [Quadro K1200]
        0x13bd,	# GM107GL [Tesla M10]
        0x1789, # GM107GL [GRID M3-3020]
        0x179c, # GM107 [GeForce 940MX]

        0x17c2, # GM200 [GTX TITAN X]
        0x17c8, # GM200 [GTX 980 Ti]
        0x17f0,	# GM200GL [Quadro M6000]
        0x17f1, # GM200GL [Quadro M6000 24GB]
        0x17fd, # GM200GL [Tesla M40]

        0x13c0,	# GM204 [GTX 980]
        0x13c1,	# GM204
        0x13c2,	# GM204 [GTX 970]
        0x13c3,	# GM204
        0x13d7,	# GM204M [GTX 980M]
        0x13d8,	# GM204M [GTX 970M]
        0x13d9,	# GM204M [GTX 965M]
        0x13da,	# GM204M [GTX 980 Mobile]
        0x13e7,	# GM204GL [GTX 980 Engineering Sample]
        0x13f0,	# GM204GL [Quadro M5000]
        0x13f1,	# GM204GL [Quadro M4000]
        0x13f2,	# GM204GL [Tesla M60]
        0x13f3,	# GM204GL [Tesla M6]
        0x13f8,	# GM204GLM [Quadro M5000M / M5000 SE]
        0x13f9,	# GM204GLM [Quadro M4000M]
        0x13fa,	# GM204GLM [Quadro M3000M]
        0x13fb,	# GM204GLM [Quadro M5500]

        0x1401,	# GM206 [GTX 960]
        0x1402,	# GM206 [GTX 950]
        0x1404,	# GM206 [GTX 960 FAKE]
        0x1406,	# GM206 [GTX 960 OEM]
        0x1407,	# GM206 [GTX 750 v2]
        0x1427,	# GM206M [GTX 965M]
        0x1430,	# GM206GL [Quadro M2000]
        0x1431,	# GM206GL [Tesla M4]
        0x1436,	# GM206GLM [Quadro M2200 Mobile]
    ]

    pascal_ids = [
        0x1725,
        0x172e,
        0x172f,
        0x15f0,	# GP100GL [Quadro GP100]
        0x15f1,	# GP100GL
        0x15f7,	# GP100GL [Tesla P100 PCIe 12GB]
        0x15f8,	# GP100GL [Tesla P100 PCIe 16GB]
        0x15f9,	# GP100GL [Tesla P100 SXM2 16GB]

        0x1b00,	# GP102 [TITAN X]
        0x1b01,	# GP102 [GTX 1080 Ti 10GB]
        0x1b02,	# GP102 [TITAN Xp]
        0x1b04,	# GP102
        0x1b06,	# GP102 [GTX 1080 Ti]
        0x1b07,	# GP102 [P102-100]
        0x1b30,	# GP102GL [Quadro P6000]
        0x1b38,	# GP102GL [Tesla P40]
        0x1b39,	# GP102GL [Tesla P10]
        0x1b70,	# GP102GL
        0x1b78,	# GP102GL

        0x1b80,	# GP104 [GTX 1080]
        0x1b81,	# GP104 [GTX 1070]
        0x1b82,	# GP104 [GTX 1070 Ti]
        0x1b83,	# GP104 [GTX 1060 6GB]
        0x1b84,	# GP104 [GTX 1060 3GB]
        0x1b87,	# GP104 [P104-100]
        0x1ba0,	# GP104M [GTX 1080 Mobile]
        0x1ba1,	# GP104M [GTX 1070 Mobile]
        0x1ba2,	# GP104M [GTX 1070 Mobile]
        0x1ba9,	# GP104M
        0x1baa,	# GP104M
        0x1bad,	# GP104 [GTX 1070 Engineering Sample]
        0x1bb0,	# GP104GL [Quadro P5000]
        0x1bb1,	# GP104GL [Quadro P4000]
        0x1bb3,	# GP104GL [Tesla P4]
        0x1bb4,	# GP104GL [Tesla P6]
        0x1bb5,	# GP104GLM [Quadro P5200 Mobile]
        0x1bb6,	# GP104GLM [Quadro P5000 Mobile]
        0x1bb7,	# GP104GLM [Quadro P4000 Mobile]
        0x1bb8,	# GP104GLM [Quadro P3000 Mobile]
        0x1bb9,	# GP104GLM [Quadro P4200 Mobile]
        0x1bbb,	# GP104GLM [Quadro P3200 Mobile]
        0x1bc7,	# GP104 [P104-101]
        0x1be0,	# GP104BM [GTX 1080 Mobile]
        0x1be1,	# GP104BM [GTX 1070 Mobile]

        0x1c00,	# GP106
        0x1c01,	# GP106
        0x1c02,	# GP106 [GTX 1060 3GB]
        0x1c03,	# GP106 [GTX 1060 6GB]
        0x1c04,	# GP106 [GTX 1060 5GB]
        0x1c06,	# GP106 [GTX 1060 6GB Rev. 2]
        0x1c07,	# GP106 [P106-100]
        0x1c09,	# GP106 [P106-090]
        0x1c20,	# GP106M [GTX 1060 Mobile]
        0x1c21,	# GP106M [GTX 1050 Ti Mobile]
        0x1c22,	# GP106M [GTX 1050 Mobile]
        0x1c23,	# GP106M [GTX 1060 Mobile Rev. 2]
        0x1c2d,	# GP106M
        0x1c30,	# GP106GL [Quadro P2000]
        0x1c31,	# GP106GL [Quadro P2200]
        0x1c35,	# GP106M [Quadro P2000 Mobile]
        0x1c36,	# GP106 [P106M]
        0x1c60,	# GP106BM [GTX 1060 Mobile 6GB]
        0x1c61,	# GP106BM [GTX 1050 Ti Mobile]
        0x1c62,	# GP106BM [GTX 1050 Mobile]
        0x1c70,	# GP106GL

        0x1c80,
        0x1c81,	# GP107 [GTX 1050]
        0x1c82,	# GP107 [GTX 1050 Ti]
        0x1c83,	# GP107 [GTX 1050 3GB]
        0x1c8c,	# GP107M [GTX 1050 Ti Mobile]
        0x1c8d,	# GP107M [GTX 1050 Mobile]
        0x1c8e,	# GP107M
        0x1c8f,	# GP107M [GTX 1050 Ti Max-Q]
        0x1c90,	# GP107M [GeForce MX150]
        0x1c91,	# GP107M [GTX 1050 3 GB Max-Q]
        0x1c92,	# GP107M [GTX 1050 Mobile]
        0x1c94,	# GP107M [GeForce MX350]
        0x1c96,	# GP107M [GeForce MX350]
        0x1ca7,	# GP107GL
        0x1ca8,	# GP107GL
        0x1caa,	# GP107GL
        0x1cb1,	# GP107GL [Quadro P1000]
        0x1cb2,	# GP107GL [Quadro P600]
        0x1cb3,	# GP107GL [Quadro P400]
        0x1cb6,	# GP107GL [Quadro P620]
        0x1cba,	# GP107GLM [Quadro P2000 Mobile]
        0x1cbb,	# GP107GLM [Quadro P1000 Mobile]
        0x1cbc,	# GP107GLM [Quadro P600 Mobile]
        0x1cbd,	# GP107GLM [Quadro P620]
        0x1ccc,	# GP107BM [GTX 1050 Ti Mobile]
        0x1ccd,	# GP107BM [GTX 1050 Mobile]
        0x1cfa,	# GP107GL [Quadro P2000]
        0x1cfb,	# GP107GL [Quadro P1000]

        0x1d01,	# GP108 [GeForce GT 1030]
        0x1d02,	# GP108 [GeForce GT 1010]
        0x1d10,	# GP108M [GeForce MX150]
        0x1d11,	# GP108M [GeForce MX230]
        0x1d12,	# GP108M [GeForce MX150]
        0x1d13,	# GP108M [GeForce MX250]
        0x1d16,	# GP108M [GeForce MX330]
        0x1d33,	# GP108GLM [Quadro P500 Mobile]
        0x1d34,	# GP108GLM [Quadro P520]
        0x1d52,	# GP108BM [GeForce MX250]
        0x1d56,	# GP108BM [GeForce MX330]
    ]


class amd_ids:

    gcn_7000_ids = [
        # GCN v1
        # AMDPitcairnGraphicsAccelerator - AMD7000Controller
        0x6800,  # HD 7970M
        0x6801,  # HD 8970M
        0x6806,  # Unknown
        0x6808,  # W7000
        0x6810,  # R7 370 / R9 270X/370X
        0x6818,  # HD 7870
        0x6819,  # HD 7850 / R7 265 / R9 270 1024SP
        # AMDTahitiGraphicsAccelerator - AMD7000Controller
        0x6790,  # Unknown
        0x6798,  # HD 7970/8970 OEM / R9 280X / D700
        0x679A,  # HD 7950/8950 OEM / R9 280
        0x679E,  # HD 7870 XT
        0x6780,  # W9000
        # AMDVerdeGraphicsAccelerator - AMD7000Controller
        0x6820,  # HD 8890M / R9 M275X/M375X / M5100
        0x6821,  # HD 8870M / R9 M270X/M370X
        0x6823,  # HD 8850M / R9 M265X
        0x6825,  # HD 7870M
        0x6827,  # HD 7850M/8850M
        0x682B,  # HD 8830M / R7 250 / R7 M465X
        0x682D,  # M4000
        0x682F,  # HD 7730M
        0x6835,  # R9 255
        0x6839,  # Unknown
        0x683B,  # Unknown
        0x683D,  # HD 7770/8760 / R7 250X
        0x683F,  # HD 7750/8740 / R7 250E
    ]

    gcn_8000_ids = [
        # GCN v2
        # AMDBonaireGraphicsAccelerator - AMD8000Controller
        0x6640,  # M6100
        0x6641,  # HD 8930M
        0x6646,  # R9 M280X / W6170M
        0x6647,  # R9 M270X/M280X
        0x6650,  # Unknown
        0x6651,  # Unknown
        0x665C,  # HD 7790/8770 / R7 360 / R9 260/360
        0x665D,  # R7 200
        # AMDHawaiiGraphicsAccelerator - AMD8000Controller
        0x67B0,  # R9 290X/390X
    ]

    gcn_9000_ids = [
        # GCN v3
        # AMDFijiGraphicsAccelerator - AMD9000Controller
        0x7300,  # R9 FURY / NANO
        0x730F,  # Unknown
        # AMDTongaGraphicsAccelerator - AMD9000Controller
        0x6920,  # R9 M395/ M395X
        0x6921,  # R9 M295X / M390X
        0x6930,  # Unknown
        0x6938,  # R9 380X / R9 M295X
        0x6939,  # R9 285/380
    ]

    polaris_ids = [
        # GCN v4
        # AMDRadeonX4000
        # AMDBaffinGraphicsAccelerator - AMD9500Controller
        0x67E0,  # Pro WX 4170
        0x67E3,  # Pro WX 4100
        0x67E8,  # Pro WX 4130/4150
        0x67EB,  # Pro V5300X
        0x67EF,  # 460/560D / Pro 450/455/460/555/555X/560/560X
        0x67FF,  # 550 640SP / RX 560/560X
        0x67E1,  # Unknown
        0x67E7,  # Unknown
        0x67E9,  # Unknown
        # AMDEllesmereGraphicsAccelerator - AMD9500Controller
        0x67C0,  # Pro WX 7100 Mobile
        0x67C1,  # Unknown
        0x67C2,  # Pro V7300X / V7350x2
        0x67C4,  # Pro WX 7100
        0x67C7,  # Pro WX 5100
        0x67DF,  # 470/480/570/570X/580/580X/590
        0x67D0,  # Pro V7300X / V7350x2
        0x67C8,  # Unknown
        0x67C9,  # Unknown
        0x67CA,  # Unknown
        0x67CC,  # Unknown
        0x67CF,  # Unknown
    ]

    polaris_spoof_ids = [
        # Polaris 12 (Lexa)
        0x6981,  # Lexa XT [Radeon PRO WX 3200]
    ]

    vega_ids = [
        # GCN v5
        # AMDRadeonX5000
        # AMDVega10GraphicsAccelerator - AMD10000Controller
        0x6860,  # Instinct MI25
        0x6861,  # Pro WX 9100
        0x6862,  # Pro SSG
        0x6863,  # Vega Frontier
        0x6864,  # Pro V340
        0x6867,  # Pro Vega 56
        0x6868,  # Pro WX 8100/8200
        0x6869,  # Pro Vega 48
        0x686A,  # Unknown
        0x686B,  # Pro Vega 64X
        0x686C,  # Instinct MI25
        0x686D,  # Unknown
        0x686E,  # Unknown
        0x686F,  # Unknown
        0x687F,  # RX Vega 56/64
        # AMDVega12GraphicsAccelerator - AMD10000Controller
        0x69A0,  # Unknown
        0x69A1,  # Unknown
        0x69A2,  # Unknown
        0x69A3,  # Unknown
        0x69AF,  # Unknown
        # AMDVega20GraphicsAccelerator - AMD10000Controller
        0x66A0,  # Instinct
        0x66A1,  # Pro VII/Instinct MI50
        0x66A2,  # Unknown
        0x66A3,  # Pro Vega II/ Pro Vega II Duo
        0x66A7,  # Unknown
        0x66AF,  # VII
    ]

    navi_ids = [
        # AMDRadeonX6000
        # AMDNavi10GraphicsAccelerator
        0x7310,  # Pro W5700X
        0x7312,  # Pro W5700
        0x7318,  # Unknown
        0x7319,  # Unknown
        0x731A,  # Unknown
        0x731B,  # Unknown
        0x731F,  # RX 5600/5600 XT / 5700/5700 XT
        # AMDNavi12GraphicsAccelerator
        0x7360,  # 5600M
        # AMDNavi14GraphicsAccelerator
        0x7340,  # 5500/5500M / Pro 5500M
        0x7341,  # Pro W5500
        0x7343,  # Unknown
        0x7347,  # Pro W5500M
        0x734F,  # Pro W5300M
        # AMDNavi21GraphicsAccelerator
        0x73A2,  # Pro W6900X
        0x73AB,  # Pro W6800X/Pro W6800X Duo
        0x73BF,  # 6800/6800 XT / 6900 XT
        0x73A3,  # Pro W6800
        # AMDNavi23GraphicsAccelerator
        0x73E3,  # Pro W6600
        0x73FF,  # 6600/6600 XT/6600M
        0x73E0,  # Unknown
    ]

    r500_ids = [
        0x7187,  # X1300/X1550
        0x7146,  # X1300/X1550
        0x71c5,  # Mobile X1600
        0x7249,  # X1900 XT
    ]

    terascale_1_ids = [
        0x9400,  # HD 2900 PRO/XT
        0x9401,  # HD 2900 XT
        0x9402,  # Unknown
        0x9403,  # HD 2900 PRO
        0x9581,  # HD 2600 (mobile)
        0x9583,  # HD 2600 XT/2700 (mobile)
        0x9588,  # HD 2600 XT
        0x94C8,  # HD 2400 XT (mobile)
        0x94C9,  # HD 2400 (mobile)
        0x9500,  # HD 3850 X2
        0x9501,  # HD 3870
        0x9505,  # HD 3690/3850
        0x9507,  # HD 3830
        0x9504,  # HD 3850 (mobile)
        0x9506,  # HD 3850 X2 (mobile)
        0x9598,  # HD 3650/3750/4570/4580
        0x9488,  # HD 4670 (mobile)
        0x9599,  # HD 3650 AGP
        0x9591,  # HD 3650 (mobile)
        0x9593,  # HD 3670 (mobile)
        0x9440,  # HD 4870
        0x9442,  # HD 4850
        0x944A,  # HD 4850 (mobile)
        0x945A,  # HD 4870 (mobile)
        0x9490,  # HD 4670
        0x949E,  # FirePro V5700
        0x9480,  # HD 4650/5165 (mobile)
        0x9540,  # HD 4550
        0x9541,  # Unknown
        0x954E,  # Unknown
        0x954F,  # HD 4350/4550
        0x9552,  # HD 4330/4350/4550 (mobile)
        0x9553,  # HD 4530/4570/545v (mobile)
        0x94A0,  # HD 4830
    ]

    terascale_2_ids = [
        0x6738,  # HD 6870
        0x6739,  # HD 6850
        0x6720,  # HD 6970M/6990M
        0x6722,  # Unknown
        0x6768,  # Unknown
        0x6770,  # HD 6450A/7450A
        0x6779,  # HD 6450/7450/8450 / R5 230 OEM
        0x6760,  # HD 6400M/7400M
        0x6761,  # HD 6430M
        0x68E0,  # HD 5430/5450/547
        0x6898,  # HD 5870
        0x6899,  # HD 5850
        0x68B8,  # HD 5770
        0x68B0,  # Unknown
        0x68B1,  # Unknown
        0x68A0,  # HD 5870 (mobile)
        0x68A1,  # HD 5850 (mobile)
        0x6840,  # HD 7500M/7600M
        0x6841,  # HD 7550M/7570M/7650M
        0x68D8,  # HD 5670/5690/5730
        0x68C0,  # HD 5730 / 6570M
        0x68C1,  # HD 5650/5750 / 6530M/6550M
        0x68D9,  # HD 5550/5570/5630/6510/6610/7570
        0x6750,  # HD 6650A/7650A
        0x6758,  # HD 6670/7670
        0x6759,  # HD 6570/7570/8550
        0x6740,  # HD 6730M/6770M/7690M XT
        0x6741,  # HD 6630M/6650M/6750M/7670M/7690M
        0x6745,  # Unknown
    ]


class intel_ids:
    # https://dgpu-docs.intel.com/devices/hardware-table.html
    gma_950_ids = [
        0x2582,  # 915G
        0x2592,  # 915GM
        0x2772,  # 945G
        0x27A2,  # 945GM
    ]

    gma_x3100_ids = [
        0x2a02,  # 965GM
    ]

    iron_ids = [
        # AppleIntelHDGraphics IDs
        0x0044,  # Unknown
        0x0046,  # HD Graphics
    ]

    sandy_ids = [
        # AppleIntelHD3000Graphics IDs
        # AppleIntelSNBGraphicsFB IDs
        0x0106,  # HD Graphics 2000
        0x0601,  # Unknown
        0x0116,  # HD Graphics 3000
        0x0102,  # HD Graphics 2000
        0x0126,  # HD Graphics 3000
    ]

    ivy_ids = [
        # AppleIntelHD4000Graphics IDs
        # AppleIntelFramebufferCapri IDs
        0x0152,  # HD Graphics 2500
        0x0156,  # HD Graphics 2500
        0x0162,  # HD Graphics 4000
        0x0166,  # HD Graphics 4000
    ]

    haswell_ids = [
        # AppleIntelHD5000Graphics IDs
        # AppleIntelFramebufferAzul IDs
        0x0D26,  # Iris Pro Graphics P5200
        0x0A26,  # HD Graphics 5000
        0x0A2E,  # Iris Graphics 5100
        0x0D22,  # Iris Pro Graphics 5200
        0x0412,  # HD Graphics 4600
    ]

    broadwell_ids = [
        # AppleIntelBDWGraphicsFramebuffer IDs
        0x0BD1,  # Unknown
        0x0BD2,  # Unknown
        0x0BD3,  # Unknown
        0x1606,  # HD Graphics
        0x160E,  # HD Graphics
        0x1616,  # HD Graphics 5500
        0x161E,  # HD Graphics 5300
        0x1626,  # HD Graphics 6000
        0x1622,  # Iris Pro Graphics 6200
        0x1612,  # HD Graphics 5600
        0x162B,  # Iris Graphics 6100
    ]

    skylake_ids = [
        # AppleIntelSKLGraphicsFramebuffer IDs
        0x1916,  # HD Graphics 520
        0x191E,  # HD Graphics 515
        0x1926,  # Iris Graphics 540
        0x1927,  # Iris Graphics 550
        0x1912,  # HD Graphics 530
        0x1932,  # Iris Pro Graphics 580
        0x1902,  # HD Graphics 510
        0x1917,  # Unknown
        0x193B,  # Iris Pro Graphics 580
        0x191B,  # HD Graphics 530
    ]

    kaby_lake_ids = [
        # AppleIntelKBLGraphicsFramebuffer IDs
        0x5912,  # HD Graphics 630
        0x5916,  # HD Graphics 620
        0x591B,  # HD Graphics 630
        0x591C,  # UHD Graphics 615
        0x591E,  # HD Graphics 615
        0x5926,  # Iris Plus Graphics 640
        0x5927,  # Iris Plus Graphics 650
        0x5923,  # HD Graphics 635
    ]

    coffee_lake_ids = [
        # AppleIntelCFLGraphicsFramebuffer IDs
        0x3E9B,  # UHD Graphics 630
        0x3EA5,  # Iris Plus Graphics 655
        0x3EA6,  # Unknown
        0x3E92,  # UHD Graphics 630
        0x3E91,  # UHD Graphics 630
        0x3E98,  # UHD Graphics 630
    ]

    comet_lake_ids = [
        0x9BC8,  # UHD Graphics 630
        0x9BC5,  # UHD Graphics 630
        0x9BC4,  # UHD Graphics
    ]

    ice_lake_ids = [
        # AppleIntelICLLPGraphicsFramebuffer IDs
        0xFF05,  # Unknown
        0x8A70,  # Unknown
        0x8A71,  # Unknown
        0x8A51,  # Iris Plus Graphics G7
        0x8A5C,  # Iris Plus Graphics G4
        0x8A5D,  # Unknown
        0x8A52,  # Iris Plus Graphics G7
        0x8A53,  # Iris Plus Graphics G7
        0x8A5A,  # Iris Plus Graphics G4
        0x8A5B,  # Unknown
    ]

    AppleIntel8254XEthernet = [
        # AppleIntel8254XEthernet IDs
        0x1096,  # 80003ES2LAN
        0x100F,  # 82545EM
        0x105E,  # 82571EB/82571GB
    ]

    AppleIntelI210Ethernet = [
        # AppleIntelI210Ethernet IDs
        0x1533,  # I210
        0x15F2,  # I225
        0x15F3,  # I225
        0x3100,  # I225
        0x3101,  # I225
        0x5502,  # I225
        0x0D9F,  # I225
        0x15F8,  # I225
        0x15F7,  # I225
        0x15FD,  # I225
    ]

    Intel82574L = [
        # Intel82574L IDs
        0x104B,  # 82566DC
        0x10F6,  # 82574L
    ]


class broadcom_ids:
    AppleBCMWLANBusInterfacePCIe = [
        0x43DC,  # BCM4355
        0x4464,  # BCM4364
        0x4488,  # BCM4377b
        0x4425,  # BCM4378 (M1)
        0x4433,  # BCM4387 (M1 Pro/Max/Ultra)
    ]

    AirPortBrcmNIC = [
        # AirPortBrcmNIC IDs
        0x43BA,  # BCM43602
        0x43A3,  # BCM4350
        0x43A0,  # BCM4360
    ]

    # Not natively supported, but supported by AirportBrcmFixup
    AirPortBrcmNICThirdParty = [
        0x4357,  # BCM43225
        0x43B1,  # BCM4352
        0x43B2,  # BCM4352 (2.4 GHz)
    ]

    AirPortBrcm4360 = [
        # AirPortBrcm4360 IDs (removed duplicates for 4360 class cards)
        0x4331,  # BCM94331
        0x4353,  # BCM943224
    ]

    AirPortBrcm4331 = [
        # AirPortBrcm4331 IDs (removed duplicates for 4331 class cards)
        0x432B,  # BCM94322
    ]

    AppleAirPortBrcm43224 = [
        # AppleAirPortBrcm43224 IDs
        0x4311,  # BCM4311 - never used by Apple
        0x4312,  # BCM4311 - never used by Apple
        0x4313,  # BCM4311 - never used by Apple
        0x4318,  # BCM4318 - never used by Apple
        0x4319,  # BCM4318 - never used by Apple
        0x431A,  # Unknown - never used by Apple
        0x4320,  # BCM4306 - never used by Apple
        0x4324,  # BCM4309 - never used by Apple
        0x4325,  # BCM4306 - never used by Apple
        0x4328,  # BCM4328
        0x432C,  # BCM4322 - never used by Apple
        0x432D,  # BCM4322 - never used by Apple
    ]

    AppleBCM5701Ethernet = [
        # AppleBCM5701Ethernet IDs
        0x1684,  # BCM5764M
        0x16B0,  # BCM57761
        0x16B4,  # BCM57765
        0x1682,  # BCM57762
        0x1686,  # BCM57766
    ]


class aquantia_ids:
    AppleEthernetAquantiaAqtion = [
        # AppleEthernetAquantiaAqtion IDs
        0x0001,  # AQC107
        0xD107,  # AQC107
        0x07B1,  # AQC107
        0x80B1,  # AQC107
        0x87B1,  # AQC107
        0x88B1,  # AQC107
        0x89B1,  # AQC107
        0x91B1,  # AQC107
        0x92B1,  # AQC107
        0x00C0,  # AQC113
        0x04C0,  # AQC113
        0x94C0,  # AQC113
        0x93C0,  # AQC113
    ]


class marvell_ids:
    MarvelYukonEthernet = [
        # AppleYukon2.kext IDs
        # AppleYukon2 supports 2 vendors (Marvell and SysKonnect)
        0x9E00,
        0x2100,
        0x9E00,
        0x2200,
        0x9E00,
        0x8100,
        0x9E00,
        0x8200,
        0x9E00,
        0x9100,
        0x9E00,
        0x9200,
        0x9000,
        0x2100,
        0x9000,
        0x2200,
        0x9000,
        0x8100,
        0x9000,
        0x8200,
        0x9000,
        0x9100,
        0x9000,
        0x9200,
        0x9E00,
        0x2200,
        0x9E00,
        0x2200,
    ]


class syskonnect_ids:
    MarvelYukonEthernet = [
        # AppleYukon2.kext IDs
        # AppleYukon2 supports 2 vendors (Marvell and SysKonnect)
        0x4365,
        0x4360,
        0x435A,
        0x4354,
        0x4362,
        0x4363,
        0x00BA,
        0x436A,
    ]


class atheros_ids:
    AtherosWifi = [
        # AirPortAtheros40 IDs
        0x0030,  # AR93xx
        0x002A,  # AR928X
        0x001C,  # AR242x / AR542x
        0x0023,  # AR5416 - never used by Apple
        0x0024,  # AR5418
    ]
