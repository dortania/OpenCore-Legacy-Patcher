/* Disable the non-existant Co-processor Bridge found on Arrendale, Lynnfield and Clarkdale Macs.
 * IOPCIFamily in macOS 11.0 up-to 11.2 was unable to handle ACPI probing when device was not present,
 * therefore kernel panicing the machine.
 *
 * This SSDT reports the device as disabled avoiding the probing.
 * Not required for macOS 11.2 and newer, however recommended to alliviate pottential issues
 */
DefinitionBlock ("", "SSDT", 2, "DRTNIA", "CPBGoff", 0x00001000)
{
    External (_SB_.CPBG, DeviceObj)

    Scope (_SB.CPBG)
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Store ("Disabling incompatible CPBG Device", Debug)
                Return (Zero) // Disable only in macOS incase Windows or Linux requires
            }
            Else
            {
                Return (0x0F)
            }
        }
    }
}