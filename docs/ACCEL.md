# Working Around Legacy Acceleration Issues

* [Downloading older non-Metal Apps](#downloading-older-non-metal-apps)
* [Unable to run Zoom](#unable-to-run-zoom)
* [Unable to grant special permissions to apps (ie. Camera Access to Zoom)](#unable-to-grant-special-permissions-to-apps-ie-camera-access-to-zoom)
* [Keyboard Backlight broken](#keyboard-backlight-broken)
* [Photos and Maps Apps Heavily Distorted](#photos-and-maps-apps-heavily-distorted)
* [Cannot press "Done" when editing a Sidebar Widget](#cannot-press-done-when-editing-a-sidebar-widget)
* [Wake from sleep heavily distorted on AMD/ATI in macOS 11.3 and newer](#wake-from-sleep-heavily-distorted-on-amd-ati-in-macos-11-3-and-newer)
* [Achieving GPU Acceleration on 2011 15" and 17" MacBook Pros](#achieving-gpu-acceleration-on-2011-15-and-17-macbook-pros)

The below page is for users experiencing issues with their overall usage of macOS Big Sur and the Legacy Graphics Acceleration patches. Note that the following GPUs currently do not have acceleration support in Big Sur:

* Intel 3rd and 4th Gen - GMA series

## Downloading older non-Metal Apps

Many Apple apps now have direct reliance on Metal for proper functioning, however legacy builds of these apps still do work in Big Sur. See below for archive of many apps such as Pages, iMovie, GarageBand.

* [Apple Apps for Non-Metal Macs](https://archive.org/details/apple-apps-for-non-metal-macs)

Note: This archive assumes that you own these copies of these apps through the Mac App Store, Dortania does not condone piracy

## Unable to run Zoom

Currently Zoom relies partially on Metal and so needs a small binary patch. Dosdude1 has provided a nice script for this:

* [Zoom Non-Metal Fix](http://dosdude1.com/catalina/zoomnonmetal-new.command.zip)

## Unable to grant special permissions to apps (ie. Camera Access to Zoom)

Due to the usage of `amfi_get_out_of_my_way=1`, macOS will fail to prompt users for special permissions upon application start as well as omit the entires in System Preferences. To work around this, we recommend users install [tccplus](https://github.com/jslegendre/tccplus) to manage permissions.

Example usage with Discord and microphone permissions:

```sh
# Open Terminal and run the following commands
cd ~/Downloads/
chmod +x tccplus
./tccplus add Microphone com.hnc.Discord
```

## Keyboard Backlight broken

Due to forcing `hidd` into spinning up with the fallback mode enabled, this can break the OS's recognition of backlight keyboards. Thankfully the drivers themselves still do operate so applications such as [LabTick](https://www.macupdate.com/app/mac/22151/lab-tick) are able to set the brightness manually.

## Photos and Maps Apps Heavily Distorted

Due to the Metal Backend, the enhanced color output of these apps seems to heavily break overall UI usage. To work around this, [users reported](https://forums.macrumors.com/threads/macos-11-big-sur-on-unsupported-macs-thread.2242172/post-29870324) forcing the color output of their monitor from Billions to Millions of colors helped greatly. Apps easily allowing this customization are [SwitchResX](https://www.madrau.com), [ResXreme](https://macdownload.informer.com/resxtreme/) and [EasyRes](http://easyresapp.com).

## Cannot press "Done" when editing a Sidebar Widget

To work around this, simply press Tab to hover over and press spacebar to simulate a click.

## Wake from sleep heavily distorted on AMD/ATI in macOS 11.3 and newer

Unfortunately a very well known issue the community is investigating, current known solution is to simply downgrade to 11.2.3 or older until a proper fix can be found.

In the event Apple removes 11.2.3 from their catalogue, we've provided a mirror below:

* [Install macOS 11.2.3 20D91](https://archive.org/details/install-mac-os-11.2.3-20-d-91)

## Achieving GPU Acceleration on 2011 15" and 17" MacBook Pros

Currently, OpenCore Legacy Patcher has support for GPUs based on the AMD/ATI TeraScale 2 architecture. This includes the AMD/ATI HD 5000 and HD 6000 desktop graphics cards found in many Macs. To enable the functionality of these, a setting in the "5. Patcher Settings" menu for enabling TeraScale 2 graphics acceleration needs to be set to yes. However, the reason this is not enabled by default is because some systems with TeraScale 2 GPUs may experience strobing of the image/colours on screen. This can result in seizures to users sensitive to these flashing effects, so proceed at your own risk. On MacBook Pro 2011 15" and 17" however, there are fortunately no strobing effects. With the setting enabled, the "3. Post-Install Volume Patch" menu will now allow you to install the TeraScale 2 patches.

Due to the widespread TeraScale 2 GPU failures on MacBook 2011 15" and 17", a command can be run that temporarily disables them and switches over to the integrated Intel HD 3000 graphics. To run the command, boot into Recovery (or Single User Mode if the dGPU is experiencing issues like green lines or image corruption) and run the following line in the Terminal:

```sh
nvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs=%01%00%00%00
```

This will disable the dGPU and the graphics processing will occur on the Intel HD 3000 integrated graphics processor instead. Note that external display outputs are directly routed to the dGPU and therefore can not be used while it's disabled. Solutions such as a [DisplayLink Adapter](https://www.displaylink.com/products/usb-adapters) can work around this limitation.
