from .base import Config

from logging import getLogger, Formatter, StreamHandler, Filter
from logging.handlers import RotatingFileHandler
# from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

from os import path, makedirs
from sys import stdout, stderr
from humanfriendly import parse_size


class ExcludeExceptionsFilter(Filter):

    def filter(self, record):
        return not record.exc_info


class Logger(object):
    """
    A Singleton class that configures and provides a centralized logger for the
    application.
    - Configures a console handler for verbose logging.
    - Configures a file handler with log rotation.
    - Retrieves logging configurations from the provided configuration source.

    It ensures consistent logging behavior across the entire application.
    """

    # -------------------------------------------------------------------------
    # Singleton
    # -------------------------------------------------------------------------

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures the class follows the Singleton pattern.
        Creates a single instance of the class and reuses it in subsequent
        calls.

        :param args: Positional arguments for initialization.
        :param kwargs: Keyword arguments for initialization.
        :return: The single instance of the Logger class.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    _config = None

    def __init__(self):
        """
        Initializes the logger and configures handlers based on the provided
        configuration.
        - Sets the logging level to the most permissive level.
        - Configures a handler for console output (verbose).
        - Configures a handler for log rotation in a file.
        """

        if not getattr(self, '_logger', None):
            self._logger = getLogger(__name__)
            self._config = Config()

            log_level = self._get_most_permissive_level()
            self._logger.setLevel(log_level)

            self._configure_verbose_handler()

            metadata_path = self._get_config_value('metadata', 'folder')
            if path.exists(metadata_path):
                self._configure_logrotate_handler(metadata_path)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def logger(self):
        """
        Returns the configured logger instance.

        :return: Instance of logging.Logger.
        """

        return self._logger

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------

    def close(self):
        """
        Close all handlers associated with the logger.
        :param logger: Instance of logging.Logger.
        """
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    def _configure_verbose_handler(self):
        """
        Configures the StreamHandler for console output.
        - Retrieves the logging level, output stream, and format from the
        configuration.
        - Adds the handler to the main logger.

        :raises ValueError: If the configured level or stream is invalid.
        """

        log_level = self._get_config_value('stream_logging', 'level')
        log_stream = self._get_config_value('stream_logging', 'stream')

        log_format = self._get_config_value('stream_logging', 'format')
        log_formater = Formatter(log_format)

        stream = stdout if log_stream == 'stdout' else stderr
        console_handler = StreamHandler(stream)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(log_formater)

        exception_filter = ExcludeExceptionsFilter()
        console_handler.addFilter(exception_filter)

        self._logger.addHandler(console_handler)

    def _configure_logrotate_handler(self, metadata_path):
        """
        Configures the RotatingFileHandler for log file rotation.
        - Retrieves the file path, logging level, maximum file size, and backup
        count from the configuration.
        - Adds the handler to the main logger.

        :param metadata_path: Path to the group metadata folder.

        :raises OSError: If the log directory cannot be created.
        """

        file_path = self._get_log_path(metadata_path)

        log_level = self._get_config_value('file_logging', 'level')
        backup_count = self._get_config_value('file_logging', 'backup_count')

        log_format = self._get_config_value('file_logging', 'format')
        log_formater = Formatter(log_format)

        max_size = self._get_config_value('file_logging', 'max_size')
        max_size = self._safe_parse_humanfriendly_size(max_size, 0)

        file_handler = RotatingFileHandler(
            file_path, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(log_formater)

        self._logger.addHandler(file_handler)

    # -------------------------------------------------------------------------
    # Auxiliary methods
    # -------------------------------------------------------------------------

    def _get_log_path(self, metadata_path):
        """
        Generates and returns the full path to the log file.
        - Combines the metadata folder with the 'logs' subdirectory.
        - Creates the directory if it does not exist.

        :return: Full path to the log file.
        :raises OSError: If the log directory cannot be created.
        """

        file_path = None

        log_base_path = path.join(metadata_path, 'logs')
        if not path.exists(log_base_path):
            self._mkdir(log_base_path)

        file_name = self._get_config_value('file_logging', 'file')
        file_path = path.join(log_base_path, file_name)

        return file_path

    def _mkdir(self, target_path):
        """
        Creates a directory at the specified path if it does not exist.

        :param target_path: Path to the directory to be created.
        :raises OSError: If an error occurs while creating the directory.
        """

        try:
            makedirs(target_path, exist_ok=True)
        except OSError as ex:
            message = f'Failed to create {target_path}. {ex}'
            raise OSError(message) from ex

    def _safe_parse_humanfriendly_size(self, value, default):
        """
        Safely converts a size string with units to bytes.
        - Uses humanfriendly.parse_size for conversion.
        - Returns a default value if an error occurs.

        :param value: String representing the size, e.g., "10M", "2GB".
        :param default: Default value to return in case of an error.
        :return: Size in bytes (int) or the default value.
        """

        try:
            return parse_size(value)
        except Exception:
            return default

    def _get_most_permissive_level(self):
        """
        Determines the most permissive logging level between stream_logging and
        file_logging.
        - Compares levels defined in the configuration.
        - Returns the level that allows the most output (DEBUG < INFO < WARNING
        < ERROR < CRITICAL).

        :return: The most permissive logging level as a string.
        """

        permisive_order = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

        stream_level = \
            self._get_config_value('stream_logging', 'level').upper()
        stream_level = \
            stream_level if stream_level in permisive_order else 'INFO'

        file_level = self._get_config_value('file_logging', 'level').upper()
        file_level = file_level if file_level in permisive_order else 'INFO'

        stream_order = permisive_order.index(stream_level)
        file_order = permisive_order.index(file_level)

        most_permisive_index = min(stream_order, file_order)

        return permisive_order[most_permisive_index]

    # -------------------------------------------------------------------------
    # Wrappers
    # -------------------------------------------------------------------------

    def _get_config_value(self, section, key):
        """
        Fetches a configuration value from the central configuration object.

        :param section: The name of the configuration section (e.g. "logging").
        :param key: The specific key within the section (e.g., "level").
        :return: The value associated with the provided section and key.
        :raises KeyError: If the section or key does not exist.
        """
        return self._config.get_value(section, key)

    # -------------------------------------------------------------------------
    # Message methods
    # -------------------------------------------------------------------------

    def abort(self, msg, exit_code=1, *args, **kwargs):
        """
        Logs a message with the ERROR level and terminates the application.
        - ERROR messages indicate serious issues that have caused a failure in
          part of the application.
        - This method logs the message and exits the application with the given
        exit code.

        :param msg: The message to log.
        :param exit_code: The exit code to use when terminating the application
                          (default is 1, indicating an error).
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.error(msg, *args, **kwargs)
        exit(exit_code)

    def debug(self, msg, *args, **kwargs):
        """
        Logs a message with the DEBUG level.
        - DEBUG messages are typically used for detailed diagnostic output.

        :param msg: The message to log.
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Logs a message with the INFO level.
        - INFO messages provide general operational information about the
        application's state.

        :param msg: The message to log.
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Logs a message with the WARNING level.
        - WARNING messages indicate potential issues or unexpected situations
        that do not stop the application.

        :param msg: The message to log.
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Logs a message with the ERROR level.
        - ERROR messages indicate serious issues that have caused a failure in
        part of the application.

        :param msg: The message to log.
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Logs a message with the CRITICAL level.
        - CRITICAL messages indicate severe errors that may cause the
        application to stop functioning.

        :param msg: The message to log.
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """
        Logs a message with a specified logging level.
        - This method allows for dynamic control over the log level used.

        :param level: The logging level (e.g., logging.DEBUG, logging.INFO).
        :param msg: The message to log.
        :param args: Additional positional arguments for string formatting.
        :param kwargs: Additional keyword arguments passed to the logger.
        """
        self.logger.log(level, msg, *args, **kwargs)

    def exception(self, exception_type, msg, *args, **kwargs):
        """
        Logs an error message and raises a specified exception type.

        :param exception_type: The exception class to raise (must be a subclass
                               of BaseException).
        :param msg: The error message to log.
        :param args: Positional arguments for string formatting in the message.
        :param kwargs: Additional keyword arguments passed to the logger.
        :raises exception_type: The specified exception with the formatted
                                message.
        """
        self.logger.error(msg, *args, **kwargs, exc_info=True)

        formatted_message = msg % args if args else msg
        raise exception_type(formatted_message)
