# Generates menubar for wxPython to use

import wx

class GenerateMenubar:

    def __init__(self) -> None:
        self.menubar: wx.MenuBar = None


    def generate(self) -> wx.MenuBar:
        self.menubar = wx.MenuBar()

        return self.menubar