# Working Around Legacy Acceleration Issues

* [Downloading older non-Metal Apps](#downloading-older-non-metal-apps)
* [Unable to run Zoom](#unable-to-run-zoom)
* [Unable to grant special permissions to apps (ie. Camera Access to Zoom)](#unable-to-grant-special-permissions-to-apps-ie-camera-access-to-zoom)
* [Keyboard Backlight broken](#keyboard-backlight-broken)
* [Photos and Maps Apps Heavily Distorted](#photos-and-maps-apps-heavily-distorted)
* [Cannot press "Done" when editing a Sidebar Widget](#cannot-press-done-when-editing-a-sidebar-widget)
* [Wake from sleep heavily distorted on AMD/ATI in macOS 11.3 and newer](#wake-from-sleep-heavily-distorted-on-amd-ati-in-macos-11-3-and-newer)
* [Unable to switch GPUs on 2011 15" and 17" MacBook Pros](#unable-to-switch-gpus-on-2011-15-and-17-macbook-pros)
* [Erratic Colours on ATI TeraScale 2 GPUs (HD5000/HD6000)](#erratic-colours-on-ati-terascale-2-gpus-hd5000-hd6000)

The below page is for users experiencing issues with their overall usage of macOS Big Sur and the Legacy Graphics Acceleration patches. Note that the following GPUs currently do not have acceleration support in Big Sur:

* Intel 3rd and 4th Gen - GMA series

For those unfamiliar with what is considered a non-Metal GPU, see below chart:

::: details macOS GPU Chart

| Graphics Vendor | Architecture | Series | Supports Metal |
| :--- | :--- | :--- | :--- |
| ATI | TeraScale 1 | HD2000 - HD4000 | <span style="color:red">No</span> |
| ^^ | TeraScale 2 | HD5000 - HD6000 | ^^ |
| AMD | GCN (and newer) | HD7000+ | <span style="color:green">Yes</span> |
| Nvidia | Tesla | 8000GT - GT300 |  <span style="color:red">No</span> |
| ^^ | Fermi | GT400 - GT500 | ^^ | 
| ^^ | Kepler | GT600 - GT700 | <span style="color:green">Yes</span> |
| Intel | GMA | GMA900 - GMA3000 | <span style="color:red">No</span> |
| ^^ | Iron Lake | HD series | ^^ |
| ^^ | Sandy Bridge | HD3000 | ^^ |
| ^^ | Ivy Bridge (and newer) | HD4000 | <span style="color:green">Yes</span> |

:::

Additionally we currently do not have macOS Monterey acceleration patches for non-Metal Macs. We recommend users either upgrade their Macs with a Metal GPU or remain on Big Sur until further development

::: details Why there's no non-Metal patches for Monterey

With macOS Monterey, please understand our current legacy acceleration patch sets are no longer functional. As of right now, only basic framebuffer and brightness control may be achieved, however proper animations and hardware acceleration is not available.

This is due to numerous changes with Skylight and other macOS frameworks relying more and more on Metal functions and thus making it even more difficult to re-add legacy OpenGL support.

> When can we expect acceleration support

For the time being, please understand we cannot predict when there will be patch sets ready. Note that it took over 300 days from Big Sur's unveiling to achieve public acceleration for non-Metal GPUs. And with TeraScale 2 acceleration, this took almost 3 years to achieve public acceleration.

So please be patient as developers are hard at work, however please expect no acceleration support in Monterey until next year at the minimum if not even later.

:::

## Downloading older non-Metal Apps

Many Apple apps now have direct reliance on Metal for proper functioning, however legacy builds of these apps still do work in Big Sur. See below for archive of many apps such as Pages, iMovie, GarageBand.

* [Apple Apps for Non-Metal Macs](https://archive.org/details/apple-apps-for-non-metal-macs)

Note: This archive assumes that you own these copies of these apps through the Mac App Store, Dortania does not condone piracy

## Unable to run Zoom

Currently Zoom relies partially on Metal and so needs a small binary patch. Dosdude1 has provided a nice script for this:

* [Zoom Non-Metal Fix](http://dosdude1.com/catalina/zoomnonmetal-new.command.zip)

## Unable to grant special permissions to apps (ie. Camera Access to Zoom)

With version 0.2.5, this issue should be full resolved

::: details 0.2.4 and older Work-Around

Due to the usage of `amfi_get_out_of_my_way=1`, macOS will fail to prompt users for special permissions upon application start as well as omit the entires in System Preferences. To work around this, we recommend users install [tccplus](https://github.com/jslegendre/tccplus) to manage permissions.

Example usage with Discord and microphone permissions:

```sh
# Open Terminal and run the following commands
cd ~/Downloads/
chmod +x tccplus
./tccplus add Microphone com.hnc.Discord
```

For those who may experience issues with `tccplus`, you can manually patch `com.apple.TCC` to add permissions:

```sh
# get app id (Zoom.us used in example):
$ osascript -e 'id of app "zoom.us"'
# output: us.zoom.xos

$ sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "INSERT or REPLACE INTO access VALUES('kTCCServiceMicrophone','us.zoom.xos',0,2,0,1,NULL,NULL,NULL,'UNUSED',NULL,0,1541440109);"

$ sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "INSERT or REPLACE INTO access VALUES('kTCCServiceCamera','us.zoom.xos',0,2,0,1,NULL,NULL,NULL,'UNUSED',NULL,0,1541440109);"
```

:::

## Keyboard Backlight broken

Due to forcing `hidd` into spinning up with the fallback mode enabled, this can break the OS's recognition of backlight keyboards. Thankfully the drivers themselves still do operate so applications such as [LabTick](https://www.macupdate.com/app/mac/22151/lab-tick) are able to set the brightness manually.

## Photos and Maps Apps Heavily Distorted

Due to the Metal Backend, the enhanced color output of these apps seems to heavily break overall UI usage. To work around this, [users reported](https://forums.macrumors.com/threads/macos-11-big-sur-on-unsupported-macs-thread.2242172/post-29870324) forcing the color output of their monitor from Billions to Millions of colors helped greatly. Apps easily allowing this customization are [SwitchResX](https://www.madrau.com), [ResXreme](https://macdownload.informer.com/resxtreme/) and [EasyRes](http://easyresapp.com).

## Cannot press "Done" when editing a Sidebar Widget

To work around this, simply press Tab to hover over and press spacebar to simulate a click.

## Wake from sleep heavily distorted on AMD/ATI in macOS 11.3 and newer

Unfortunately a very well known issue the community is investigating, current known solution is to simply downgrade to 11.2.3 or older until a proper fix can be found. Additionally logging out and logging in can resolve the issue without requiring a reboot

* Note, this issue should be exclusive to TeraScale 1 GPUs (ie. HD2000-4000). TeraScale 2 GPUs should not exhibit this issue

In the event Apple removes 11.2.3 from their catalogue, we've provided a mirror below:

* [Install macOS 11.2.3 20D91](https://archive.org/details/install-mac-os-11.2.3-20-d-91)

## Unable to switch GPUs on 2011 15" and 17" MacBook Pros

Currently OpenCore Legacy Patcher, GPU switching between the iGPU and dGPU is broken. The simplest way to set a specific GPU is to disable the dGPU when you wish to remain on the more power efficient iGPU.

The best way to achieve this is to boot Recovery (or Single User Mode if the dGPU refuses to function at all) and run the following command:

```sh
nvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs=%01%00%00%00
```

This will disable the dGPU and allow the iGPU to function in Big Sur. Note that external display outputs are directly routed to the dGPU and therefore can no longer be used. Solutions such as a [DisplayLink Adapters](https://www.displaylink.com/products/usb-adapters) can work around this limitation in theory. However, currently the proprietary DisplayLink driver refuses to function on legacy-patched systems, either resulting in a windowserver crash loop or no output at all. 

## Erratic Colours on ATI TeraScale 2 GPUs (HD5000/HD6000)

Due to an odd bug with ATI's TeraScale 2 GPUs, many users will experience erratic/strobing colours once finished installing and rebooting into the accelerated patches. The issue stems from an incorrect assumption in the GPU drivers where it will enforce the Billion Colour space on your display. To fix, simply force your Display into a lower color depth such as a Million Colours.

Applications that can set color depth are:

* [SwitchResX](https://www.madrau.com)
* [ResXtreme](https://macdownload.informer.com/resxtreme/)