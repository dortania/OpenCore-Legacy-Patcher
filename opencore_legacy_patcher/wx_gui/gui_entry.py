"""
gui_entry.py: Entry point for the wxPython GUI
"""

import wx
import sys
import atexit
import logging

from Cocoa import NSApp, NSApplication


from .. import constants

from ..sys_patch.patchsets import HardwarePatchsetDetection

from ..wx_gui import (
    gui_cache_os_update,
    gui_main_menu,
    gui_build,
    gui_install_oc,
    gui_sys_patch_start,
    gui_update,
)


class SupportedEntryPoints:
    """
    Enum for supported entry points
    """
    MAIN_MENU  = gui_main_menu.MainFrame
    BUILD_OC   = gui_build.BuildFrame
    INSTALL_OC = gui_install_oc.InstallOCFrame
    SYS_PATCH  = gui_sys_patch_start.SysPatchStartFrame
    UPDATE_APP = gui_update.UpdateFrame
    OS_CACHE   = gui_cache_os_update.OSUpdateFrame


class EntryPoint:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.app: wx.App = None
        self.main_menu_frame: gui_main_menu.MainFrame = None
        self.constants: constants.Constants = global_constants

        self.constants.gui_mode = True


    def _generate_base_data(self) -> None:
        self.app = wx.App()
        self.app.SetAppName(self.constants.patcher_name)

        # Reference:
        # - https://discuss.wxpython.org/t/macos-window-opens-in-the-background-and-does-not-receive-focus/36763/10
        NSApplication.sharedApplication()
        NSApp().activateIgnoringOtherApps_(True)


    def start(self, entry: SupportedEntryPoints = gui_main_menu.MainFrame, start_patching: bool = False) -> None:
        """
        Launches entry point for the wxPython GUI
        """
        self._generate_base_data()

        if "--gui_patch" in sys.argv or "--gui_unpatch" in sys.argv or start_patching is True :
            entry = gui_sys_patch_start.SysPatchStartFrame
            patches = HardwarePatchsetDetection(constants=self.constants).device_properties

        logging.info(f"Entry point set: {entry.__name__}")

        # Normally set by main.py, but transitions from CLI mode may not have this set
        self.constants.gui_mode = True

        self.frame: wx.Frame = entry(
            None,
            title=f"{self.constants.patcher_name} {self.constants.patcher_version}{' (Nightly)' if not self.constants.commit_info[0].startswith('refs/tags') else ''}",
            global_constants=self.constants,
            screen_location=None,
            **({"patches": patches} if "--gui_patch" in sys.argv or "--gui_unpatch" in sys.argv or start_patching is True else {})
        )

        atexit.register(self.OnCloseFrame)

        if "--gui_patch" in sys.argv or start_patching is True:
            self.frame.start_root_patching()
        elif "--gui_unpatch" in sys.argv:
            self.frame.revert_root_patching()

        self.app.MainLoop()


    def OnCloseFrame(self, event: wx.Event = None) -> None:
        """
        Closes the wxPython GUI
        """

        if not self.frame:
            return

        logging.info("Cleaning up wxPython GUI")

        self.frame.SetTransparent(0)
        wx.Yield()

        self.frame.DestroyChildren()
        self.frame.Destroy()
        self.app.ExitMainLoop()
