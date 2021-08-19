# Booting OpenCore and macOS

Now we finally get to boot OpenCore!

Reboot machine while holding `Option` to select the EFI Boot entry with the OpenCore icon (holding the `Control` key will make this the default boot entry):

* This will be the Mac Boot Picker

![](../images/efi-boot.png)

Now that you've loaded OpenCore, now select Install macOS!:

* This will be the OpenCore Picker

![](../images/oc-boot.png)

After plenty of verbose booting, you will reach the installer screen! From there it's just like any normal macOS install. For an example of how the boot process looks, see the following video:

* [OpenCore Legacy Patcher Boot Process](https://www.youtube.com/watch?v=AN3zsbQV_n4)
*NOTE: As macOS installation progresses, serveral restarts are going occure which is part of the process. On each occurance, you must be ready to hold down the key "option/alt" in order to make it back to the same menu from which you had initially picked "EFI". You then pick (unlike previously) the HD icon which will represent the target storage device, onto macOS will continue installing. This will happen at least one more time. It is advised, therefore, to NOT leave the machine unattended, as you can expect the restart state - during which, the aformentioned interaction with the booting process is essential.
# Once installed and booting, head to [Post-Installation](./POST-INSTALL.md)
