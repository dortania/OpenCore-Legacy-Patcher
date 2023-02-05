import logging
import sys
import threading
from pathlib import Path


class InitializeLoggingSupport:


    def __init__(self) -> None:
        self.log_filename: str  = f"OpenCore-Patcher.log"
        self.log_filepath: Path = None

        self.max_file_size:     int = 1024 * 1024 * 10
        self.file_size_redline: int = 1024 * 1024 * 9  # When to start cleaning log file

        self._initialize_logging_path()
        self._clean_log_file()
        self._initialize_logging_configuration()
        self._implement_custom_traceback_handler()


    def _initialize_logging_path(self):
        """
        Initialize logging framework storage path
        """

        self.log_filepath = Path(f"~/Library/Logs/{self.log_filename}").expanduser()

        if self.log_filepath.parent.exists():
            return

        # Likely in an installer environment, store in /Users/Shared
        self.log_filepath = Path("/Users/Shared") / self.log_filename


    def _clean_log_file(self):
        """
        Determine if log file should be cleaned

        We check if we're near the max file size, and if so, we clean the log file
        """

        if self.log_filepath.stat().st_size < self.file_size_redline:
            return

        # Check if backup log file exists
        backup_log_filepath = self.log_filepath.with_suffix(".old.log")
        if backup_log_filepath.exists():
            backup_log_filepath.unlink()

        # Rename current log file to backup log file
        self.log_filepath.rename(backup_log_filepath)


    def _initialize_logging_configuration(self):
        """
        Initialize logging framework configuration

        StreamHandler's format is used to mimic the default behavior of print()
        While FileHandler's format is for more in-depth logging
        """

        logging.basicConfig(
            level=logging.NOTSET,
            format="%(asctime)s - %(filename)s (%(lineno)d): %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_filepath),
            ],
        )
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().handlers[1].maxBytes = self.max_file_size


    def _implement_custom_traceback_handler(self):
        """
        Reroute traceback to logging module
        """

        def custom_excepthook(type, value, tb):
            """
            Reroute traceback in main thread to logging module
            """
            logging.error("Uncaught exception in main thread", exc_info=(type, value, tb))

        def custom_thread_excepthook(args):
            """
            Reroute traceback in spawned thread to logging module
            """
            logging.error("Uncaught exception in spawned thread", exc_info=(args))

        sys.excepthook = custom_excepthook
        threading.excepthook = custom_thread_excepthook