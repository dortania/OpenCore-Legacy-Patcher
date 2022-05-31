# Data for SkyLightShim Plugin systems
class shim_list:
    shim_pathing = {
        "CoreWLAN.dylib": "/System/Library/CoreServices/WiFiAgent.app/Contents/MacOS/WiFiAgent",
        "BacklightFixup.dylib": "/System/Library/CoreServices/loginwindow.app/Contents/MacOS/loginwindow",
    }

    shim_legacy_accel = [
        "CoreWLAN.dylib",
    ]

    shim_legacy_accel_keyboard = [
        "BacklightFixup.dylib",
    ]