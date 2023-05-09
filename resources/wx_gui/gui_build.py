import wx
import logging
import threading
import traceback

from resources.wx_gui import gui_main_menu, gui_install_oc, gui_support
from resources.build import build
from resources import constants


class BuildFrame(wx.Frame):
    """
    Create a frame for building OpenCore
    Uses a Modal Dialog for smoother transition from other frames
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        super(BuildFrame, self).__init__(parent, title=title, size=(350, 200), style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.install_button: wx.Button = None
        self.text_box:     wx.TextCtrl = None
        self.frame_modal:    wx.Dialog = None

        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.stock_output = logging.getLogger().handlers[0].stream

        self.frame_modal = wx.Dialog(self, title=title, size=(400, 200))

        self._generate_elements(self.frame_modal)

        self.SetPosition(screen_location) if screen_location else self.Centre()
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
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Center(wx.HORIZONTAL)

        model_label = wx.StaticText(frame, label=f"Model: {self.constants.custom_model or self.constants.computer.real_model}", pos=(-1,30))
        model_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        model_label.Center(wx.HORIZONTAL)

        # Button: Install OpenCore
        install_button = wx.Button(frame, label="🔩 Install OpenCore", pos=(-1, model_label.GetPosition()[1] + model_label.GetSize()[1]), size=(150, 30))
        install_button.Bind(wx.EVT_BUTTON, self.on_install)
        install_button.Center(wx.HORIZONTAL)
        install_button.Disable()
        self.install_button = install_button

        # Read-only text box: {empty}
        text_box = wx.TextCtrl(frame, value="", pos=(-1, install_button.GetPosition()[1] + install_button.GetSize()[1] + 10), size=(400, 350), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        text_box.Center(wx.HORIZONTAL)
        self.text_box = text_box

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(-1, text_box.GetPosition()[1] + text_box.GetSize()[1] + 5), size=(200, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_to_main_menu)
        return_button.Center(wx.HORIZONTAL)
        return_button.Disable()
        self.return_button = return_button

        # Adjust window size to fit all elements
        frame.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))


    def _invoke_build(self):
        while gui_support.PayloadMount(self.constants, self).is_unpack_finished() is False:
            wx.Yield()

        thread = threading.Thread(target=self._build)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        self.return_button.Enable()
        dialog = wx.MessageDialog(
            parent=self,
            message=f"Would you like to install OpenCore now?",
            caption="Finished building your OpenCore configuration!",
            style=wx.YES_NO | wx.ICON_QUESTION
        )
        dialog.SetYesNoLabels("Install to disk", "View build log")

        self.on_install() if dialog.ShowModal() == wx.ID_YES else self.install_button.Enable()


    def _build(self):
        """
        Calls build function and redirects stdout to the text box
        """
        logger = logging.getLogger()
        logger.addHandler(gui_support.ThreadHandler(self.text_box))
        try:
            build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants)
        except:
            logging.error("- An internal error occurred while building:\n")
            logging.error(traceback.format_exc())
        logger.removeHandler(logger.handlers[2])


    def on_return_to_main_menu(self, event: wx.Event = None):
        self.frame_modal.Hide()
        main_menu_frame = gui_main_menu.MainMenu(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        main_menu_frame.Show()
        self.frame_modal.Destroy()
        self.Destroy()


    def on_install(self, event: wx.Event = None):
        self.frame_modal.Destroy()
        self.Destroy()
        install_oc_frame = gui_install_oc.InstallOCFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetScreenPosition()
        )
        install_oc_frame.Show()


