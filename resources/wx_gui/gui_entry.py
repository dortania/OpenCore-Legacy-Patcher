import wx
import sys
import logging
import atexit

from resources import constants
from resources.wx_gui import (
    gui_main_menu,
    gui_build,
    gui_menubar,
    gui_install_oc
)

class SupportedEntryPoints:
    """
    Enum for supported entry points
    """
    MAIN_MENU  = gui_main_menu.MainMenu
    BUILD_OC   = gui_build.BuildFrame
    INSTALL_OC = gui_install_oc.InstallOCFrame

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
        self.frame: wx.Frame = entry(
            None,
            title=f"{self.constants.patcher_name} ({self.constants.patcher_version})",
            global_constants=self.constants,
            screen_location=None
        )
        self.frame.SetMenuBar(gui_menubar.GenerateMenubar().generate())
        atexit.register(self.OnCloseFrame)

        self.app.MainLoop()


    def OnCloseFrame(self, event=None):
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

        sys.exit()
