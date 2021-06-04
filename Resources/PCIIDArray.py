# Array of Device IDs for different devices


class nvidia_ids:
    # Courteous of envytools as well as Macrumors:
    # https://envytools.readthedocs.io/en/latest/hw/pciid.html
    # https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/
    tesla_ids = [
        # G80
        "0190",  # G80 [GeForce 8800 GTS / 8800 GTX]
        "0191",  # G80 [GeForce 8800 GTX]
        "0193",  # G80 [GeForce 8800 GTS]
        "0194",  # G80 [GeForce 8800 Ultra]
        "019E",  # G80GL [Quadro FX 4600]
        "019D",  # G80GL [Quadro FX 5600]
        # G84
        "0400",  # G84 [8600 GTS]
        "0401",  # G84 [8600 GT]
        "0402",  # G84 [8600 GT]
        "0403",  # G84 [8600 GS]
        "0404",  # G84 [8400 GS]
        "0405",  # G84 [9500M GS]
        "0406",  # G84 [8300 GS]
        "0407",  # G84 [8600M GT]
        "0408",  # G84 [9650M GS]
        "0409",  # G84 [8700M GT]
        "040A",  # G84 [FX 370]
        "040B",  # G84 [NVS 320M]
        "040C",  # G84 [FX 570M]
        "040D",  # G84 [FX 1600M]
        "040E",  # G84 [FX 570]
        "040F",  # G84 [FX 1700]
        # G86
        "0420",  # G86 [8400 SE]
        "0421",  # G86 [8500 GT]
        "0422",  # G86 [8400 GS]
        "0423",  # G86 [8300 GS]
        "0424",  # G86 [8400 GS]
        "0425",  # G86 [8600M GS]
        "0426",  # G86 [8400M GT]
        "0427",  # G86 [8400M GS]
        "0428",  # G86 [8400M G]
        "0429",  # G86 [NVS 140M]
        "042A",  # G86 [NVS 130M]
        "042B",  # G86 [NVS 135M]
        "042C",  # G86 [9400 GT]
        "042D",  # G86 [FX 360M]
        "042E",  # G86 [9300M G]
        "042F",  # G86 [NVS 290]
        # G92
        "0410",  # G92 [GT 330]
        "0600",  # G92 [8800 GTS 512]
        "0601",  # G92 [9800 GT]
        "0602",  # G92 [8800 GT]
        "0603",  # G92 [GT 230]
        "0604",  # G92 [9800 GX2]
        "0605",  # G92 [9800 GT]
        "0606",  # G92 [8800 GS]
        "0607",  # G92 [GTS 240]
        "0608",  # G92 [9800M GTX]
        "0609",  # G92 [8800M GTS]
        "060A",  # G92 [GTX 280M]
        "060B",  # G92 [9800M GT]
        "060C",  # G92 [8800M GTX]
        "060F",  # G92 [GTX 285M]
        "0610",  # G92 [9600 GSO]
        "0611",  # G92 [8800 GT]
        "0612",  # G92 [9800 GTX/9800 GTX+]
        "0613",  # G92 [9800 GTX+]
        "0614",  # G92 [9800 GT]
        "0615",  # G92 [GTS 250]
        "0617",  # G92 [9800M GTX]
        "0618",  # G92 [GTX 260M]
        "0619",  # G92 [FX 4700 X2]
        "061A",  # G92 [FX 3700]
        "061B",  # G92 [VX 200]
        "061C",  # G92 [FX 3600M]
        "061D",  # G92 [FX 2800M]
        "061E",  # G92 [FX 3700M]
        "061F",  # G92 [FX 3800M]
        # G94
        "0621",  # G94 [GT 230]
        "0622",  # G94 [9600 GT]
        "0623",  # G94 [9600 GS]
        "0624",  # G94 [9600 GT Green Edition]
        "0625",  # G94 [9600 GSO 512]
        "0626",  # G94 [GT 130]
        "0627",  # G94 [GT 140]
        "0628",  # G94 [9800M GTS]
        "062A",  # G94 [9700M GTS]
        "062B",  # G94 [9800M GS]
        "062C",  # G94 [9800M GTS ]
        "062D",  # G94 [9600 GT]
        "062E",  # G94 [9600 GT]
        "062F",  # G94 [9800 S]
        "0631",  # G94 [GTS 160M]
        "0635",  # G94 [9600 GSO]
        "0637",  # G94 [9600 GT]
        "0638",  # G94 [FX 1800]
        "063A",  # G94 [FX 2700M]
        # G96
        "0640",  # G96 [9500 GT]
        "0641",  # G96 [9400 GT]
        "0643",  # G96 [9500 GT]
        "0644",  # G96 [9500 GS]
        "0645",  # G96 [9500 GS]
        "0646",  # G96 [GT 120]
        "0647",  # G96 [9600M GT]
        "0648",  # G96 [9600M GS]
        "0649",  # G96 [9600M GT]
        "064A",  # G96 [9700M GT]
        "064B",  # G96 [9500M G]
        "064C",  # G96 [9650M GT]
        "0651",  # G96 [G 110M]
        "0652",  # G96 [GT 130M]
        "0653",  # G96 [GT 120M]
        "0654",  # G96 [GT 220M]
        "0655",  # G96 [GT 120]
        "0656",  # G96 [GT 120 ]
        "0658",  # G96 [FX 380]
        "0659",  # G96 [FX 580]
        "065A",  # G96 [FX 1700M]
        "065B",  # G96 [9400 GT]
        "065C",  # G96 [FX 770M]
        "065F",  # G96 [G210]
        # G98
        "06E0",  # G98 [9300 GE]
        "06E1",  # G98 [9300 GS]
        "06E2",  # G98 [8400]
        "06E3",  # G98 [8400 SE]
        "06E4",  # G98 [8400 GS]
        "06E5",  # G98M [9300M GS]
        "06E6",  # G98 [G100]
        "06E7",  # G98 [9300 SE]
        "06E8",  # G98 [9200M GS]
        "06E9",  # G98 [9300M GS]
        "06EA",  # G98 [NVS 150M]
        "06EB",  # G98 [NVS 160M]
        "06EC",  # G98 [G 105M]
        "06ED",  # G98 [9600 GT / 9800 GT]
        "06EF",  # G98 [G 103M]
        "06F1",  # G98 [G105M]
        "06F8",  # G98 [NVS 420]
        "06F9",  # G98 [FX 370 LP]
        "06FA",  # G98 [NVS 450]
        "06FB",  # G98 [FX 370M]
        "06FD",  # G98 [NVS 295]
        "06FF",  # G98 [HICx16]
        # GT200
        "05E0",  # GT200 [GTX 295]
        "05E1",  # GT200 [GTX 280]
        "05E2",  # GT200 [GTX 260]
        "05E3",  # GT200 [GTX 285]
        "05E6",  # GT200 [GTX 275]
        "05E7",  # GT200 [C1060]
        "05E9",  # GT200 [CX]
        "05EA",  # GT200 [GTX 260]
        "05EB",  # GT200 [GTX 295]
        "05ED",  # GT200 [FX 5800]
        "05EE",  # GT200 [FX 4800]
        "05EF",  # GT200 [FX 3800]
        "05FD",  # GT200GL [Quadro FX 5800]
        "05FE",  # GT200GL [Quadro FX 4800]
        "05FF",  # GT200GL [Quadro FX 3800]
        # MCP77 GPU
        "0840",  # MCP77 GPU [8200M]
        "0844",  # MCP77 GPU [9100M G]
        "0845",  # MCP77 GPU [8200M G]
        "0846",  # MCP77 GPU [9200]
        "0847",  # MCP77 GPU [9100]
        "0848",  # MCP77 GPU [8300]
        "0849",  # MCP77 GPU [8200]
        "084A",  # MCP77 GPU [730A]
        "084B",  # MCP77 GPU [9200]
        "084C",  # MCP77 GPU [980A/780A SLI]
        "084D",  # MCP77 GPU [750A SLI]
        "084F",  # MCP77 GPU [8100 / 720A]
        # MCP79 GPU
        "0860",  # MCP79 GPU [9400]
        "0861",  # MCP79 GPU [9400]
        "0862",  # MCP79 GPU [9400M G]
        "0863",  # MCP79 GPU [9400M]
        "0864",  # MCP79 GPU [9300]
        "0865",  # MCP79 GPU [ION]
        "0866",  # MCP79 GPU [9400M G]
        "0867",  # MCP79 GPU [9400]
        "0868",  # MCP79 GPU [760i SLI]
        "0869",  # MCP79 GPU [9400]
        "086A",  # MCP79 GPU [9400]
        "086C",  # MCP79 GPU [9300 / 730i]
        "086D",  # MCP79 GPU [9200]
        "086E",  # MCP79 GPU [9100M G]
        "086F",  # MCP79 GPU [8200M G]
        "0870",  # MCP79 GPU [9400M]
        "0871",  # MCP79 GPU [9200]
        "0872",  # MCP79 GPU [G102M]
        "0873",  # MCP79 GPU [G102M]
        "0874",  # MCP79 GPU [ION]
        "0876",  # MCP79 GPU [ION]
        "087A",  # MCP79 GPU [9400]
        "087D",  # MCP79 GPU [ION]
        "087E",  # MCP79 GPU [ION LE]
        "087F",  # MCP79 GPU [ION LE]
        # GT215
        "0CA0",  # GT215 [GT 330]
        "0CA2",  # GT215 [GT 320]
        "0CA3",  # GT215 [GT 240]
        "0CA4",  # GT215 [GT 340]
        "0CA5",  # GT215 [GT 220]
        "0CA7",  # GT215 [GT 330]
        "0CA9",  # GT215 [GTS 250M]
        "0CAC",  # GT215 [GT 220]
        "0CAF",  # GT215 [GT 335M]
        "0CB0",  # GT215 [GTS 350M]
        "0CB1",  # GT215 [GTS 360M]
        "0CBC",  # GT215 [FX 1800M]
        # GT216
        "0A20",  # GT216 [GT 220]
        "0A22",  # GT216 [315]
        "0A23",  # GT216 [210]
        "0A26",  # GT216 [405]
        "0A27",  # GT216 [405]
        "0A28",  # GT216 [GT 230M]
        "0A29",  # GT216 [GT 330M]
        "0A2A",  # GT216 [GT 230M]
        "0A2B",  # GT216 [GT 330M]
        "0A2C",  # GT216 [NVS 5100M]
        "0A2D",  # GT216 [GT 320M]
        "0A32",  # GT216 [GT 415]
        "0A34",  # GT216 [GT 240M]
        "0A35",  # GT216 [GT 325M]
        "0A38",  # GT216 [400]
        "0A3C",  # GT216 [FX 880M]
        # GT218
        "0A60",  # GT218 [G210]
        "0A62",  # GT218 [205]
        "0A63",  # GT218 [310]
        "0A64",  # GT218 [ION]
        "0A65",  # GT218 [210]
        "0A66",  # GT218 [310]
        "0A67",  # GT218 [315]
        "0A68",  # GT218 [G105M]
        "0A69",  # GT218 [G105M]
        "0A6A",  # GT218 [NVS 2100M]
        "0A6C",  # GT218 [NVS 3100M]
        "0A6E",  # GT218 [305M]
        "0A6F",  # GT218 [ION]
        "0A70",  # GT218 [310M]
        "0A71",  # GT218 [305M]
        "0A72",  # GT218 [310M]
        "0A73",  # GT218 [305M]
        "0A74",  # GT218 [G210M]
        "0A75",  # GT218 [310M]
        "0A76",  # GT218 [ION]
        "0A78",  # GT218 [FX 380 LP]
        "0A7A",  # GT218 [315M]
        "0A7C",  # GT218 [FX 380M]
        "10C0",  # GT218 [9300 GS]
        "10C3",  # GT218 [8400GS]
        "10C5",  # GT218 [405]
        "10D8",  # GT218 [NVS 300]
        # MCP89 GPU
        "08A0",  # MCP89 GPU [320M]
        "08A2",  # MCP89 GPU [320M]
        "08A3",  # MCP89 GPU [320M]
        "08A4",  # MCP89 GPU [320M]
    ]

    fermi_ids = [
        # GF100
        "06C0",  # GF100 [GTX 480]
        "06C4",  # GF100 [GTX 465]
        "06CA",  # GF100 [GTX 480M]
        "06CB",  # GF100 [GTX 480]
        "06CD",  # GF100 [GTX 470]
        "06D1",  # GF100 [C2050 / C2070]
        "06D2",  # GF100 [M2070]
        "06D8",  # GF100 [6000]
        "06D9",  # GF100 [5000]
        "06DA",  # GF100 [5000M]
        "06DC",  # GF100 [6000]
        "06DD",  # GF100 [4000]
        "06DE",  # GF100 [T20]
        "06DF",  # GF100 [M2070-Q]
        # GF104
        "0E22",  # GF104 [GTX 460]
        "0E23",  # GF104 [GTX 460 SE]
        "0E24",  # GF104 [GTX 460 OEM]
        "0E30",  # GF104 [GTX 470M]
        "0E31",  # GF104 [GTX 485M]
        "0E3A",  # GF104 [3000M]
        "0E3B",  # GF104 [4000M]
        # GF114
        "1200",  # GF114 [GTX 560 Ti]
        "1201",  # GF114 [GTX 560]
        "1202",  # GF114 [GTX 560 Ti OEM]
        "1203",  # GF114 [GTX 460 SE v2]
        "1205",  # GF114 [GTX 460 v2]
        "1206",  # GF114 [GTX 555]
        "1207",  # GF114 [GT 645 OEM]
        "1208",  # GF114 [GTX 560 SE]
        "1210",  # GF114 [GTX 570M]
        "1211",  # GF114 [GTX 580M]
        "1212",  # GF114 [GTX 675M]
        "1213",  # GF114 [GTX 670M]
        # GF106
        "0DC0",  # GF106 [GT 440]
        "0DC4",  # GF106 [GTS 450]
        "0DC5",  # GF106 [GTS 450]
        "0DC6",  # GF106 [GTS 450]
        "0DCD",  # GF106 [GT 555M]
        "0DCE",  # GF106 [GT 555M]
        "0DD1",  # GF106 [GTX 460M]
        "0DD2",  # GF106 [GT 445M]
        "0DD3",  # GF106 [GT 435M]
        "0DD6",  # GF106 [GT 550M]
        "0DD8",  # GF106 [2000]
        "0DDA",  # GF106 [2000M]
        # GF116
        "1241",  # GF116 [GT 545 OEM]
        "1243",  # GF116 [GT 545]
        "1244",  # GF116 [GTX 550 Ti]
        "1245",  # GF116 [GTS 450 Rev. 2]
        "1246",  # GF116 [GT 550M]
        "1247",  # GF116 [GT 635M]
        "1248",  # GF116 [GT 555M]
        "1249",  # GF116 [GTS 450 Rev. 3]
        "124B",  # GF116 [GT 640 OEM]
        "124D",  # GF116 [GT 555M]
        "1251",  # GF116 [GTX 560M]
        # GF108
        "0DE0",  # GF108 [GT 440]
        "0DE1",  # GF108 [GT 430]
        "0DE2",  # GF108 [GT 420]
        "0DE3",  # GF108 [GT 635M]
        "0DE4",  # GF108 [GT 520]
        "0DE5",  # GF108 [GT 530]
        "0DE8",  # GF108 [GT 620M]
        "0DE9",  # GF108 [GT 630M]
        "0DEA",  # GF108 [610M]
        "0DEB",  # GF108 [GT 555M]
        "0DEC",  # GF108 [GT 525M]
        "0DED",  # GF108 [GT 520M]
        "0DEE",  # GF108 [GT 415M]
        "0DEF",  # GF108 [NVS 5400M]
        "0DF0",  # GF108 [GT 425M]
        "0DF1",  # GF108 [GT 420M]
        "0DF2",  # GF108 [GT 435M]
        "0DF3",  # GF108 [GT 420M]
        "0DF4",  # GF108 [GT 540M]
        "0DF5",  # GF108 [GT 525M]
        "0DF6",  # GF108 [GT 550M]
        "0DF7",  # GF108 [GT 520M]
        "0DF8",  # GF108 [600]
        "0DF9",  # GF108 [500M]
        "0DFA",  # GF108 [1000M]
        "0DFC",  # GF108 [NVS 5200M]
        "0F00",  # GF108 [GT 630]
        "0F01",  # GF108 [GT 620]
        "0F02",  # GF108 [GT 730]
        # GF110
        "1080",  # GF110 [GTX 580]
        "1081",  # GF110 [GTX 570]
        "1082",  # GF110 [GTX 560 Ti]
        "1084",  # GF110 [GTX 560]
        "1086",  # GF110 [GTX 570]
        "1087",  # GF110 [GTX 560 Ti]
        "1088",  # GF110 [GTX 590]
        "1089",  # GF110 [GTX 580]
        "108B",  # GF110 [GTX 580]
        "1091",  # GF110 [M2090]
        "1096",  # GF110GL [Tesla C2050 / C2075]
        "109A",  # GF110 [5010M]
        "109B",  # GF110 [7000]
        # GF119
        "1040",  # GF119 [GT 520]
        "1042",  # GF119 [510]
        "1048",  # GF119 [605]
        "1049",  # GF119 [GT 620]
        "104A",  # GF119 [GT 610]
        "104B",  # GF119 [GT 625 OEM]
        "104C",  # GF119 [GT 705]
        "1050",  # GF119 [GT 520M]
        "1051",  # GF119 [GT 520MX]
        "1052",  # GF119 [GT 520M]
        "1054",  # GF119 [410M]
        "1055",  # GF119 [410M]
        "1056",  # GF119 [NVS 4200M]
        "1057",  # GF119 [NVS 4200M]
        "1058",  # GF119 [610M]
        "1059",  # GF119 [610M]
        "105A",  # GF119 [610M]
        "105B",  # GF119M [705M]
        "107C",  # GF119 [NVS 315]
        "107D",  # GF119 [NVS 310]
        # GF117
        "1140",  # GF117 [GT 620M]
    ]

    kepler_ids = [
        # GK104
        "1180",  # GK104 [GTX 680]
        "1183",  # GK104 [GTX 660 Ti]
        "1184",  # GK104 [GTX 770]
        "1185",  # GK104 [GTX 660]
        "1186",  # GK104 [GTX 660 Ti]
        "1187",  # GK104 [GTX 760]
        "1188",  # GK104 [GTX 690]
        "1189",  # GK104 [GTX 670]
        "118E",  # GK104 [GTX 760 OEM]
        "118F",  # GK104GL [Tesla K10]
        "1198",  # GTX 880M
        "1199",  # GK104 [GTX 870M]
        "119A",  # GTX 860M
        "119D",  # GK104M [GTX 775M Mac Edition]
        "119E",  # GTX 780M
        "119F",  # GK104 [GTX 780M]
        "11A0",  # GK104 [GTX 680M]
        "11A1",  # GK104 [GTX 670MX]
        "11A2",  # GK104 [GTX 675MX]
        "11A3",  # GK104 [GTX 680MX]
        "11A7",  # GK104 [GTX 675MX]
        "11A9",  # GTX 870M
        "11B4",  # GK104GL [Quadro K4200]
        "11B6",  # Quadro K3100M
        "11B7",  # Quadro K4100M
        "11B8",  # Quadro K5100M
        "11BA",  # GK104 [K5000]
        "11BC",  # GK104 [K5000M]
        "11BD",  # GK104 [K4000M]
        "11BE",  # GK104 [K3000M]
        "11BF",  # GK104 [GRID K2]
        # GK106
        "11C0",  # GK106 [GTX 660]
        "11C2",  # GK106 [GTX 650 Ti BOOST]
        "11C6",  # GK106 [GTX 650 Ti]
        "11E0",  # GK106 [GTX 770M]
        "11E1",  # GTX 765M
        "11E2",  # GTX 765M
        "11FA",  # GK106 [K4000]
        "11FC",  # Quadro K2100M
        # GK107
        "0FC0",  # GK107 [GT 640]
        "0FC1",  # GK107 [GT 640]
        "0FC2",  # GK107 [GT 630]
        "0FC6",  # GK107 [GTX 650]
        "0FC8",  # GK107 [GT 740]
        "0FCD",  # GK107M [GT 755M]
        "0FD1",  # GK107 [GT 650M]
        "0FD2",  # GK107 [GT 640M]
        "0FD3",  # GK107 [GT 640M LE]
        "0FD4",  # GK107 [GTX 660M]
        "0FD5",  # GK107 [GT 650M]
        "0FD8",  # GK107 [GT 640M]
        "0FD9",  # GK107 [GT 645M]
        "0FDF",  # GK107M [ GT 740M]
        "0FE0",  # GK107 [GTX 660M]
        "0FE1",  # GK107M [GT 730M]
        "0FE3",  # GK107M [GT 745M]
        "0FE4",  # GK107M [GT 750M]
        "0FE9",  # GK107 [GT 750M Mac Edition]
        "0FEA",  # GK107M [GT 755M Mac Edition]
        "0FEE",  # GK107M [810M]
        "0FF2",  # GK107GL [GRID K1]
        "0FF3",  # GK107GL [Quadro K420]
        "0FF6",  # Quadro K1100M
        "0FF9",  # GK107 [K2000D]
        "0FFA",  # GK107 [K600]
        "0FFB",  # GK107 [K2000M]
        "0FFC",  # GK107 [K1000M]
        "0FFD",  # GK107 [NVS 510]
        "0FFE",  # GK107 [K2000]
        "0FFF",  # GK107 [410]
        # GK110
        "1001",  # GK110B [GTX TITAN Z]
        "1003",  # GK110 [GTX Titan LE]
        "1004",  # GK110 [GTX 780]
        "1005",  # GK110 [GTX Titan]
        "1007",  # GK110 [GTX 780 Rev. 2]
        "100A",  # GK110B [GTX 780 Ti]
        "100C",  # GK110B [GTX TITAN Black]
        "101F",  # GK110 [TEslA K20]
        "1020",  # GK110 [TEslA K2]
        "1021",  # GK110 [TEslA K2m]
        "1022",  # GK110 [TEslA K20C]
        "1023",  # GK110BGL [Tesla K40m]
        "1024",  # GK180GL [Tesla K40c]
        "1026",  # GK110 [TEslA K20s]
        "1028",  # GK110 [TEslA K20m]
        "102D",  # GK210GL [Tesla K80]
        "103C",  # GK110GL [Quadro K5200]
        # GK208
        "1280",  # GK208 [GT 635]
        "1281",  # GK208 [GT 710]
        "1282",  # GK208 [GT 640 REv. 2]
        "1284",  # GK208 [GT 630 REv. 2]
        "1286",  # GK208 [GT 720]
        "1287",  # GK208B [GT 730]
        "1288",  # GK208B [GT 720]
        "1289",  # GK208 [GT 710]
        "128B",  # GK208B [GT 710]
        "1290",  # GK208 [GT 730M]
        "1291",  # GK208 [GT 735M]
        "1292",  # GK208 [GT 740M]
        "1293",  # GK208 [GT 730M]
        "1294",  # GK208 [GT 740M]
        "1295",  # GK208 [710M]
        "1296",  # GK208M [825M]
        "1298",  # GK208M [GT 720M]
        "1299",  # GK208BM [920M]
        "129A",  # GK208BM [910M]
        "12B9",  # GK208 [K610M]
        "12BA",  # GK208 [K510M]
    ]


