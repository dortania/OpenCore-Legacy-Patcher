# Boot Process with OpenCore Legacy Patcher

OpenCore Legacy Patcher itself is actually quite a "dumb" program, and essentially edits a config.plist file and moves files around, it actually has little logic regarding the boot process.  The real magic of OCLP is [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg), our back-end and what makes this patcher so powerful.

## Boot Process with OpenCore

To understand a bit more of how OpenCore is able revive older Macs in such a native-like way, we need to go over *how* OpenCore works with your Mac:

![](../images/oc-explained.png)
