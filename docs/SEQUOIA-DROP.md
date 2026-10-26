# macOS Sequoia

![](./images/macos-sequoia.png)

Another year, another release.

This time Apple dropped surprisingly few amount of Macs. With the release of OpenCore Legacy Patcher 2.0.0, early support for macOS Sequoia has been implemented.


## Newly dropped hardware

* MacBookAir8,1 :       MacBook Air (2018)
* MacBookAir8,2 :       MacBook Air (2019)

## Current status

OpenCore Legacy Patcher 2.0.0 supports Sequoia for the models below, however some challenges remain. You can find information about them further down this page.

<img width="625" alt="" src="./images/OCLP-200-Initial-Support.png">

Unfortunately due to T2 related problems, the recently dropped MacBookAir8,x models cannot be supported at this time. We have made some progress on this issue, but panics are still occurring and there is still a significant amount of development work to do before T2 machines may even get to the install screen. We cannot provide any estimate on when T2 machines will be supported. 

[More information here.](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1136)

## Non-functional features

On majority of patched Macs, iPhone Mirroring and Apple Intelligence won't be functional.

iPhone Mirroring requires T2 for attestation and Apple Intelligence requires an NPU only found in Apple Silicon, the patcher is unable to provide a fix for these as they're hardware requirements.

## Issues

[See ongoing issues.](https://dortania.github.io/OpenCore-Legacy-Patcher/ONGOING-ISSUES.html)