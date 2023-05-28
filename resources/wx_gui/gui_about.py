# About frame, just to sat

import wx
import wx.adv
import logging

from resources.wx_gui import gui_support

from resources import constants


class AboutFrame(wx.Frame):

    def __init__(self, global_constants: constants.Constants) -> None:
        if wx.FindWindowByName("About"):
            return

        logging.info("Generating About frame")
        super(AboutFrame, self).__init__(None, title="About", size=(350, 350), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.constants: constants.Constants = global_constants
        gui_support.Centre(self, self.constants)
        self.hyperlink_colour = (25, 179, 231)

        self._generate_elements(self)

        self.Show()


    def _generate_elements(self, frame: wx.Frame) -> None:

        # Set title
        title = wx.StaticText(frame, label="OpenCore Legacy Patcher", pos=(-1, 5))
        title.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title.Centre(wx.HORIZONTAL)

        # Set version
        version = wx.StaticText(frame, label=f"Version: {self.constants.patcher_version}", pos=(-1, title.GetPosition()[1] + title.GetSize()[1] + 5))
        version.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        version.Centre(wx.HORIZONTAL)

        # Description
        description = [
            "Written by a small group of Mac hobbyists who just",
            "want to keep old machines out of the landfill!",

        ]
        spacer = 5
        for line in description:
            desc = wx.StaticText(frame, label=line, pos=(-1, version.GetPosition()[1] + version.GetSize()[1] + 5 + spacer))
            desc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            desc.Centre(wx.HORIZONTAL)

            spacer += 20

        # Set icon
        icon_mac = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/com.apple.macbook-unibody-plastic.icns"
        icon_mac = wx.StaticBitmap(frame, bitmap=wx.Bitmap(icon_mac, wx.BITMAP_TYPE_ICON), pos=(5, desc.GetPosition()[1] - 15))
        icon_mac.SetSize((160, 160))
        icon_mac.Centre(wx.HORIZONTAL)

        icon_path = str(self.constants.app_icon_path)
        icon = wx.StaticBitmap(frame, bitmap=wx.Bitmap(icon_path, wx.BITMAP_TYPE_ICON), pos=(5, desc.GetPosition()[1] + desc.GetSize()[1] + 17))
        icon.SetSize((64, 64))
        icon.Centre(wx.HORIZONTAL)

        # Set frame size
        frame.SetSize((-1, icon.GetPosition()[1] + icon.GetSize()[1] + 60))
