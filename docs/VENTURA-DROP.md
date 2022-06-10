![](../images/macos-ventura.png)

Apple's nineteenth major release of their XNU-based operating system continues the march towards Apple Silicon only support. As predicted by the non-metal team, the graphics stack was overhauled again and we saw the loss of many Macs with the introduction of this version.

**Please note that for now, and the foreseeable future, macOS Ventura is not supported by OpenCore Legacy Patcher.** There are no ETAs on when it will be supported, and no support will be provided for this OS if you choose to work on your own.

## Newly dropped hardware

* iMac16,1
* iMac16,2
* iMac17,1
* MacBook9,1
* MacBookAir7,1
* MacBookAir7,2
* MacBookPro11,4
* MacBookPro11,5
* MacBookPro12,1
* MacBookPro13,1
* MacBookPro13,2
* MacBookPro13,3
* Macmini7,1
* MacPro6,1 

::: details Model names

* iMac (21.5-inch, Late 2015)
* iMac (Retina 4K, 21.5-inch, Late 2015) 
* iMac (Retina 5K, 27-inch, Late 2015)
* MacBook (Retina, 12-inch, Early 2016)
* MacBook Air (11-inch, Early 2015)
* MacBook Air (13-inch, Early 2015)
* MacBook Air (13-inch, 2017)
* MacBook Pro (Retina, 13-inch, Early 2015)
* MacBook Pro (Retina, 15-inch, Mid 2015)
* MacBook Pro (13-inch, 2016, Two Thunderbolt 3 ports)
* MacBook Pro (13-inch, 2016, Four Thunderbolt 3 ports)
* MacBook Pro (15-inch, 2016)
* Mac mini (Late 2014)
* Mac Pro (Late 2013)

::: 

## Broken hardware

### CPU

With macOS Ventura, Apple removed the non-AVX2 dynamic library cache (or dyld) from the Preboot volume. Due to this, any Mac with an Ivy Bridge or older CPU will not be able to boot macOS Ventura without modifications to the Preboot volume. 

* MacBookPro10,x and older
* MacPro6,1 and older
* MacBook7,1 and older
* MacBookAir5,x and older
* Macmini6,x and older
* iMac13,x and older
* Xserve3,1 and older

::: warning

Although some of the above systems can be patched to boot Ventura, a scan of Ventura's executables show a major increase in AVX-based instruction sets being used by the system. Therefore, these systems are extremely unstable when running it.

:::

### GPU

Apple also removed all unsupported GPU drivers from macOS. Due to this, most, if not all, unsupported Macs will require root patches when available in the future.


* Haswell, Broadwell, and Skylake iGPUs
  * HD 4200-6000
  * Iris 540-550
  * Iris Pro 5100-6200
  * HD 515-530
* AMD Graphics Core Next 1-3
  * HD 7xxx-8xxx
  * Any FirePro GPU
  * Any R9 GPU

::: details Legacy Acceleration Patches

Like with every new macOS update, the non-metal acceleration patches have been broken again. Since Ventura includes a major graphics rewrite with Metal 3 (which also affects the GPUs above), we are unsure as to how long it will take to get them running again, if at all:

  * Intel Ironlake and Sandy Bridge iGPUs
  * NVIDIA Tesla and Fermi GPUs
  * AMD TeraScale 1 and 2 GPUs

As usual, this affects the following systems:

* iMac12,x and older
* Macmini5,x and older
* MacBook7,1 and older
* MacBookAir4,x and older
* MacBookPro8,x and older

:::

### Peripherals

Additionally, trackpad drivers were removed for pre-Force Touch models, rendering older trackpads only able to use primary clicks and single finger swipes as it is seen by macOS as a mouse. Keyboard drivers were also removed, rendering multimedia keys and keyboard backlights non-functional:

* MacBookPro11,1-11,3 and older
* MacBookAir7,x and older
* MacBook7,1 and older

