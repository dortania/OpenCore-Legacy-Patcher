/* Removes PCI0's 32-bit Allocation Limitation to resolve PCIe device support on Sandy and
 * Ivy Bridge Macs, mainly applicable for Audio and eGPU support.
 * BUF0 to BUF1 patch required to override existing BuffObj in DSDT.
 *
 * Source:
 * https://egpu.io/forums/pc-setup/fix-dsdt-override-to-correct-error-12/
 */
DefinitionBlock ("", "SSDT", 2, "DRTNIA", "WinPCI", 0x00000000)
{
    External (_SB_.PCI0, DeviceObj)

    Scope (\_SB.PCI0)
    {
        Store ("Injecting new BUF0 BuffObj", Debug)
        Name (BUF0, ResourceTemplate ()
        {
            WordBusNumber (ResourceProducer, MinFixed, MaxFixed, PosDecode,
                0x0000,             // Granularity
                0x0000,             // Range Minimum
                0x00FF,             // Range Maximum
                0x0000,             // Translation Offset
                0x0100,             // Length
                ,, )
            DWordIO (ResourceProducer, MinFixed, MaxFixed, PosDecode, EntireRange,
                0x00000000,         // Granularity
                0x00000000,         // Range Minimum
                0x00000CF7,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00000CF8,         // Length
                ,, , TypeStatic, DenseTranslation)
            IO (Decode16,
                0x0CF8,             // Range Minimum
                0x0CF8,             // Range Maximum
                0x01,               // Alignment
                0x08,               // Length
                )
            DWordIO (ResourceProducer, MinFixed, MaxFixed, PosDecode, EntireRange,
                0x00000000,         // Granularity
                0x00000D00,         // Range Minimum
                0x0000FFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x0000F300,         // Length
                ,, , TypeStatic, DenseTranslation)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000A0000,         // Range Minimum
                0x000BFFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00020000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000C0000,         // Range Minimum
                0x000C3FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000C4000,         // Range Minimum
                0x000C7FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000C8000,         // Range Minimum
                0x000CBFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000CC000,         // Range Minimum
                0x000CFFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000D0000,         // Range Minimum
                0x000D3FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000D4000,         // Range Minimum
                0x000D7FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000D8000,         // Range Minimum
                0x000DBFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000DC000,         // Range Minimum
                0x000DFFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000E0000,         // Range Minimum
                0x000E3FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000E4000,         // Range Minimum
                0x000E7FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000E8000,         // Range Minimum
                0x000EBFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000EC000,         // Range Minimum
                0x000EFFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00004000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x000F0000,         // Range Minimum
                0x000FFFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00010000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0x00000000,         // Range Minimum
                0xFEAFFFFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0xFEB00000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            DWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x00000000,         // Granularity
                0xFED40000,         // Range Minimum
                0xFED44FFF,         // Range Maximum
                0x00000000,         // Translation Offset
                0x00005000,         // Length
                ,, , AddressRangeMemory, TypeStatic)
            QWordMemory (ResourceProducer, PosDecode, MinFixed, MaxFixed, Cacheable, ReadWrite,
                0x0000000000000000, // Granularity
                0x0000000C20000000, // Range Minimum,  set it to 48.5GB
                0x0000000E0FFFFFFF, // Range Maximum,  set it to 56.25GB
                0x0000000000000000, // Translation Offset
                0x00000001F0000000, // Length calculated by Range Max - Range Min.
                ,, , AddressRangeMemory, TypeStatic)
        })
    }
}