"""
example_data.py: Sample Hardware probes, for use in OpenCore Legacy Patcher validation
"""

from ..detections import device_probe


class MacBook:

    MacBook71 = device_probe.Computer(
        real_model="MacBook7,1",
        real_board_id="Mac-F22C89C8",
        reported_model="MacBook7,1",
        reported_board_id="Mac-F22C89C8",
        gpus=[
            device_probe.NVIDIA(vendor_id=4318, device_id=2208, class_code=196608, name="IGPU", model="NVIDIA GeForce 320M", pci_path="PciRoot(0x0)/Pci(0x2,0x0)"),
        ],
        igpu=device_probe.NVIDIA(vendor_id=4318, device_id=2208, class_code=196608, name="IGPU", model="NVIDIA GeForce 320M", pci_path="PciRoot(0x0)/Pci(0x2,0x0)"),
        dgpu=None,
        storage=[
            device_probe.SATAController(vendor_id=4318, device_id=3464, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0xa,0x0)"),
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17235, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Core(TM)2 Duo CPU     P8600  @ 2.40GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "SMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

class MacBookPro:

    MacBookPro92_Stock = device_probe.Computer(
        real_model="MacBookPro9,2",
        real_board_id="Mac-6F01561E16C75D06",
        reported_model="MacBookPro9,2",
        reported_board_id="Mac-6F01561E16C75D06",
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=358, class_code=196608, name="IGPU", model="Intel HD Graphics 4000", pci_path="PciRoot(0x0)/Pci(0x2,0x0)")
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=358, class_code=196608, name="IGPU", model="Intel HD Graphics 4000", pci_path="PciRoot(0x0)/Pci(0x2,0x0)"),
        dgpu=None,
        storage=[device_probe.SATAController(vendor_id=32902, device_id=7683, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17201, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-3210M CPU @ 2.50GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'EST', 'TM2', 'SSSE3', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    MacBookPro111_Stock = device_probe.Computer(
        real_model='MacBookPro11,1',
        real_board_id='Mac-189A3D4F975D5FFC',
        reported_model='MacBookPro11,1',
        reported_board_id='Mac-189A3D4F975D5FFC',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=2606, class_code=196608, name='IGPU', model='Intel Iris', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)')
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=2606, class_code=196608, name='IGPU', model='Intel Iris', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
        dgpu=None,
        storage=[
            device_probe.SATAController(vendor_id=6987, device_id=37251, class_code=67073, name='SSD0', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP06@1c0005/SSD0@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x5)/Pci(0x0,0x0)')
        ],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=32902, device_id=39985, class_code=787248, name='XHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/XHC1@140000', pci_path='PciRoot(0x0)/Pci(0x14,0x0)')
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17312, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP03@1c0002/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x2)/Pci(0x0,0x0)'),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-4258U CPU @ 2.40GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'EST', 'TM2', 'SSSE3', 'FMA', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'SEGLIM64', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=[],
        ),
        oclp_version='0.4.2',
        opencore_version='DBG-077-2022-01-10',
        bluetooth_chipset='BRCM20702 Hub',
        third_party_sata_ssd=False
    )

    MacBookPro133_Stock = device_probe.Computer(
        real_model='MacBookPro13,3',
        real_board_id='Mac-A5C67F76ED83108C',
        reported_model='MacBookPro13,3',
        reported_board_id='Mac-A5C67F76ED83108C',
        build_model='MacBookPro13,3',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=6427, class_code=196608, name='IGPU', model='Intel HD Graphics 530', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False),
            device_probe.AMD(vendor_id=4098, device_id=26607, class_code=196608, name='GFX0', model='AMD Radeon Pro 455', acpi_path='IOACPIPlane:/_SB/PCI0@0/PEG0@10000/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=6427, class_code=196608, name='IGPU', model='Intel HD Graphics 530', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False),
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26607, class_code=196608, name='GFX0', model='AMD Radeon Pro 455', acpi_path='IOACPIPlane:/_SB/PCI0@0/PEG0@10000/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
        storage=[
            device_probe.NVMeController(vendor_id=5197, device_id=43012, class_code=67586, name='SSD0', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP17@1b0000/SSD0@0', pci_path='PciRoot(0x0)/Pci(0x1b,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False, aspm=258)
        ],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=32902, device_id=41263, class_code=787248, name='XHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/XHC1@140000', pci_path='PciRoot(0x0)/Pci(0x14,0x0)', disable_metal=False, force_compatible=False),
            device_probe.XHCIController(vendor_id=32902, device_id=5588, class_code=787248, name='XHC3', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/PEG2@10002/UPSB@0/DSB2@20000/XHC3@0', pci_path='PciRoot(0x0)/Pci(0x1,0x2)/Pci(0x0,0x0)/Pci(0x2,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
            device_probe.XHCIController(vendor_id=32902, device_id=5588, class_code=787248, name='XHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/PEG1@10001/UPSB@0/DSB2@20000/XHC2@0', pci_path='PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x0)/Pci(0x2,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        sdxc_controller=[],
        ethernet=[],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17338, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i7-6820HQ CPU @ 2.70GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'FMA', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'SEGLIM64', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=[]
        ),
        oclp_version='0.5.0',
        opencore_version=None,
        opencore_path=None,
        bluetooth_chipset=None,
        ambient_light_sensor=False,
        third_party_sata_ssd=False,
        secure_boot_model='x86legacyap',
        secure_boot_policy=0,
        oclp_sys_version=None,
        oclp_sys_date=None,
        oclp_sys_url=None,
        firmware_vendor='Apple'
    )

    MacBookPro141_SSD_Upgrade = device_probe.Computer(
        real_model='MacBookPro14,1',
        real_board_id='Mac-B4831CEBD52A0C4C',
        reported_model='MacBookPro14,1',
        reported_board_id='Mac-B4831CEBD52A0C4C',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=22822, class_code=196608, name='IGPU', model='Intel Iris Plus Graphics 640', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)')
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=22822, class_code=196608, name='IGPU', model='Intel Iris Plus Graphics 640', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
        dgpu=None,
        storage=[
            device_probe.NVMeController(vendor_id=6535, device_id=20499, class_code=67586, name='SSD0', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/SSD0@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)', aspm=2)
        ],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=32902, device_id=40239, class_code=787248, name='XHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/XHC1@140000', pci_path='PciRoot(0x0)/Pci(0x14,0x0)'),
            device_probe.XHCIController(vendor_id=32902, device_id=5588, class_code=787248, name='XHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP05@1c0004/UPSB@0/DSB2@20000/XHC2@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x4)/Pci(0x0,0x0)/Pci(0x2,0x0)/Pci(0x0,0x0)')
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17315, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP09@1d0000/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1d,0x0)/Pci(0x0,0x0)'),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-7360U CPU @ 2.30GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'FMA', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'SEGLIM64', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=[],
        ), oclp_version='0.4.1',
        opencore_version=None,
        bluetooth_chipset=None,
        third_party_sata_ssd=False)

    MacBookPro171_Stock = device_probe.Computer(
        # Run under Rosetta
        real_model="MacBookPro17,1",
        real_board_id="J293",
        reported_model="MacBookPro17,1",
        reported_board_id="J293",
        gpus=[device_probe.AMD(vendor_id=4098, device_id=26640, class_code=196608, name="display", model="Unknown Unknown", pci_path="")],
        igpu=None,
        dgpu=None,
        storage=[],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17445, class_code=163840, name="wlan", model=None, pci_path=""),
        cpu=device_probe.CPU(
            name="Apple M1",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "PCLMULQDQ", "DTSE64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "AES", "SEGLIM64"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

class Macmini:

    Macmini52_Stock = device_probe.Computer(
        real_model='Macmini5,2',
        real_board_id='Mac-4BC72D62AD45599E',
        reported_model='Macmini5,2',
        reported_board_id='Mac-4BC72D62AD45599E',
        build_model='Macmini5,2',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=294, class_code=229376, name='IGPU', model='Intel HD Graphics 3000', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False),
            device_probe.AMD(vendor_id=4098, device_id=26433, class_code=196608, name='GFX0', model='AMD Radeon HD 6630M', acpi_path='IOACPIPlane:/_SB/PCI0@0/P0P2@10000/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)],
        igpu=device_probe.Intel(vendor_id=32902, device_id=294, class_code=229376, name='IGPU', model='Intel HD Graphics 3000', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False),
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26433, class_code=196608, name='GFX0', model='AMD Radeon HD 6630M', acpi_path='IOACPIPlane:/_SB/PCI0@0/P0P2@10000/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=7171, class_code=67073, name='SATA', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SATA@1f0002', pci_path='PciRoot(0x0)/Pci(0x1f,0x2)', disable_metal=False, force_compatible=False)
        ],
        usb_controllers=[
            device_probe.EHCIController(vendor_id=32902, device_id=7213, class_code=787232, name='EHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC2@1a0007', pci_path='PciRoot(0x0)/Pci(0x1a,0x7)', disable_metal=False, force_compatible=False),
            device_probe.EHCIController(vendor_id=32902, device_id=7206, class_code=787232, name='EHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC1@1d0007', pci_path='PciRoot(0x0)/Pci(0x1d,0x7)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=7212, class_code=787200, name='UHC5', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC5@1a0000', pci_path='PciRoot(0x0)/Pci(0x1a,0x0)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=7207, class_code=787200, name='UHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC1@1d0000', pci_path='PciRoot(0x0)/Pci(0x1d,0x0)', disable_metal=False, force_compatible=False)
        ],
        sdxc_controller=[
            device_probe.SDXCController(vendor_id=5348, device_id=5820, class_code=525569, name='SDXC', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/SDXC@1', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x1)', disable_metal=False, force_compatible=False)
        ],
        ethernet=[
            device_probe.BroadcomEthernet(vendor_id=5348, device_id=5812, class_code=131072, name='GIGE', model='Broadcom 57765-B0', acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/GIGE@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17201, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP02@1c0001/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-2520M CPU @ 2.50GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'TSCTMR', 'AVX1.0'],
            leafs=['']
        ),
        oclp_version='0.5.0',
        opencore_version='REL-083-2022-08-01',
        opencore_path='PciRoot(0x0)/Pci(0x1F,0x2)/Sata(0x0,0x0,0x0)/HD(1,GPT,D011D782-7E9A-459B-905D-9DA8D6494A53,0x28,0x64000)/EFI\\OC\\OpenCore.efi',
        bluetooth_chipset='BRCM20702 Hub',
        ambient_light_sensor=False,
        third_party_sata_ssd=True,
        secure_boot_model='x86legacyap',
        secure_boot_policy=0,
        oclp_sys_version='v0.4.11',
        oclp_sys_date='October 06, 2022 @ 10:06:53',
        oclp_sys_url=None,
        firmware_vendor='Apple',
        rosetta_active=False
    )

    Macmini61_Stock = device_probe.Computer(
        real_model='Macmini6,1',
        real_board_id='Mac-031AEE4D24BFF0B1',
        reported_model='Macmini6,1',
        reported_board_id='Mac-031AEE4D24BFF0B1',
        build_model='Macmini6,1',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=358, class_code=196608, name='IGPU', model='Intel HD Graphics 4000', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False)
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=358, class_code=196608, name='IGPU', model='Intel HD Graphics 4000', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False),
        dgpu=None,
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=7683, class_code=67073, name='SATA', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SATA@1f0002', pci_path='PciRoot(0x0)/Pci(0x1f,0x2)', disable_metal=False, force_compatible=False)
        ],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=32902, device_id=7729, class_code=787248, name='XHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/XHC1@140000', pci_path='PciRoot(0x0)/Pci(0x14,0x0)', disable_metal=False, force_compatible=False),
            device_probe.EHCIController(vendor_id=32902, device_id=7725, class_code=787232, name='EHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC2@1a0000', pci_path='PciRoot(0x0)/Pci(0x1a,0x0)', disable_metal=False, force_compatible=False),
            device_probe.EHCIController(vendor_id=32902, device_id=7718, class_code=787232, name='EHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC1@1d0000', pci_path='PciRoot(0x0)/Pci(0x1d,0x0)', disable_metal=False, force_compatible=False)
        ],
        sdxc_controller=[
            device_probe.SDXCController(vendor_id=5348, device_id=5820, class_code=525569, name='SDXC', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/SDXC@1', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x1)', disable_metal=False, force_compatible=False)
        ],
        ethernet=[
            device_probe.BroadcomEthernet(vendor_id=5348, device_id=5766, class_code=131072, name='GIGE', model='Broadcom 57766-A1', acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/GIGE@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17201, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP02@1c0001/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False
        ),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-3210M CPU @ 2.50GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'EST', 'TM2', 'SSSE3', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=['RDWRFSGS', 'SMEP', 'ERMS', 'MDCLEAR', 'IBRS', 'STIBP', 'L1DF', 'SSBD']
        ),
        oclp_version='0.5.0',
        opencore_version='REL-083-2022-08-01',
        opencore_path='PciRoot(0x0)/Pci(0x1F,0x2)/Sata(0x0,0x0,0x0)/HD(1,GPT,B46958E3-7EB7-40C2-BB3A-2C88A0856DC7,0x28,0x64000)/EFI\\OC\\OpenCore.efi',
        bluetooth_chipset='BRCM20702 Hub',
        ambient_light_sensor=False,
        third_party_sata_ssd=True,
        secure_boot_model='x86legacyap',
        secure_boot_policy=0,
        oclp_sys_version='v0.5.0',
        oclp_sys_date='October 04, 2022 @ 12:24:50',
        oclp_sys_url='',
        firmware_vendor='Apple',
        rosetta_active=False
    )

    Macmini71_Stock = device_probe.Computer(
        real_model='Macmini7,1',
        real_board_id='Mac-35C5E08120C7EEAF',
        reported_model='Macmini7,1',
        reported_board_id='Mac-35C5E08120C7EEAF',
        build_model='Macmini7,1',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=2606, class_code=196608, name='IGPU', model='Intel Iris', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False)
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=2606, class_code=196608, name='IGPU', model='Intel Iris', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)', disable_metal=False, force_compatible=False),
        dgpu=None,
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=39939, class_code=67073, name='SATA', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SATA@1f0002', pci_path='PciRoot(0x0)/Pci(0x1f,0x2)', disable_metal=False, force_compatible=False)
        ],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=32902, device_id=39985, class_code=787248, name='XHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/XHC1@140000', pci_path='PciRoot(0x0)/Pci(0x14,0x0)', disable_metal=False, force_compatible=False)
        ],
        sdxc_controller=[
            device_probe.SDXCController(vendor_id=5348, device_id=5820, class_code=525569, name='SDXC', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP04@1c0003/SDXC@1', pci_path='PciRoot(0x0)/Pci(0x1c,0x3)/Pci(0x0,0x1)', disable_metal=False, force_compatible=False)
        ],
        ethernet=[
            device_probe.BroadcomEthernet(vendor_id=5348, device_id=5766, class_code=131072, name='GIGE', model='Broadcom 57766-A1', acpi_path='IOACPIPlane:/_SB/PCI0@0/RP04@1c0003/GIGE@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x3)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17312, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP03@1c0002/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x2)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-4278U CPU @ 2.60GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'EST', 'TM2', 'SSSE3', 'FMA', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'SEGLIM64', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=['RDWRFSGS', 'TSC_THREAD_OFFSET', 'BMI1', 'AVX2', 'SMEP', 'BMI2', 'ERMS', 'INVPCID', 'FPU_CSDS', 'MDCLEAR', 'IBRS', 'STIBP', 'L1DF', 'SSBD']
        ),
        oclp_version='0.5.0',
        opencore_version='REL-083-2022-08-01',
        opencore_path='PciRoot(0x0)/Pci(0x1F,0x2)/Sata(0x0,0x0,0x0)/HD(1,GPT,293E8ABF-B98C-4258-A811-04464BCA90EF,0x28,0x64000)/EFI\\OC\\OpenCore.efi',
        bluetooth_chipset='BRCM20702 Hub',
        ambient_light_sensor=False,
        third_party_sata_ssd=True,
        secure_boot_model='x86legacyap',
        secure_boot_policy=0,
        oclp_sys_version='v0.5.0',
        oclp_sys_date='October 04, 2022 @ 12:04:48',
        oclp_sys_url='https://github.com/dortania/OpenCore-Legacy-Patcher/commit/daf28a62effb2ce06a71cb5961c9d0c79d72c16b',
        firmware_vendor='Apple',
        rosetta_active=False
    )

    Macmini81_Stock = device_probe.Computer(
        real_model="Macmini8,1",
        real_board_id="Mac-7BA5B2DFE22DDD8C",
        reported_model="Macmini8,1",
        reported_board_id="Mac-7BA5B2DFE22DDD8C",
        gpus=[device_probe.Intel(vendor_id=32902, device_id=16027, class_code=196608, name="IGPU", model="Intel UHD Graphics 630", pci_path="PciRoot(0x0)/Pci(0x2,0x0)")],
        igpu=device_probe.Intel(vendor_id=32902, device_id=16027, class_code=196608, name="IGPU", model="Intel UHD Graphics 630", pci_path="PciRoot(0x0)/Pci(0x2,0x0)"),
        dgpu=None,
        storage=[],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17508, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Core(TM) i7-8700B CPU @ 3.20GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "PCLMULQDQ", "DTES64", "MON", "DSCPL", "VMX", "SMX", "EST", "TM2", "SSSE3", "FMA", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "x2APIC", "MOVBE", "POPCNT", "AES", "PCID", "XSAVE", "OSXSAVE", "SEGLIM64", "TSCTMR", "AVX1.0", "RDRAND", "F16C"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None
    )

    Macmini91_Stock = device_probe.Computer(
        # Run under Rosetta
        real_model="Macmini9,1",
        real_board_id="J274",
        reported_model="Macmini9,1",
        reported_board_id="J274",
        gpus=[
            device_probe.AMD(vendor_id=4098, device_id=26640, class_code=196608, name="display", model="Unknown Unknown", pci_path="", )
        ],
        igpu=None,
        dgpu=None,
        storage=[],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17445, class_code=163840, name="wlan", model=None, pci_path=""),
        cpu=device_probe.CPU(
            name="Apple M1",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "PCLMULQDQ", "DTSE64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "AES", "SEGLIM64"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None
    )

class iMac:

    iMac81_Stock = device_probe.Computer(
        # Stock Model
        real_model="iMac8,1",
        real_board_id="Mac-F226BEC8",
        reported_model="iMac8,1",
        reported_board_id="Mac-F226BEC8",
        gpus=[
            device_probe.AMD(vendor_id=4098, device_id=38088, class_code=196608, name="GFX0", model="ATI Radeon HD 2400", pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)")
        ],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=38088, class_code=196608, name="GFX0", model="ATI Radeon HD 2400", pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=10281, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17192, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x4)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Core(TM)2 Duo CPU     E8135  @ 2.40GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    iMac112_Stock = device_probe.Computer(
        # Stock Model
        real_model="iMac11,2",
        real_board_id="Mac-F2238AC8",
        reported_model="iMac11,2",
        reported_board_id="Mac-F2238AC8",
        gpus=[
            device_probe.AMD(vendor_id=4098, device_id=38024, class_code=196608, name="GFX0", model="ATI Radeon HD 4670", pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)")
        ],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=38024, class_code=196608, name="GFX0", model="ATI Radeon HD 4670", pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=15138, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=device_probe.Atheros(vendor_id=5772, device_id=42, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Core(TM) i3 CPU         540  @ 3.07GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "POPCNT", "PCID"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    iMac122_Upgraded = device_probe.Computer(
        real_model="iMac12,2",
        real_board_id="Mac-942B59F58194171B",
        reported_model="iMac12,2",
        reported_board_id="Mac-942B59F58194171B",
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=258, class_code=196608, name="HD Graphics 3000", model=None, pci_path="PciRoot(0x0)/Pci(0x2,0x0)"),
            device_probe.AMD(vendor_id=4098, device_id=26600, class_code=196608, name="GFX0", model="Radeon Pro WX4130", pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"),
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=258, class_code=196608, name="HD Graphics 3000", model=None, pci_path="PciRoot(0x0)/Pci(0x2,0x0)"),
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26600, class_code=196608, name="GFX0", model="Radeon Pro WX4130", pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=7170, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17338, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Core(TM) i7-2600 CPU @ 3.40GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "PCLMULQDQ", "DTES64", "MON", "DSCPL", "VMX", "SMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "xAPIC", "POPCNT", "AES", "PCID", "XSAVE", "OSXSAVE", "TSCTMR", "AVX1.0"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    iMac122_Upgraded_Nvidia = device_probe.Computer(
        real_model='iMac12,2',
        real_board_id='Mac-942B59F58194171B',
        reported_model='iMac12,2',
        reported_board_id='Mac-942B59F58194171B',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=258, class_code=229376, name='IGPU',  model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
            device_probe.NVIDIA(vendor_id=4318, device_id=4092, class_code=196608, name='GFX0', model='Quadro K1000M by Nick[D]vB', acpi_path='IOACPIPlane:/_SB/PCI0@0/P0P2@10000/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)')],
        igpu=device_probe.Intel(vendor_id=32902, device_id=258, class_code=229376, name='IGPU', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
        dgpu=device_probe.NVIDIA(vendor_id=4318, device_id=4092, class_code=196608, name='GFX0', model='Quadro K1000M by Nick[D]vB', acpi_path='IOACPIPlane:/_SB/PCI0@0/P0P2@10000/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)'),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=7170, class_code=67073, name='SATA', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SATA@1f0002', pci_path='PciRoot(0x0)/Pci(0x1f,0x2)')
        ],
        usb_controllers=[
            device_probe.EHCIController(vendor_id=32902, device_id=7213, class_code=787232, name='EHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC2@1a0007', pci_path='PciRoot(0x0)/Pci(0x1a,0x7)'),
            device_probe.EHCIController(vendor_id=32902, device_id=7206, class_code=787232, name='EHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC1@1d0007', pci_path='PciRoot(0x0)/Pci(0x1d,0x7)')
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17201, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP02@1c0001/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)'),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i7-2600 CPU @ 3.40GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'TSCTMR', 'AVX1.0'],
            leafs=[],
        ),
        oclp_version='0.3.3',
        opencore_version=None,
        bluetooth_chipset='BRCM2046 Hub',
        third_party_sata_ssd=True
    )

    iMac151_Stock = device_probe.Computer(
        real_model='iMac15,1',
        real_board_id='Mac-42FD25EABCABB274',
        reported_model='iMac15,1',
        reported_board_id='Mac-42FD25EABCABB274',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=1042, class_code=196608, name='IGPU', model='Intel Iris Pro', acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
            device_probe.AMD(vendor_id=4098, device_id=26640, class_code=196608, name='GFX0', model='AMD Radeon R9 M290X', acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)')
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=1042, class_code=196608, name='IGPU', model='Intel Iris Pro', acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26640, class_code=196608, name='GFX0', model='AMD Radeon R9 M290X', acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)'),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=35842, class_code=67073, name='SATA', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1f,0x2)'),
            device_probe.SATAController(vendor_id=6987, device_id=37251, class_code=67073, name='SSD0', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)')
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17312, class_code=163840, name='ARPT', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1c,0x2)/Pci(0x0,0x0)'),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-4690 CPU @ 3.50GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'FMA', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'SEGLIM64', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
        bluetooth_chipset='BRCM20702 Hub',
        third_party_sata_ssd=False
    )

    iMac201_Stock = device_probe.Computer(
        real_model='iMac20,1',
        real_board_id='Mac-CFF7D910A743CAAF',
        reported_model='iMac20,1',
        reported_board_id='Mac-CFF7D910A743CAAF',
        gpus=[
            device_probe.Intel(vendor_id=32902, device_id=39880, class_code=196608, name='IGPU', model='Intel HD Graphics CFL', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
            device_probe.AMD(vendor_id=4098, device_id=29504, class_code=196608, name='GFX0', model='AMD Radeon Pro 5300', acpi_path='IOACPIPlane:/_SB/PCI0@0/PEG0@10000/EGP0@0/EGP1@0/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)')
        ],
        igpu=device_probe.Intel(vendor_id=32902, device_id=39880, class_code=196608, name='IGPU', model='Intel HD Graphics CFL', acpi_path='IOACPIPlane:/_SB/PCI0@0/IGPU@20000', pci_path='PciRoot(0x0)/Pci(0x2,0x0)'),
        dgpu=device_probe.AMD(vendor_id=4098, device_id=29504, class_code=196608, name='GFX0', model='AMD Radeon Pro 5300', acpi_path='IOACPIPlane:/_SB/PCI0@0/PEG0@10000/EGP0@0/EGP1@0/GFX0@0', pci_path='PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)'),
        storage=[],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=32902, device_id=1773, class_code=787248, name='XHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/XHC1@140000', pci_path='PciRoot(0x0)/Pci(0x14,0x0)'),
            device_probe.XHCIController(vendor_id=32902, device_id=5612, class_code=787248, name='XHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP05@1c0004/UPSB@0/DSB2@20000/XHC2@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x4)/Pci(0x0,0x0)/Pci(0x2,0x0)/Pci(0x0,0x0)')
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17508, class_code=163840, name='ARPT', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/RP01@1c0000/ARPT@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)'),
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i5-10500 CPU @ 3.10GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'FMA', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'PCID', 'XSAVE', 'OSXSAVE', 'SEGLIM64', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
        bluetooth_chipset=None,
        third_party_sata_ssd=False
    )

