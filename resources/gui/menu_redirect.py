import wx
import time

class RedirectText(object):
    def __init__(self,aWxTextCtrl, sleep):
        self.out=aWxTextCtrl
        self.sleep = sleep

    def write(self,string):
        self.out.WriteText(string)
        wx.GetApp().Yield()
        if self.sleep:
            time.sleep(0.01)

    def fileno(self):
        return 1

    def flush(self):
        pass

class RedirectLabel(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        if string.endswith("MB/s"):
            self.out.SetLabel(string)
            self.out.Centre(wx.HORIZONTAL)
        wx.GetApp().Yield()
        time.sleep(0.01)

    def flush(self):
        pass

class RedirectLabelAll(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.SetLabel(string)
        self.out.Centre(wx.HORIZONTAL)
        wx.GetApp().Yield()
        time.sleep(0.01)