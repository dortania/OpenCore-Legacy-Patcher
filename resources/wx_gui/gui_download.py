# Generate UI for downloading files
import wx
import logging

from resources import (
    constants,
    network_handler,
    utilities
)


class DownloadFrame(wx.Frame):
    """
    Update provided frame with download stats
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, download_obj: network_handler.DownloadObject, item_name: str) -> None:
        logging.info("Initializing Download Frame")
        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.parent: wx.Frame = parent
        self.download_obj: network_handler.DownloadObject = download_obj
        self.item_name: str = item_name

        self.user_cancelled: bool = False

        self.frame_modal = wx.Dialog(parent, title=title, size=(400, 200))

        self._generate_elements(self.frame_modal)


    def _generate_elements(self, frame: wx.Dialog = None) -> None:
        """
        Generate elements for download frame
        """

        frame = self if not frame else frame

        title_label = wx.StaticText(frame, label=f"Downloading: {self.item_name}", pos=(-1,5))
        title_label.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        title_label.Centre(wx.HORIZONTAL)

        label_amount = wx.StaticText(frame, label="0.00 B downloaded of 0.00B (0.00%)", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 5))
        label_amount.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        label_amount.Centre(wx.HORIZONTAL)

        label_speed = wx.StaticText(frame, label="Average download speed: Unknown", pos=(-1, label_amount.GetPosition()[1] + label_amount.GetSize()[1] + 5))
        label_speed.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        label_speed.Centre(wx.HORIZONTAL)

        label_est_time = wx.StaticText(frame, label="Estimated time remaining: Unknown", pos=(-1, label_speed.GetPosition()[1] + label_speed.GetSize()[1] + 5))
        label_est_time.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        label_est_time.Centre(wx.HORIZONTAL)

        progress_bar = wx.Gauge(frame, range=100, pos=(-1, label_est_time.GetPosition()[1] + label_est_time.GetSize()[1] + 5), size=(300, 20))
        progress_bar.Centre(wx.HORIZONTAL)

        return_button = wx.Button(frame, label="Return", pos=(-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 5))
        return_button.Bind(wx.EVT_BUTTON, lambda event: self.terminate_download())
        return_button.Centre(wx.HORIZONTAL)

        # Set size of frame
        frame.SetSize((-1, return_button.GetPosition()[1] + return_button.GetSize()[1] + 40))
        frame.ShowWindowModal()

        self.download_obj.download()
        while self.download_obj.is_active():
            if self.download_obj.get_percent() == -1:
                amount_str = f"{utilities.human_fmt(self.download_obj.downloaded_file_size)} downloaded"
            else:
                amount_str = f"{utilities.human_fmt(self.download_obj.downloaded_file_size)} downloaded of {utilities.human_fmt(self.download_obj.total_file_size)} ({self.download_obj.get_percent():.2f}%)"
            label_amount.SetLabel(amount_str)
            label_amount.Centre(wx.HORIZONTAL)

            label_speed.SetLabel(
                f"Average download speed: {utilities.human_fmt(self.download_obj.get_speed())}/s"
            )

            label_est_time.SetLabel(
                f"Estimated time remaining: {utilities.seconds_to_readable_time(self.download_obj.get_time_remaining())}"
            )

            progress_bar.SetValue(int(self.download_obj.get_percent()))
            wx.Yield()

        if self.download_obj.download_complete is False and self.user_cancelled is False:
            wx.MessageBox(f"Download failed: \n{self.download_obj.error_msg}", "Error", wx.OK | wx.ICON_ERROR)

        frame.Destroy()


    def terminate_download(self) -> None:
        """
        Terminate download
        """
        if wx.MessageBox("Are you sure you want to cancel the download?", "Cancel Download", wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT) == wx.YES:
            logging.info("User cancelled download")
            self.user_cancelled = True
            self.download_obj.stop()