class amd_ids:
    legacy_gcn_ids = [
        # AMDRadeonX4000
        # AMDBonaireGraphicsAccelerator
        "6640",
        "6641",
        "6646",
        "6647",
        "6650",
        "6651",
        "665C",
        "665D",
        # AMDFijiGraphicsAccelerator
        "7300",
        "730F",
        # AMDHawaiiGraphicsAccelerator
        "67B0",
        # AMDPitcairnGraphicsAccelerator
        "6800",
        "6801",
        "6806",
        "6808",
        "6810",
        "6818",
        "6819",
        # AMDTahitiGraphicsAccelerator
        "6790",
        "6798",
        "679A",
        "679E",
        "6780",
        # AMDTongaGraphicsAccelerator
        "6920",
        "6921",
        "6930",
        "6938",
        "6939",
        # AMDVerdeGraphicsAccelerator
        "6820",
        "6821",
        "6823",
        "6825",
        "6827",
        "682B",
        "682D",
        "682F",
        "6835",
        "6839",
        "683B",
        "683D",
        "683F",
    ]

    polaris_ids = [
        # AMDRadeonX4000
        # AMDBaffinGraphicsAccelerator
        "67E0",
        "67E3",
        "67E8",
        "67EB",
        "67EF",
        "67FF",
        "67E1",
        "67E7",
        "67E9",
        # AMDEllesmereGraphicsAccelerator
        "67C0",
        "67C1",
        "67C2",
        "67C4",
        "67C7",
        "67DF",
        "67D0",
        "67C8",
        "67C9",
        "67CA",
        "67CC",
        "67CF",
    ]

    vega_ids = [
        # AMDRadeonX5000
        # AMDVega10GraphicsAccelerator
        "6860",
        "6861",
        "6862",
        "6863",
        "6864",
        "6867",
        "6868",
        "6869",
        "686A",
        "686B",
        "686C",
        "686D",
        "686E",
        "686F",
        "687F",
        # AMDVega12GraphicsAccelerator
        "69A0",
        "69A1",
        "69A2",
        "69A3",
        "69AF",
        # AMDVega20GraphicsAccelerator
        "66A0",
        "66A1",
        "66A2",
        "66A3",
        "66A7",
        "66AF",
    ]

    navi_ids = [
        # AMDRadeonX6000
        # AMDNavi10GraphicsAccelerator
        "7310",
        "7312",
        "7318",
        "7319",
        "731A",
        "731B",
        "731F",
        # AMDNavi12GraphicsAccelerator
        "7360",
        # AMDNavi14GraphicsAccelerator
        "7340",
        "7341",
        "7343",
        "7347",
        "734F",
        # AMDNavi21GraphicsAccelerator
        "73A2",
        "73AB",
        "73BF",
    ]
    terascale_1_ids = [
        "9400",
        "9401",
        "9402",
        "9403",
        "9581",
        "9583",
        "9588",
        "94C8",
        "94C9",
        "9500",
        "9501",
        "9505",
        "9507",
        "9504",
        "9506",
        "9598",
        "9488",
        "9599",
        "9591",
        "9593",
        "9440",
        "9442",
        "944A",
        "945A",
        "9490",
        "949E",
        "9480",
        "9540",
        "9541",
        "954E",
        "954F",
        "9552",
        "9553",
        "94A0",
    ]

    terascale_2_ids = [
        "6738",
        "6739",
        "6720",
        "6722",
        "6768",
        "6770",
        "6779",
        "6760",
        "6761",
        "68E0",
        "6898",
        "6899",
        "68B8",
        "68B0",
        "68B1",
        "68A0",
        "68A1",
        "6840",
        "6841",
        "68D8",
        "68C0",
        "68C1",
        "68D9",
        "6750",
        "6758",
        "6759",
        "6740",
        "6741",
        "6745",
    ]


