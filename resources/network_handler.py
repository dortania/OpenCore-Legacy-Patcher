# Library dedicated to Network Handling tasks including downloading files
# Primarily based around the DownloadObject class, which provides a simple
# object for libraries to query download progress and status
# Copyright (C) 2023, Mykola Grymalyuk

import time
import requests
import threading
import logging
import enum
from pathlib import Path

from resources import utilities

SESSION = requests.Session()


class DownloadStatus(enum.Enum):
    """
    Enum for download status
    """

    INACTIVE:    str = "Inactive"
    DOWNLOADING: str = "Downloading"
    ERROR:       str = "Error"
    COMPLETE:    str = "Complete"


class NetworkUtilities:
    """
    Utilities for network related tasks, primarily used for downloading files
    """

    def __init__(self, url: str):
        self.url: str = url


    def verify_network_connection(self):
        """
        Verifies that the network is available

        Returns:
            bool: True if network is available, False otherwise
        """

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


class DownloadObject:
    """
    Object for downloading files from the network

    Usage:
        >>> download_object = DownloadObject(url, path)
        >>> download_object.download(display_progress=True)

        >>> if download_object.is_active():
        >>>     print(download_object.get_percent())

        >>> if not download_object.download_complete:
        >>>     print("Download failed")

        >>> print("Download complete"")

    """

    def __init__(self, url: str, path: str):
        self.url:       str = url
        self.status:    str = DownloadStatus.INACTIVE
        self.error_msg: str = ""
        self.filename:  str = self._get_filename()

        self.filepath:  Path = Path(path)

        self.total_file_size:      float = 0.0
        self.downloaded_file_size: float = 0.0
        self.start_time:           float = time.time()

        self.error:             bool = False
        self.should_stop:       bool = False
        self.download_complete: bool = False
        self.has_network:       bool = NetworkUtilities(self.url).verify_network_connection()

        self.active_thread: threading.Thread = None

        if self.has_network:
            self._populate_file_size()


    def __del__(self):
        self.stop()


    def download(self, display_progress: bool = False, spawn_thread: bool = True):
        """
        Download the file

        Spawns a thread to download the file, so that the main thread can continue
        Note sleep is disabled while the download is active

        Parameters:
            display_progress (bool): Display progress in console
            spawn_thread (bool): Spawn a thread to download the file, otherwise download in the current thread

        """
        self.status = DownloadStatus.DOWNLOADING
        logging.info(f"Starting download: {self.filename}")
        if spawn_thread:
            if self.active_thread:
                logging.error("Download already in progress")
                return
            self.active_thread = threading.Thread(target=self._download, args=(display_progress,))
            self.active_thread.start()
        else:
            self._download(display_progress)


    def _get_filename(self):
        """
        Get the filename from the URL

        Returns:
            str: Filename
        """

        return Path(self.url).name


    def _populate_file_size(self):
        """
        Get the file size of the file to be downloaded

        If unable to get file size, set to zero
        """

        try:
            result = requests.head(self.url, allow_redirects=True, timeout=5)
            if 'Content-Length' in result.headers:
                self.total_file_size = float(result.headers['Content-Length'])
            else:
                raise Exception("Content-Length missing from headers")
        except Exception as e:
            logging.error(f"Error determining file size {self.url}: {str(e)}")
            logging.error("Assuming file size is 0")
            self.total_file_size = 0.0


    def _prepare_working_directory(self, path: Path):
        """
        Delete the file if it already exists

        Parameters:
            path (str): Path to the file

        Returns:
            bool: True if successful, False if not
        """

        try:
            if Path(path).exists():
                logging.info(f"Deleting existing file: {path}")
                Path(path).unlink()
                return True
            if not Path(path).parent.exists():
                logging.info(f"Creating directory: {Path(path).parent}")
                Path(path).parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error = True
            self.error_msg = str(e)
            self.status = DownloadStatus.ERROR
            logging.error(f"Error preparing working directory {path}: {self.error_msg}")
            return False

        return True


    def _download(self, display_progress: bool = False):
        """
        Download the file

        Libraries should invoke download() instead of this method

        Parameters:
            display_progress (bool): Display progress in console
        """

        utilities.disable_sleep_while_running()

        try:
            if not self.has_network:
                raise Exception("No network connection")

            if self._prepare_working_directory(self.filepath) is False:
                raise Exception(self.error_msg)

            response = SESSION.get(self.url, stream=True, timeout=10)

            with open(self.filepath, 'wb') as file:
                for i, chunk in enumerate(response.iter_content(1024 * 1024 * 4)):
                    if self.should_stop:
                        raise Exception("Download stopped")
                    if chunk:
                        file.write(chunk)
                        self.downloaded_file_size += len(chunk)
                        if display_progress and i % 100:
                            # Don't use logging here, as we'll be spamming the log file
                            if self.total_file_size == 0.0:
                                print(f"Downloaded {utilities.human_fmt(self.downloaded_file_size)} of {self.filename}")
                            else:
                                print(f"Downloaded {self.get_percent():.2f}% of {self.filename} ({utilities.human_fmt(self.get_speed())}/s) ({self.get_time_remaining():.2f} seconds remaining)")
                self.download_complete = True
                logging.info(f"Download complete: {self.filename}")
        except Exception as e:
            self.error = True
            self.error_msg = str(e)
            self.status = DownloadStatus.ERROR
            logging.error(f"Error downloading {self.url}: {self.error_msg}")

        self.status = DownloadStatus.COMPLETE
        utilities.enable_sleep_after_running()


    def get_percent(self):
        """
        Query the download percent

        Returns:
            float: The download percent, or -1 if unknown
        """

        if self.total_file_size == 0.0:
            logging.error("File size is 0, cannot calculate percent")
            return -1
        return self.downloaded_file_size / self.total_file_size * 100


    def get_speed(self):
        """
        Query the download speed

        Returns:
            float: The download speed in bytes per second
        """

        return self.downloaded_file_size / (time.time() - self.start_time)


    def get_time_remaining(self):
        """
        Query the time remaining for the download

        Returns:
            float: The time remaining in seconds, or -1 if unknown
        """

        if self.total_file_size == 0.0:
            logging.error("File size is 0, cannot calculate time remaining")
            return -1
        return (self.total_file_size - self.downloaded_file_size) / self.get_speed()


    def get_file_size(self):
        """
        Query the file size of the file to be downloaded

        Returns:
            float: The file size in bytes, or 0.0 if unknown
        """

        return self.total_file_size


    def is_active(self):
        """
        Query if the download is active

        Returns:
            boolean: True if active, False if completed, failed, stopped, or inactive
        """

        if self.status == DownloadStatus.DOWNLOADING:
            return True
        return False


    def stop(self):
        """
        Stop the download

        Returns:
            boolean: If the download is active, this function will hold the thread until stopped
        """

        self.should_stop = True
        if self.active_thread.is_alive():
            time.sleep(1)