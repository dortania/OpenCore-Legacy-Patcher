import wx
import sys
import logging
import atexit

from resources import constants
from resources.wx_gui import (
    gui_main_menu,
    gui_build,
    gui_install_oc,
    gui_sys_patch,
    gui_support,
    gui_update,
)
from resources.sys_patch import sys_patch_detect

class SupportedEntryPoints:
    """
    Enum for supported entry points
    """
    MAIN_MENU  = gui_main_menu.MainMenu
    BUILD_OC   = gui_build.BuildFrame
    INSTALL_OC = gui_install_oc.InstallOCFrame
    SYS_PATCH  = gui_sys_patch.SysPatchMenu
    UPDATE_APP = gui_update.UpdateFrame

class EntryPoint:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.app: wx.App = None
        self.main_menu_frame: gui_main_menu.MainMenu = None
        self.constants: constants.Constants = global_constants

        self.constants.gui_mode = True


    def _generate_base_data(self) -> None:
        self.app = wx.App()


    def start(self, entry: SupportedEntryPoints = gui_main_menu.MainMenu) -> None:
        """
        Launches entry point for the wxPython GUI
        """
        self._generate_base_data()

        if "--gui_patch" in sys.argv or "--gui_unpatch" in sys.argv:
            entry = gui_sys_patch.SysPatchMenu
            patches = sys_patch_detect.DetectRootPatch(self.constants.computer.real_model, self.constants).detect_patch_set()

        self.frame: wx.Frame = entry(
            None,
            title=f"{self.constants.patcher_name} ({self.constants.patcher_version})",
            global_constants=self.constants,
            screen_location=None,
            **({"patches": patches} if "--gui_patch" in sys.argv or "--gui_unpatch" in sys.argv else {})
        )
        if self.frame:
            self.frame.SetMenuBar(gui_support.GenerateMenubar().generate())
        atexit.register(self.OnCloseFrame)

        if "--gui_patch" in sys.argv:
            self.frame.start_root_patching(patches)
        elif "--gui_unpatch" in sys.argv:
            self.frame.revert_root_patching(patches)

        self.app.MainLoop()


    def OnCloseFrame(self, event: wx.Event = None):
        """
        Closes the wxPython GUI
        """

        if not self.frame:
            return

        logging.info("- Cleaning up wxPython GUI")

        self.frame.SetTransparent(0)
        wx.GetApp().Yield()

        self.frame.DestroyChildren()
        self.frame.Destroy()
        self.app.ExitMainLoop()
