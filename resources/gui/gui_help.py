import wx
import webbrowser
from resources import constants
from data import os_data

class gui_help_menu:
    def __init__(self, versions, frame, frame_modal):
        self.constants: constants.Constants = versions
        self.frame = frame
        self.frame_modal = frame_modal

        # Define Window Size
        self.WINDOW_WIDTH_MAIN  = 300


    def reset_frame_modal(self):
        if not self.frame_modal:
            self.frame_modal = wx.Dialog(self.frame)
        else:
            self.frame_modal.DestroyChildren()
            self.frame_modal.Close()
            if self.constants.detected_os >= os_data.os_data.big_sur:
                self.frame_modal.ShowWithoutActivating()

    def help_menu(self, event=None):
        # Define Menu
        # Header: Get help with OpenCore Legacy Patcher
        # Subheader: Following resources are available:
        # Button: Official Guide
        # Button: Official Discord Server

        self.reset_frame_modal()
        self.frame_modal.SetSize((self.WINDOW_WIDTH_MAIN, -1))

        # Header
        self.header = wx.StaticText(self.frame_modal, label="Patcher Resources", pos=(10,10))
        self.header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header.Centre(wx.HORIZONTAL)

        # Subheader
        self.subheader = wx.StaticText(self.frame_modal, label="Following resources are available:")
        self.subheader.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subheader.SetPosition(
            wx.Point(
                self.header.GetPosition().x,
                self.header.GetPosition().y + self.header.GetSize().height + 5
            )
        )
        self.subheader.Centre(wx.HORIZONTAL)


        # Official Guide
        self.guide = wx.Button(self.frame_modal, label="Official Guide", size=(200,30))
        self.guide.SetPosition(
            wx.Point(
                self.subheader.GetPosition().x,
                self.subheader.GetPosition().y + self.subheader.GetSize().height + 5

            )
        )
        self.guide.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(self.constants.guide_link))
        self.guide.Centre(wx.HORIZONTAL)

        # Official Discord Server
        self.discord = wx.Button(self.frame_modal, label="Official Discord Server", size=(200,30))
        self.discord.SetPosition(
            wx.Point(
                self.guide.GetPosition().x,
                self.guide.GetPosition().y + self.guide.GetSize().height
            )
        )
        self.discord.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open(self.constants.discord_link))
        self.discord.Centre(wx.HORIZONTAL)

        # Overclock Button
        self.overclock = wx.Button(self.frame_modal, label="Official Support Phone", size=(200,30))
        self.overclock.SetPosition(
            wx.Point(
                self.discord.GetPosition().x,
                self.discord.GetPosition().y + self.discord.GetSize().height
            )
        )
        self.overclock.Bind(wx.EVT_BUTTON, lambda event: webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.overclock.Centre(wx.HORIZONTAL)


        self.return_to_main = wx.Button(self.frame_modal, label="Return to Main Menu", size=(150,30))
        self.return_to_main.SetPosition(
            wx.Point(
                self.overclock.GetPosition().x,
                self.overclock.GetPosition().y + self.overclock.GetSize().height + 5
            )
        )
        self.return_to_main.Bind(wx.EVT_BUTTON, lambda event: self.frame_modal.Close())
        self.return_to_main.Centre(wx.HORIZONTAL)

        # Set Window Size to below Copyright Label
        self.frame_modal.SetSize(
            (
                -1,
                self.return_to_main.GetPosition().y + self.return_to_main.GetSize().height + 40
            )
        )
        self.frame_modal.ShowWindowModal()
