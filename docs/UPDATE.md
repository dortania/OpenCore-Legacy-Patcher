# Updating OpenCore and Patches

This guide explains how to get fully up to date application, bootloader and patches.

## Updating the application

Latest versions of OCLP can download updates by themselves, you will get notified of a new update with the changelog.

[You can also manually download the latest release here.](https://github.com/dortania/OpenCore-Legacy-Patcher/releases)

![Update available](./images/OCLP_Update_Available.png)



## Updating patches

After the update, the application asks if you want to update OpenCore and root patches.
    
   * Note: OCLP will always build with developer set default settings. If you use settings that deviate from OCLP defaults, select "no" from here and then do your settings. 
   
![Update successful](./images/OCLP_Update_Successful.png) | 

If you selected "no", you will have to manually build and install OpenCore to update to the latest version of the bootloader, then install new root patches to ensure you're running on the latest fixes.


## Checking OCLP and OpenCore versions

To check what version of OpenCore bootloader and the Patcher you're currently running, you can run the following in the terminal:

```bash
# OpenCore Version
nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:opencore-version
# Patcher Version
nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:OCLP-Version
```

<div align="center">
             <img src="./images/oclp-version.png" alt="OCLP version" width="600" />
</div>

From this, we can see that we're running a RELEASE version of OpenCore 0.8.0 built on April 18th, 2022 with Patcher Version 0.4.5!