class MacPro:

    MacPro31_Stock = device_probe.Computer(
        # Stock Model, stock TS1 GPU and no Wifi card
        real_model="MacPro3,1",
        real_board_id="Mac-F42C88C8",
        reported_model="MacPro3,1",
        reported_board_id="Mac-F42C88C8",
        gpus=[
            device_probe.AMD(vendor_id=4098, device_id=38272, class_code=196608, name="GFX0", model="ATI Radeon HD 2600", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)")
        ],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=38272, class_code=196608, name="GFX0", model="ATI Radeon HD 2600", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=9857, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=None,
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           X5482  @ 3.20GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    MacPro31_Upgrade = device_probe.Computer(
        # Upgraded Model, TS2 GPU and El-Capitan era Wifi card
        real_model="MacPro3,1",
        real_board_id="Mac-F42C88C8",
        reported_model="MacPro3,1",
        reported_board_id="Mac-F42C88C8",
        gpus=[
            device_probe.AMD(vendor_id=4098, device_id=26808, class_code=196608, name="GFX0", model="ATI Radeon HD 5770", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)")
        ],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26808, class_code=196608, name="GFX0", model="ATI Radeon HD 5770", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=9857, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=device_probe.Broadcom(
            vendor_id=5348, device_id=17192, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x3)/Pci(0x0,0x0)"
        ),
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           X5482  @ 3.20GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    MacPro31_Modern_AMD = device_probe.Computer(
        # Upgraded Model, Polaris GPU and BCM94360CD
        real_model="MacPro3,1",
        real_board_id="Mac-F42C88C8",
        reported_model="MacPro3,1",
        reported_board_id="Mac-F42C88C8",
        gpus=[
            device_probe.AMD(vendor_id=4098, device_id=26591, class_code=196608, name="GFX0", model="Radeon RX 470/570", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)")
        ],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26591, class_code=196608, name="GFX0", model="Radeon RX 470/570", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=9857, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=device_probe.Broadcom(
            vendor_id=5348, device_id=17312, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x3)/Pci(0x0,0x0)"
        ),
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           X5482  @ 3.20GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    MacPro31_Modern_Kepler = device_probe.Computer(
        # Upgraded Model, Kepler GPU and BCM94360CD
        real_model="MacPro3,1",
        real_board_id="Mac-F42C88C8",
        reported_model="MacPro3,1",
        reported_board_id="Mac-F42C88C8",
        gpus=[device_probe.NVIDIA(vendor_id=4318, device_id=4737, class_code=196608, name="GFX0", model="NVIDIA GeForce GT 710", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)")],
        igpu=None,
        dgpu=device_probe.NVIDIA(vendor_id=4318, device_id=4737, class_code=196608, name="GFX0", model="NVIDIA GeForce GT 710", pci_path="PciRoot(0x0)/Pci(0x5,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=9857, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")
        ],
        wifi=device_probe.Broadcom(
            vendor_id=5348, device_id=17312, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1c,0x3)/Pci(0x0,0x0)"
        ),
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           X5482  @ 3.20GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None,
    )

    MacPro41_Upgrade = device_probe.Computer(
        # Upgraded model with AMD HD7950, Atheros PCIe card
        real_model="MacPro4,1",
        real_board_id="Mac-F221BEC8",
        reported_model="MacPro4,1",
        reported_board_id="Mac-F221BEC8",
        gpus=[device_probe.AMD(vendor_id=4098, device_id=26522, class_code=196608, name="PXS1", model="AMD Radeon HD 7950", pci_path="PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)")],
        igpu=None,
        dgpu=None,
        storage=[device_probe.SATAController(vendor_id=32902, device_id=14882, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)")],
        wifi=device_probe.Atheros(vendor_id=5772, device_id=48, class_code=163840, name="PXS4", model=None, pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x4,0x0)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           W3520  @ 2.67GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "POPCNT"],
            leafs=[],
        ),
        oclp_version=None,
        opencore_version=None
    )

    MacPro41_Modern_AMD = device_probe.Computer(
        # Upgraded model with AMD RX470, BCM94360CD, Intel 660p
        # Booted through OpenCore
        real_model="MacPro4,1",
        real_board_id="Mac-F221BEC8",
        reported_model="MacPro4,1",
        reported_board_id="Mac-27AD2F918AE68F61",
        gpus=[device_probe.AMD(vendor_id=4098, device_id=26591, class_code=196608, name="GFX0", model="Radeon RX 470/570", pci_path="PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)")],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=26591, class_code=196608, name="GFX0", model="Radeon RX 470/570", pci_path="PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=14882, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)"),
            device_probe.NVMeController(vendor_id=32902, device_id=61864, class_code=67586, name="PXS3", model=None, pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x2,0x0)/Pci(0x0,0x0)", aspm=2)
        ],
        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17312, class_code=163840, name="ARPT", model=None, pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x4,0x0)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           W3520  @ 2.67GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON", "DSCPL", "VMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "POPCNT"],
            leafs=[],
        ),
        oclp_version="0.2.5",
        opencore_version="REL-071-2021-07-02"
    )

    MacPro41_51__Flashed_Modern_AMD = device_probe.Computer(
        # 4,1 flashed to 5,1, RX5700XT, BCM94360CD, WD SN750 NVMe
        real_model="MacPro5,1",
        real_board_id="Mac-F221BEC8",
        reported_model="MacPro5,1",
        reported_board_id="Mac-F221BEC8",
        gpus=[device_probe.AMD(vendor_id=4098, device_id=29471, class_code=196608, name="GFX0", model="AMD Radeon RX 5700 XT", pci_path="PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)")],
        igpu=None,
        dgpu=device_probe.AMD(vendor_id=4098, device_id=29471, class_code=196608, name="GFX0", model="AMD Radeon RX 5700 XT", pci_path="PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=14882, class_code=67073, name="SATA", model=None, pci_path="PciRoot(0x0)/Pci(0x1f,0x2)"),
            device_probe.NVMeController(vendor_id=5559, device_id=20482, class_code=67586, name="PXS3", model=None, pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x2,0x0)/Pci(0x0,0x0)", aspm=2)
        ],

        wifi=device_probe.Broadcom(vendor_id=5348, device_id=17312, class_code=163840, name="PXS4", model=None, pci_path="PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x4,0x0)/Pci(0x0,0x0)"),
        cpu=device_probe.CPU(
            name="Intel(R) Xeon(R) CPU           X5670  @ 2.93GHz",
            flags=["FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP", "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX", "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "PCLMULQDQ", "DTES64", "MON", "DSCPL", "VMX", "SMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "SSE4.1", "SSE4.2", "POPCNT", "AES", "PCID"],
            leafs=[],
        ),
        oclp_version="0.2.5",
        opencore_version="REL-071-2021-07-02"
    )

    MacPro41_51_Flashed_NVIDIA_WEB_DRIVERS = device_probe.Computer(
        real_model='MacPro5,1',
        real_board_id='Mac-F221BEC8',
        reported_model='MacPro5,1',
        reported_board_id='Mac-F221BEC8',
        build_model='MacPro5,1',
        gpus=[
            device_probe.NVIDIA(vendor_id=4318, device_id=5051, class_code=196608, name='GFX0', model='NVIDIA Quadro K620', acpi_path='IOACPIPlane:/_SB/PCI0@0/IOU0@30000/PXS1@ffff', pci_path='PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)', disable_metal=True, force_compatible=True)
        ],
        igpu=None,
        dgpu=device_probe.NVIDIA(vendor_id=4318, device_id=5051, class_code=196608, name='GFX0', model='NVIDIA Quadro K620', acpi_path='IOACPIPlane:/_SB/PCI0@0/IOU0@30000/PXS1@ffff', pci_path='PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)', disable_metal=True, force_compatible=True),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=14882, class_code=67073, name='SATA', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SATA@1f0002', pci_path='PciRoot(0x0)/Pci(0x1f,0x2)', disable_metal=False, force_compatible=False)
        ],
        usb_controllers=[
            device_probe.EHCIController(vendor_id=32902, device_id=14908, class_code=787232, name='EHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC2@1a0007', pci_path='PciRoot(0x0)/Pci(0x1a,0x7)', disable_metal=False, force_compatible=False),
            device_probe.EHCIController(vendor_id=32902, device_id=14906, class_code=787232, name='EHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/EHC1@1d0007', pci_path='PciRoot(0x0)/Pci(0x1d,0x7)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=14903, class_code=787200, name='UHC4', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC4@1a0000', pci_path='PciRoot(0x0)/Pci(0x1a,0x0)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=14904, class_code=787200, name='UHC5', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC5@1a0001', pci_path='PciRoot(0x0)/Pci(0x1a,0x1)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=14905, class_code=787200, name='UHC6', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC6@1a0002', pci_path='PciRoot(0x0)/Pci(0x1a,0x2)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=14900, class_code=787200, name='UHC1', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC1@1d0000', pci_path='PciRoot(0x0)/Pci(0x1d,0x0)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=14901, class_code=787200, name='UHC2', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC2@1d0001', pci_path='PciRoot(0x0)/Pci(0x1d,0x1)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=14902, class_code=787200, name='UHC3', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/UHC3@1d0002', pci_path='PciRoot(0x0)/Pci(0x1d,0x2)', disable_metal=False, force_compatible=False)
        ],
        sdxc_controller=[],
        ethernet=[
            device_probe.IntelEthernet(vendor_id=32902, device_id=4342, class_code=131072, name='ETH1', model='Intel 82574L', acpi_path='IOACPIPlane:/_SB/PCI0@0/RP04@1c0003/ETH1@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x3)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
            device_probe.IntelEthernet(vendor_id=32902, device_id=4342, class_code=131072, name='ETH0', model='Intel 82574L', acpi_path='IOACPIPlane:/_SB/PCI0@0/RP03@1c0002/ETH0@0', pci_path='PciRoot(0x0)/Pci(0x1c,0x2)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        wifi=None,
        cpu=device_probe.CPU(
            name='Intel(R) Xeon(R) CPU           X5670  @ 2.93GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'DS', 'ACPI', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'TM', 'PBE', 'SSE3', 'PCLMULQDQ', 'DTES64', 'MON', 'DSCPL', 'VMX', 'SMX', 'EST', 'TM2', 'SSSE3', 'CX16', 'TPR', 'PDCM', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCID'],
            leafs=[],
        ),
        oclp_version='0.4.6',
        opencore_version='REL-080-2022-04-18',
        opencore_path='PciRoot(0x0)/Pci(0x1D,0x7)/USB(0x4,0x0)/HD(2,GPT,AEC1E933-C311-40E2-BBCE-FC4B14BCD770,0x64800,0x38E3000)/EFI\\OC\\OpenCore.efi',
        bluetooth_chipset='BRCM2046 Hub',
        ambient_light_sensor=False,
        third_party_sata_ssd=True,
        secure_boot_model='x86legacyap',
        secure_boot_policy=0,
        oclp_sys_version='v0.4.6',
        oclp_sys_date='September 03, 2019 @ 23:13:43',
        firmware_vendor='Apple'
    )


class Hackintosh:

    QEMU_Virtual_Machine_GT710 = device_probe.Computer(
        real_model='iMac14,4',
        real_board_id='Mac-81E3E92DD6088272',
        reported_model='iMac14,4',
        reported_board_id='Mac-81E3E92DD6088272',
        build_model=None,
        gpus=[
            device_probe.NVIDIA(vendor_id=4318, device_id=4747, class_code=196608, name='GFX0', model='NVIDIA GeForce GT 710', acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False)
        ],
        igpu=None,
        dgpu=device_probe.NVIDIA(vendor_id=4318, device_id=4747, class_code=196608, name='GFX0', model='NVIDIA GeForce GT 710', acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1c,0x0)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
        storage=[
            device_probe.SATAController(vendor_id=32902, device_id=10530, class_code=67073, name='pci8086,2922', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1f,0x2)', disable_metal=False, force_compatible=False),
            device_probe.SATAController(vendor_id=32902, device_id=10530, class_code=67073, name='pci8086,2922', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1e,0x0)/Pci(0x1,0x0)/Pci(0x7,0x0)', disable_metal=False, force_compatible=False),
            device_probe.NVMeController(vendor_id=5197, device_id=43016, class_code=67586, name='pci144d,a808', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1c,0x1)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False, aspm=0)
        ],
        usb_controllers=[
            device_probe.XHCIController(vendor_id=6945, device_id=8514, class_code=787248, name='pci1b21,2142', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1c,0x2)/Pci(0x0,0x0)', disable_metal=False, force_compatible=False),
            device_probe.EHCIController(vendor_id=32902, device_id=10556, class_code=787232, name='pci8086,293c', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1a,0x7)', disable_metal=False, force_compatible=False),
            device_probe.EHCIController(vendor_id=32902, device_id=10554, class_code=787232, name='pci8086,293a', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1d,0x7)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=10551, class_code=787200, name='SD0', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SD0@1a0000', pci_path='PciRoot(0x0)/Pci(0x1a,0x0)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=10552, class_code=787200, name='pci8086,2938', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1a,0x1)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=10553, class_code=787200, name='pci8086,2939', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1a,0x2)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=10548, class_code=787200, name='SE8', model=None, acpi_path='IOACPIPlane:/_SB/PCI0@0/SE8@1d0000', pci_path='PciRoot(0x0)/Pci(0x1d,0x0)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=10549, class_code=787200, name='pci8086,2935', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1d,0x1)', disable_metal=False, force_compatible=False),
            device_probe.UHCIController(vendor_id=32902, device_id=10550, class_code=787200, name='pci8086,2936', model=None, acpi_path=None, pci_path='PciRoot(0x0)/Pci(0x1d,0x2)', disable_metal=False, force_compatible=False)
        ],
        sdxc_controller=[],
        ethernet=[],
        wifi=None,
        cpu=device_probe.CPU(
            name='Intel(R) Core(TM) i9-7920X CPU @ 2.90GHz',
            flags=['FPU', 'VME', 'DE', 'PSE', 'TSC', 'MSR', 'PAE', 'MCE', 'CX8', 'APIC', 'SEP', 'MTRR', 'PGE', 'MCA', 'CMOV', 'PAT', 'PSE36', 'CLFSH', 'MMX', 'FXSR', 'SSE', 'SSE2', 'SS', 'HTT', 'SSE3', 'PCLMULQDQ', 'VMX', 'SSSE3', 'FMA', 'CX16', 'PDCM', 'SSE4.1', 'SSE4.2', 'x2APIC', 'MOVBE', 'POPCNT', 'AES', 'VMM', 'PCID', 'XSAVE', 'OSXSAVE', 'TSCTMR', 'AVX1.0', 'RDRAND', 'F16C'],
            leafs=['RDWRFSGS', 'TSC_THREAD_OFFSET', 'BMI1', 'HLE', 'AVX2', 'SMEP', 'BMI2', 'ERMS', 'INVPCID', 'RTM', 'MPX', 'AVX512F', 'AVX512DQ', 'RDSEED', 'ADX', 'SMAP', 'CLFSOPT', 'CLWB', 'AVX512CD', 'AVX512BW', 'AVX512VL', 'UMIP', 'MDCLEAR', 'IBRS', 'STIBP', 'ACAPMSR', 'SSBD']
        ),
        oclp_version=None,
        opencore_version='REL-083-2022-08-01',
        opencore_path=None,
        bluetooth_chipset=None,
        ambient_light_sensor=False,
        third_party_sata_ssd=False,
        secure_boot_model='x86legacyap',
        secure_boot_policy=0,
        oclp_sys_version=None,
        oclp_sys_date=None,
        oclp_sys_url=None,
        firmware_vendor='EDK II',
        rosetta_active=False
    )