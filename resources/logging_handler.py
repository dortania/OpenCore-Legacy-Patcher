import logging
import sys
import threading
import os
import subprocess
from pathlib import Path


class InitializeLoggingSupport:
    """
    Initialize logging framework for program

    Primary responsibilities:
    - Determine where to store log file
    - Clean log file if it's near the max file size
    - Initialize logging framework configuration
    - Implement custom traceback handler
    - Implement error handling for file write

    Usage:
    >>> from resources.logging_handler import InitializeLoggingSupport
    >>> InitializeLoggingSupport()

    FOR DEVELOPERS:
    - Do not invoke logging until after '_attempt_initialize_logging_configuration()' has been invoked

    """

    def __init__(self) -> None:
        self.log_filename: str  = "OpenCore-Patcher.log"
        self.log_filepath: Path = None

        self.original_excepthook:        sys       = sys.excepthook
        self.original_thread_excepthook: threading = threading.excepthook

        self.max_file_size:     int = 1024 * 1024 * 10  # 10 MB
        self.file_size_redline: int = 1024 * 1024 * 9   # 9 MB, when to start cleaning log file

        self._initialize_logging_path()
        self._clean_log_file()
        self._attempt_initialize_logging_configuration()
        self._implement_custom_traceback_handler()
        self._fix_file_permission()


    def __del__(self) -> None:
        self._restore_original_excepthook()


    def _initialize_logging_path(self) -> None:
        """
        Initialize logging framework storage path
        """

        self.log_filepath = Path(f"~/Library/Logs/{self.log_filename}").expanduser()

        if not self.log_filepath.parent.exists():
             # Likely in an installer environment, store in /Users/Shared
            self.log_filepath = Path("/Users/Shared") / self.log_filename

        print("- Initializing logging framework...")
        print(f"  - Log file: {self.log_filepath}")


    def _clean_log_file(self) -> None:
        """
        Determine if log file should be cleaned

        We check if we're near the max file size, and if so, we clean the log file
        """

        if not self.log_filepath.exists():
            return

        if self.log_filepath.stat().st_size < self.file_size_redline:
            return

        # Check if backup log file exists
        backup_log_filepath = self.log_filepath.with_suffix(".old.log")
        try:
            if backup_log_filepath.exists():
                backup_log_filepath.unlink()

            # Rename current log file to backup log file
            self.log_filepath.rename(backup_log_filepath)
        except Exception as e:
            print(f"- Failed to clean log file: {e}")


    def _fix_file_permission(self) -> None:
        """
        Fixes file permission for log file

        If OCLP was invoked as root, file permission will only allow root to write to log file
        This in turn breaks normal OCLP execution to write to log file
        """

        if os.geteuid() != 0:
            return

        result = subprocess.run(["chmod", "777", self.log_filepath], capture_output=True)
        if result.returncode != 0:
            print(f"- Failed to fix log file permissions")
            if result.stderr:
                print(result.stderr.decode("utf-8"))


    def _initialize_logging_configuration(self, log_to_file: bool = True) -> None:
        """
        Initialize logging framework configuration

        StreamHandler's format is used to mimic the default behavior of print()
        While FileHandler's format is for more in-depth logging

        Parameters:
            log_to_file (bool): Whether to log to file or not

        """

        logging.basicConfig(
            level=logging.NOTSET,
            format="%(asctime)s - %(filename)s (%(lineno)d): %(message)s",
            handlers=[
                logging.StreamHandler(stream = sys.stdout),
                logging.FileHandler(self.log_filepath) if log_to_file is True else logging.NullHandler()
            ],
        )
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().handlers[1].maxBytes = self.max_file_size


    def _attempt_initialize_logging_configuration(self) -> None:
        """
        Attempt to initialize logging framework configuration

        If we fail to initialize the logging framework, we will disable logging to file
        """

        try:
            self._initialize_logging_configuration()
        except Exception as e:
            print(f"- Failed to initialize logging framework: {e}")
            print("- Retrying without logging to file...")
            self._initialize_logging_configuration(log_to_file=False)


    def _implement_custom_traceback_handler(self) -> None:
        """
        Reroute traceback to logging module
        """

        def custom_excepthook(type, value, tb) -> None:
            """
            Reroute traceback in main thread to logging module
            """
            logging.error("Uncaught exception in main thread", exc_info=(type, value, tb))

        def custom_thread_excepthook(args) -> None:
            """
            Reroute traceback in spawned thread to logging module
            """
            logging.error("Uncaught exception in spawned thread", exc_info=(args))

        sys.excepthook = custom_excepthook
        threading.excepthook = custom_thread_excepthook


    def _restore_original_excepthook(self) -> None:
        """
        Restore original traceback handlers
        """

        sys.excepthook = self.original_excepthook
        threading.excepthook = self.original_thread_excepthook