class intel_ids:
    iron_ids = [
        # AppleIntelHDGraphics IDs
        "0044",
        "0046",
    ]

    sandy_ids = [
        # AppleIntelHD3000Graphics IDs
        # AppleIntelSNBGraphicsFB IDs
        "0106",
        "0601",
        "0116",
        "0102",
        "0126",
    ]

    ivy_ids = [
        # AppleIntelHD4000Graphics IDs
        # AppleIntelFramebufferCapri IDs
        "0152",
        "0156",
        "0162",
        "0166",
    ]


class broadcom_ids:
    AirPortBrcmNIC = [
        # AirPortBrcmNIC IDs
        "43BA",  # BCM43602
        "43A3",  # BCM4350
        "43A0",  # BCM4360
    ]

    AirPortBrcm4360 = [
        # AirPortBrcm4360 IDs (removed duplicates for 4360 class cards)
        "4331",  # BCM94331
        "4353",  # BCM943224
    ]

    AirPortBrcm4331 = [
        # AirPortBrcm4331 IDs (removed duplicates for 4331 class cards)
        "432B",  # BCM94322
    ]

    AppleAirPortBrcm43224 = [
        # AppleAirPortBrcm43224 IDs
        "4311",  # BCM4311 - never used by Apple
        "4312",  # BCM4311 - never used by Apple
        "4313",  # BCM4311 - never used by Apple
        "4318",  # BCM4318 - never used by Apple
        "4319",  # BCM4318 - never used by Apple
        "431A",  # Unknown - never used by Apple
        "4320",  # BCM4306 - never used by Apple
        "4324",  # BCM4309 - never used by Apple
        "4325",  # BCM4306 - never used by Apple
        "4328",  # BCM4328
        "432C",  # BCM4322 - never used by Apple
        "432D",  # BCM4322 - never used by Apple
    ]


class atheros_ids:
    AtherosWifi = [
        # AirPortAtheros40 IDs
        "0030",  # AR93xx
        "002A",  # AR928X
        "001C",  # AR242x / AR542x
        "0023",  # AR5416 - never used by Apple
        "0024",  # AR5418
    ]
