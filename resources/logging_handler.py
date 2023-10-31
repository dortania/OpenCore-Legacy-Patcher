import os
import sys
import pprint
import logging
import threading
import traceback
import subprocess
import applescript

from pathlib import Path
from datetime import datetime

from resources import constants, analytics_handler, global_settings


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

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants

        log_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

        self.log_filename: str  = f"OpenCore-Patcher_{self.constants.patcher_version}_{log_time}.log"
        self.log_filepath: Path = None

        self.original_excepthook:        sys       = sys.excepthook
        self.original_thread_excepthook: threading = threading.excepthook

        self.max_file_size:     int = 1024 * 1024               # 1 MB
        self.file_size_redline: int = 1024 * 1024 - 1024 * 100  # 900 KB, when to start cleaning log file

        self._initialize_logging_path()
        self._attempt_initialize_logging_configuration()
        self._start_logging()
        self._implement_custom_traceback_handler()
        self._fix_file_permission()
        self._clean_prior_version_logs()


    def _initialize_logging_path(self) -> None:
        """
        Initialize logging framework storage path
        """

        base_path = Path("~/Library/Logs").expanduser()
        if not base_path.exists() or str(base_path).startswith("/var/root/"):
            # Likely in an installer environment, store in /Users/Shared
            base_path = Path("/Users/Shared")
        else:
            # create Dortania folder if it doesn't exist
            base_path = base_path / "Dortania"
            if not base_path.exists():
                try:
                    base_path.mkdir()
                except Exception as e:
                    print(f"Failed to create Dortania folder: {e}")
                    base_path = Path("/Users/Shared")

        self.log_filepath = Path(f"{base_path}/{self.log_filename}").expanduser()
        self.constants.log_filepath = self.log_filepath

    def _clean_prior_version_logs(self) -> None:
        """
        Clean logs from old Patcher versions

        Keep 10 latest logs
        """

        paths = [
            self.log_filepath.parent,        # ~/Library/Logs/Dortania
            self.log_filepath.parent.parent, # ~/Library/Logs (old location)
        ]

        logs = []

        for path in paths:
            for file in path.glob("OpenCore-Patcher*"):
                if not file.is_file():
                    continue

                if not file.name.endswith(".log"):
                    continue

                if file.name == self.log_filename:
                    continue

                logs.append(file)

        logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for log in logs[9:]:
            try:
                log.unlink()
            except Exception as e:
                logging.error(f"Failed to delete log file: {e}")


    def _fix_file_permission(self) -> None:
        """
        Fixes file permission for log file

        If OCLP was invoked as root, file permission will only allow root to write to log file
        This in turn breaks normal OCLP execution to write to log file
        """

        if os.geteuid() != 0:
            return

        paths = [
            self.log_filepath,        # ~/Library/Logs/Dortania/OpenCore-Patcher_{version}_{date}.log
            self.log_filepath.parent, # ~/Library/Logs/Dortania
        ]

        for path in paths:
            result = subprocess.run(["chmod", "777", path], capture_output=True)
            if result.returncode != 0:
                logging.error(f"Failed to fix log file permissions")
                if result.stdout:
                    logging.error("STDOUT:")
                    logging.error(result.stdout.decode("utf-8"))
                if result.stderr:
                    logging.error("STDERR:")
                    logging.error(result.stderr.decode("utf-8"))


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
            format="[%(asctime)s] [%(filename)-32s] [%(lineno)-4d]: %(message)s",
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
            print(f"Failed to initialize logging framework: {e}")
            print("Retrying without logging to file...")
            self._initialize_logging_configuration(log_to_file=False)


    def _start_logging(self):
        """
        Start logging, used as easily identifiable start point in logs
        """

        str_msg = f"# OpenCore Legacy Patcher ({self.constants.patcher_version}) #"
        str_len = len(str_msg)

        logging.info('#' * str_len)
        logging.info(str_msg)
        logging.info('#' * str_len)

        logging.info("Log file set:")
        logging.info(f"  {self.log_filepath}")
        # Display relative path to avoid disclosing user's username
        try:
            path = self.log_filepath.relative_to(Path.home())
            logging.info(f"~/{path}")
        except ValueError:
            logging.info(self.log_filepath)


    def _implement_custom_traceback_handler(self) -> None:
        """
        Reroute traceback to logging module
        """

        def custom_excepthook(type, value, tb) -> None:
            """
            Reroute traceback in main thread to logging module
            """
            logging.error("Uncaught exception in main thread", exc_info=(type, value, tb))
            self._display_debug_properties()

            if "wx/" in "".join(traceback.format_exception(type, value, tb)):
                # Likely a GUI error, don't display error dialog
                return

            if self.constants.cli_mode is True:
                threading.Thread(target=analytics_handler.Analytics(self.constants).send_crash_report, args=(self.log_filepath,)).start()
                return

            error_msg = f"OpenCore Legacy Patcher encountered the following internal error:\n\n"
            error_msg += f"{type.__name__}: {value}"
            if tb:
                error_msg += f"\n\n{traceback.extract_tb(tb)[-1]}"

            cant_log: bool = global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting")
            if not isinstance(cant_log, bool):
                cant_log = False

            if self.constants.commit_info[0].startswith("refs/tags"):
                cant_log = True

            if cant_log is True:
                error_msg += "\n\nReveal log file?"
            else:
                error_msg += "\n\nSend crash report to Dortania?"

            # Ask user if they want to send crash report
            try:
                result = applescript.AppleScript(f'display dialog "{error_msg}" with title "OpenCore Legacy Patcher ({self.constants.patcher_version})" buttons {{"Yes", "No"}} default button "Yes" with icon caution').run()
            except Exception as e:
                logging.error(f"Failed to display crash report dialog: {e}")
                return

            if result[applescript.AEType(b'bhit')] != "Yes":
                return

            if cant_log is True:
                subprocess.run(["open", "--reveal", self.log_filepath])
                return

            threading.Thread(target=analytics_handler.Analytics(self.constants).send_crash_report, args=(self.log_filepath,)).start()


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


    def _display_debug_properties(self) -> None:
        """
        Display debug properties, primarily after main thread crash
        """
        logging.info("Host Properties:")
        logging.info(f"  XNU Version: {self.constants.detected_os}.{self.constants.detected_os_minor}")
        logging.info(f"  XNU Build: {self.constants.detected_os_build}")
        logging.info(f"  macOS Version: {self.constants.detected_os_version}")
        logging.info("Debug Properties:")
        logging.info(f"  Effective User ID: {os.geteuid()}")
        logging.info(f"  Effective Group ID: {os.getegid()}")
        logging.info(f"  Real User ID: {os.getuid()}")
        logging.info(f"  Real Group ID: {os.getgid()}")
        logging.info("  Arguments passed to Patcher:")
        for arg in sys.argv:
            logging.info(f"    {arg}")

        logging.info(f"Host Properties:\n{pprint.pformat(self.constants.computer.__dict__, indent=4)}")
