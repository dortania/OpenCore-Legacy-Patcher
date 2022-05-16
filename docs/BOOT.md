# Booting OpenCore and macOS

Now we finally get to boot OpenCore!

Reboot machine while holding `Option` to select the EFI Boot entry with the OpenCore icon (holding the `Control` key will make this the default boot entry):

* This will be the Mac Boot Picker

![](../images/efi-boot.png)

Now that you've loaded OpenCore, now select Install macOS:

* This will be the OpenCore Picker

![](../images/oc-boot.png)

You will soon reach the installer screen! If you enabled verbose mode when building OCLP, a lot of text will run across the screen. From there it's just like any normal macOS install. For an example of how the boot process looks, see the following video:

* [OpenCore Legacy Patcher Boot Process](https://www.youtube.com/watch?v=AN3zsbQV_n4)

If your Mac is looping back into the beginning of the setup after the first reboot, turn it off, start it again and hold `Option`. This time select the option with a grey hard disk icon, it can say "macOS Installer" or the name you gave the disk during the installer process. Keep repeating this step after every reboot if necessary.

![](../images/oclp-stuck-firstreboot.png)


::: warning 

**MacBookPro11,3 Note**: When booting macOS Monterey, you'll need to boot into safe mode if acceleration patches are not installed yet. [Otherwise you'll hit a black screen due to missing NVIDIA drivers.](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/522) Safe Mode can be entered by holding Shift+Enter when selecting macOS Monterey in OCLP's Boot Menu.

:::

# Once installed and booting, head to [Post-Installation](./POST-INSTALL.md)

