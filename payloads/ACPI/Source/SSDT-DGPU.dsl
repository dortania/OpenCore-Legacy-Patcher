/* Requests power off of dGPU in MacBookPro8,2/3 (TS2 hardware failure)
 * Main goal is to ensure power draw from the dGPU is reduced as
 * much as possible to simulate a hardware demux without actual
 * hardware modifications.
 *
 * Notes:
 *       - SSDT must be used in conjunction with '_INI' to 'XINI' patch
 *         to reroute PCI0 initialization.
 *
 *       - AMD drivers in macOS may still attempt to attach and kernel
 *         panic. Disable the dGPU with class-code/device-id spoof or
 *         with '-wegnoegpu'.
 *
 *       - dGPU will reactivate with sleep-wake, additional process
 *         is needed to disable the dGPU.
 *         - ie. AMDGPUWakeHandler.kext for macOS
 *
 * Ref:
 *       - https://www.tonymacx86.com/threads/help-macbook-pro-disable-radeon-gpu-via-dsdt.164458/
 *       - https://github.com/blackgate/AMDGPUWakeHandler
 *       - https://help.ubuntu.com/community/MacBookPro8-2/Raring
 */
DefinitionBlock ("", "SSDT", 2, "DRTNIA", "dGPU_OFF", 0x00001000)
{
    External (_SB_.PCI0, DeviceObj)
    External (OSYS)

    Scope (_SB.PCI0)
    {
        OperationRegion (IOGP, SystemIO, 0x0700, 0x51)
        Field (IOGP, ByteAcc, NoLock, Preserve)
        {
            Offset (0x10),
            P710,   8,
            Offset (0x28),
            P728,   8,
            Offset (0x40),
            P740,   8,
            Offset (0x50),
            P750,   8
        }

        Method (_INI, 0, NotSerialized)  // _INI: Initialize
        {
            Store (0x07D0, OSYS)
            If (CondRefOf (\_OSI, Local0))
            {
                If (_OSI ("Darwin"))
                {
                    Store (0x2710, OSYS)
                }

                If (\_OSI ("Linux"))
                {
                    Store (0x03E8, OSYS)
                }

                If (\_OSI ("Windows 2001"))
                {
                    Store (0x07D1, OSYS)
                }

                If (\_OSI ("Windows 2001 SP1"))
                {
                    Store (0x07D1, OSYS)
                }

                If (\_OSI ("Windows 2001 SP2"))
                {
                    Store (0x07D2, OSYS)
                }

                If (\_OSI ("Windows 2006"))
                {
                    Store (0x07D6, OSYS)
                }

                If (\_OSI ("Windows 2007"))
                {
                    Store (0x07D7, OSYS)
                }

                If (\_OSI ("Windows 2008"))
                {
                    Store (0x07D8, OSYS)
                }

                If (\_OSI ("Windows 2009"))
                {
                    Store (0x07D9, OSYS)
                }
            }

            // Disables dGPU
            Store ("Requesting dGPU power off", Debug)
            P728 = One  // Switch select
            P710 = 0x02 // Switch display
            P740 = 0x02 // Switch DDC
            P750 = Zero // Power down discrete graphics
        }
    }
}

