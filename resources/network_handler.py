# Download files from the network
# Implements an object, where other libraries can use to query download status

import time
import requests
import threading
import logging
from pathlib import Path

from resources import utilities


SESSION = requests.Session()

class network_utilities:

    def __init__(self, url):
        self.url: str = url


    def verify_network_connection(self):
        try:
            response = requests.head(self.url, timeout=5, allow_redirects=True)
            return True
        except (
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        ):
            return False


class download_object:

    def __init__(self, url):
        self.url:       str = url
        self.status:    str = "Downloading"
        self.error_msg: str = ""
        self.filename:  str = self._get_filename()

        self.total_file_size:      float = 0.0
        self.downloaded_file_size: float = 0.0
        self.start_time:           float = time.time()

        self.error:             bool = False
        self.should_stop:       bool = False
        self.has_network:       bool = network_utilities(self.url).verify_network_connection()
        self.download_complete: bool = False

        self.active_thread: threading.Thread = None

        if self.has_network:
            self._populate_file_size()


    def __del__(self):
        self.stop()


    def download(self, path, display_progress=False):
        if self.active_thread:
            return
        logging.info(f"Starting download: {self.filename}")
        self.active_thread = threading.Thread(target=self._download, args=(path,display_progress,))
        self.active_thread.start()


    def _get_filename(self):
        return Path(self.url).name


    def _populate_file_size(self):
        try:
            self.total_file_size = int(requests.head(self.url, allow_redirects=True, timeout=5).headers['Content-Length'])
        except Exception as e:
            self.error = True
            self.error_msg = str(e)
            self.status = "Error"
            logging.error(f"Error determining file size {self.url}: {self.error_msg}")


    def _prepare_working_directory(self, path):
        if Path(path).exists():
            Path(path).unlink()


    def _download(self, path, display_progress=False):
        try:
            if not self.has_network:
                raise Exception("No network connection")

            self._prepare_working_directory(path)

            response = SESSION.get(self.url, stream=True)

            with open(path, 'wb') as file:
                for i, chunk in enumerate(response.iter_content(1024 * 1024 * 4)):
                    if self.should_stop:
                        raise Exception("Download stopped")
                    if chunk:
                        file.write(chunk)
                        self.downloaded_file_size += len(chunk)
                        if display_progress and i % 100:
                            # Don't use logging here, as we'll be spamming the log file
                            print(f"Downloaded {self.get_percent():.2f}% of {self.filename} ({utilities.human_fmt(self.get_speed())}/s) ({self.get_time_remaining():.2f} seconds remaining)")
                self.download_complete = True
                logging.info(f"Download complete: {self.filename}")
        except Exception as e:
            self.error = True
            self.error_msg = str(e)
            self.status = "Error"
            logging.error(f"Error downloading {self.url}: {self.error_msg}")
        self.status = "Done"


    def get_percent(self):
        if self.total_file_size == 0:
            logging.error("File size is 0, cannot calculate percent")
            return -1
        return self.downloaded_file_size / self.total_file_size * 100


    def get_speed(self):
        return self.downloaded_file_size / (time.time() - self.start_time)


    def get_time_remaining(self):
        if self.total_file_size == 0:
            logging.error("File size is 0, cannot calculate time remaining")
            return -1
        return (self.total_file_size - self.downloaded_file_size) / self.get_speed()


    def get_file_size(self):
        return self.total_file_size


    def is_active(self):
        if self.status == "Downloading":
            return True
        return False


    def stop(self):
        self.should_stop = True





