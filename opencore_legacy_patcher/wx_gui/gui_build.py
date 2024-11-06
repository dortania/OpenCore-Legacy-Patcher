"""
gui_build.py: Generate UI for Building OpenCore
"""

import wx
import logging
import threading
import traceback

from .. import constants

from ..efi_builder import build

from ..wx_gui import (
    gui_main_menu,
    gui_install_oc,
    gui_support
)


class BuildFrame(wx.Frame):
    """
    Create a frame for building OpenCore
    Uses a Modal Dialog for smoother transition from other frames
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None) -> None:
        logging.info("Initializing Build Frame")
        super(BuildFrame, self).__init__(parent, title=title, size=(350, 200), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        gui_support.GenerateMenubar(self, global_constants).generate()

        self.build_successful: bool = False

        self.install_button: wx.Button = None
        self.text_box:     wx.TextCtrl = None
        self.frame_modal:    wx.Dialog = None

        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.stock_output = logging.getLogger().handlers[0].stream

        self.frame_modal = wx.Dialog(self, title=title, size=(400, 200))

        self._generate_elements(self.frame_modal)

        if self.constants.update_stage != gui_support.AutoUpdateStages.INACTIVE:
            self.constants.update_stage = gui_support.AutoUpdateStages.BUILDING

        self.Centre()
        self.frame_modal.ShowWindowModal()

        self._invoke_build()


    def _generate_elements(self, frame: wx.Frame = None) -> None:
        """
        Generate UI elements for build frame

        Format:
            - Title label:        Build and Install OpenCore
            - Text:               Model: {Build or Host Model}
            - Button:             Install OpenCore
            - Read-only text box: {empty}
            - Button:             Return to Main Menu
        """
        frame = self if not frame else frame

        title_label = wx.StaticText(frame, label="Build and Install OpenCore", pos=(-1,5))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        model_label = wx.StaticText(frame, label=f"Model: {self.constants.custom_model or self.constants.computer.real_model}", pos=(-1,30))
        model_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        model_label.Centre(wx.HORIZONTAL)

        # Button: Install OpenCore
        install_button = wx.Button(frame, label="🔩 Install OpenCore", pos=(-1, model_label.GetPosition()[1] + model_label.GetSize()[1]), size=(150, 30))
        install_button.Bind(wx.EVT_BUTTON, self.on_install)
        install_button.Centre(wx.HORIZONTAL)
        install_button.Disable()
        self.install_button = install_button

        # Read-only text box: {empty}
        text_box = wx.TextCtrl(frame, value="", pos=(-1, install_button.GetPosition()[1] + install_button.GetSize()[1] + 10), size=(380, 350), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        text_box.Centre(wx.HORIZONTAL)
        self.text_box = text_box

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(-1, text_box.GetPosition()[1] + text_box.GetSize()[1] + 5), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.Centre(wx.HORIZONTAL)
        return_button.Disable()
        self.return_button = return_button

        # Adjust window size to fit all elements
        frame.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))


    def _invoke_build(self) -> None:
        """
        Invokes build function and waits for it to finish
        """
        while gui_support.PayloadMount(self.constants, self).is_unpack_finished() is False:
            wx.Yield()

        thread = threading.Thread(target=self._build)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        self.return_button.Enable()

        # Check if config.plist was built
        if self.build_successful is False:
            dialog = wx.MessageDialog(
                parent=self,
                message="An error occurred while building OpenCore",
                caption="Error building OpenCore",
                style=wx.OK | wx.ICON_ERROR
            )
            dialog.ShowModal()
            return

        dialog = wx.MessageDialog(
            parent=self,
            message=f"Would you like to install OpenCore now?",
            caption="Finished building your OpenCore configuration!",
            style=wx.YES_NO | wx.ICON_QUESTION
        )
        dialog.SetYesNoLabels("Install to disk", "View build log")

        self.on_install() if dialog.ShowModal() == wx.ID_YES else self.install_button.Enable()


    def _build(self) -> None:
        """
        Calls build function and redirects stdout to the text box
        """
        logger = logging.getLogger()
        logger.addHandler(gui_support.ThreadHandler(self.text_box))
        try:
            build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants)
            self.build_successful = True
        except Exception as e:
            logging.error("An internal error occurred while building:\n")
            logging.error(traceback.format_exc())

            # Handle bug from 2.1.0 where None type was stored in config.plist from global settings
            if "TypeError: unsupported type: <class 'NoneType'>" in traceback.format_exc():
                logging.error("If you continue to see this error, delete the following file and restart the application:")
                logging.error("Path: /Users/Shared/.com.dortania.opencore-legacy-patcher.plist")

        logger.removeHandler(logger.handlers[2])


    def on_return_to_main_menu(self, event: wx.Event = None) -> None:
        """
        Return to main menu
        """
        self.frame_modal.Hide()
        main_menu_frame = gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        self.frame_modal.Destroy()
        self.Destroy()


    def on_install(self, event: wx.Event = None) -> None:
        """
        Launch install frame
        """
        self.frame_modal.Destroy()
        self.Destroy()
        install_oc_frame = gui_install_oc.InstallOCFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        install_oc_frame.Show()


