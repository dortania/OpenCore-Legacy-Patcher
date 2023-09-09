# Generate UI for help menu
import wx
import logging
import webbrowser

from resources import constants


class HelpFrame(wx.Frame):
    """
    Append to main menu through a modal dialog
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None) -> None:
        logging.info("Initializing Help Frame")
        self.dialog = wx.Dialog(parent, title=title, size=(300, 200))

        self.constants: constants.Constants = global_constants
        self.title: str = title

        self._generate_elements(self.dialog)
        self.dialog.ShowWindowModal()


    def _generate_elements(self, frame: wx.Frame = None) -> None:
        """
        Format:
            - Title: Patcher Resources
            - Text:  Following resources are available:
            - Button: Official Guide
            - Button: Community Discord Server
            - Button: Official Phone Support
            - Button: Return to Main Menu
        """

        frame = self if not frame else frame

        title_label = wx.StaticText(frame, label="Patcher Resources", pos=(-1,5))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, self.constants.apple_font))
        title_label.Centre(wx.HORIZONTAL)

        text_label = wx.StaticText(frame, label="Following resources are available:", pos=(-1,30))
        text_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, self.constants.apple_font))
        text_label.Centre(wx.HORIZONTAL)

        buttons = {
            "Official Guide":           self.constants.guide_link,
            "Official Phone Support":   "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "Community Discord Server": self.constants.discord_link,
        }

        for button in buttons:
            help_button = wx.Button(frame, label=button, pos=(-1, text_label.GetPosition()[1] + text_label.GetSize()[1] + (list(buttons.keys()).index(button) * 30)), size=(200, 30))
            help_button.Bind(wx.EVT_BUTTON, lambda event, temp=buttons[button]: webbrowser.open(temp))
            help_button.Centre(wx.HORIZONTAL)

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(-1, help_button.GetPosition()[1] + help_button.GetSize()[1]), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, lambda event: frame.Close())
        return_button.Centre(wx.HORIZONTAL)

        # Set size of frame
        frame.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))





