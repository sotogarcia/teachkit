from .config import Config
from .logger import Logger
from .parser import CommandLineInterface

from os import path, makedirs, system as exec_cmd, listdir
from shutil import rmtree
from configparser import ConfigParser
from platform import system as get_osname
from pathvalidate import sanitize_filename
from re import sub as re_sub, match as re_match, IGNORECASE as RE_IGNORECASE
from unidecode import unidecode

MSG_NO_GROUP = 'The provided folder "%s" does not appear to belong to a group.'
MSG_MISSING_FOLDER = 'The %s folder does not exist and will be created.'
MSG_NO_STUDENTS_YET = 'There are no students in this group yet.'


class Base(object):

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(self):
        self._os_name = get_osname()

        self._cmd = CommandLineInterface()
        self._cwd = self._cmd.cwd

        self._config = Config()
        self._logger = Logger()

        # Only create group can be executed outside an existing group folder
        if not(self.target == 'group' and self.action == 'create'):
            self.ensure_within_the_group(raise_exception=True)

        item_id = self.arguments.get('id', None)
        if item_id and isinstance(item_id, int):
            self._id = item_id
        else:
            self._id = None

        name = self.arguments.get('name', None)
        if name and isinstance(name, str) and len(name) > 0:
            self._name = name.strip()
        else:
            self._name = None

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

    @property
    def arguments(self):
        return self._cmd

    @property
    def config(self):
        return self._config

    @property
    def target(self):
        return self._cmd.target

    @property
    def action(self):
        return self._cmd.action

    @property
    def group_path(self):
        if not path.exists(self._cwd):
            message = '%s does not exists.'
            self.exception(Exception, message, self._cwd)

        return self._cwd

    @group_path.setter
    def group_path(self, target_path):
        target_path = path.abspath(target_path)

        if not path.exists(target_path):
            message = '%s does not exists.'
            self.exception(Exception, message, target_path)

        self._cwd = target_path

    @property
    def resources_path(self):
        resources_folder = self.get_config_value('resources', 'folder')

        # Ensure the folder exists
        folder_path = path.join(self._cwd, resources_folder)
        if not path.exists(folder_path):
            self.warning(MSG_MISSING_FOLDER, 'resources')
            self._mkdir(folder_path)

        self._execute_cmd_attrib(folder_path, '+s')

        # Ensure the folder has a desktop.ini
        desktop_path = path.join(folder_path, 'desktop.ini')
        if not path.exists(desktop_path):
            resources_name = self.get_config_value('resources', 'name')
            resources_icon = self.get_config_value('resources', 'icon')
            resources_infotip = self.get_config_value('resources', 'infotip')
            self._create_desktop_ini(
                folder_path, resources_name, resources_icon,
                InfoTip=resources_infotip
            )

        return folder_path

    @property
    def metadata_path(self):
        metadata_folder = self.get_config_value('metadata', 'folder')

        folder_path = path.join(self._cwd, metadata_folder)
        if not path.exists(folder_path):
            self.error(MSG_NO_GROUP, folder_path)

        self._execute_cmd_attrib(folder_path, '+s')

        # Ensure the folder has a desktop.ini
        desktop_path = path.join(folder_path, 'desktop.ini')
        if not path.exists(desktop_path):
            metadata_name = self.get_config_value('metadata', 'name')
            metadata_icon = self.get_config_value('metadata', 'icon')
            metadata_infotip = self.get_config_value('metadata', 'infotip')
            metadata_clsid = self.get_config_value('metadata', 'clsid')
            self._create_desktop_ini(
                folder_path, metadata_name, metadata_icon,
                InfoTip=metadata_infotip, CLSID=metadata_clsid
            )
        return folder_path

    @property
    def config_path(self):
        metadata_path = self.metadata_path

        # Ensure the folder exists
        folder_path = path.join(metadata_path, 'config')
        if not path.exists(folder_path):
            self.warning(MSG_MISSING_FOLDER, 'configuration')
            self._mkdir(folder_path)

        return folder_path

    @property
    def unenrolled_path(self):
        metadata_path = self.metadata_path

        # Ensure the folder exists
        folder_path = path.join(metadata_path, 'unenrolled')
        if not path.exists(folder_path):
            self.warning(MSG_MISSING_FOLDER, 'unenrolled')
            self._mkdir(folder_path)

        return folder_path

    @property
    def logging_path(self):
        metadata_path = self.metadata_path

        # Ensure the folder exists
        folder_path = path.join(metadata_path, 'logs')
        if not path.exists(folder_path):
            self.warning(MSG_MISSING_FOLDER, 'log')
            self._mkdir(folder_path)

        return folder_path

    @property
    def student_paths(self):
        folders = []

        sources = listdir(self.group_path)
        if not sources:
            self.info(MSG_NO_STUDENTS_YET, 'log')
        else:
            for index, source in enumerate(sorted(sources)):
                full_path = path.abspath(path.join(self.group_path, source))
                if path.isdir(full_path) and source[0].isalpha():
                    folders.append(source)

        return folders

    # -------------------------------------------------------------------------
    # PRIVATE MAIN METHODS
    # -------------------------------------------------------------------------

    def _create_desktop_ini(self, base_path, name=None, icon=None, **kwargs):

        config = ConfigParser(strict=False, interpolation=None)
        config['.ShellClassInfo'] = {
            'ConfirmFileOp': 1
        }

        if name:
            config['.ShellClassInfo']['LocalizedResourceName'] = name

        if icon:
            config['.ShellClassInfo']['IconResource'] = icon

        for key, value in (kwargs or {}).items():
            config['.ShellClassInfo'][key] = value

        file_path = path.join(base_path, 'desktop.ini')
        try:
            self._execute_cmd_attrib(file_path, '-r -h -s')
            with open(file_path, 'w') as configfile:
                config.write(configfile)
            self.info('The desktop.ini file was written to %s', base_path)
            self._execute_cmd_attrib(file_path, '+h +s')
        except OSError as ex:
            message = 'Failed to write %s. %s'
            self.exception(OSError, message, file_path, ex)

    def _sanitize_filename(self, file_name, shorten=False):

        name = file_name[:].strip()

        reduce_spaces = self.get_config_value('naming', 'reduce_spaces')
        if reduce_spaces:
            name = self._spaces(name)

        to_ascii = self.get_config_value('naming', 'unidecode')
        if to_ascii:
            name = unidecode(name)

        underscore = self.get_config_value('naming', 'underscore')
        if underscore:
            name = name.replace(' ', '_')

        if shorten:
            max_len = self.get_config_value('naming', 'max_len')
            name = self._limit_words(name)
        else:
            max_len = 255
        name = sanitize_filename(name, platform="auto", max_len=max_len)

        merge = self.get_config_value('naming', 'merge_underscores')
        if merge:
            name = re_sub(r'_+', r'_', name)

        convert_case = self.get_config_value('naming', 'convert_case')
        if(convert_case.lower() in ('lower', 'upper', 'title')):
            name = getattr(name, convert_case)()

        message = 'The given name "%s" was sanitized to "%s"'
        self.debug(message, file_name, name)

        return name

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------

    def ensure_within_the_group(self, raise_exception=True):
        metadata_folder = self.get_config_value('metadata', 'folder')
        folder_path = path.join(self._cwd, metadata_folder)
        result = path.exists(folder_path)

        if not result and raise_exception:
            message = 'Request outside the group folder "%s"'
            self.exception(Exception, message, self._cwd)

        return result

    # -------------------------------------------------------------------------
    # Auxiliary methods
    # -------------------------------------------------------------------------

    def _spaces(self, target):
        target = str(target or '')
        target = target.strip()

        return re_sub(' +', ' ', target)

    def _safe_cast(self, value, to_type, default=None):
        """ Performs a safe cast between `val` type to `to_type`

        @param val: value will be converted
        @param to_type: type of value to return
        @param default: value will be returned if conversion fails

        @return result of conversion or given default
        """

        try:
            return to_type(value)
        except (ValueError, TypeError) as ex:
            message = ('The value "%s" could not be converted to %s. '
                       'Default value "%s" was used instead. System says: %s.')
            self.warning(message, value, to_type, default, ex)
            return default

    def _limit_words(self, source):
        num_words = self.get_config_value('naming', 'num_words')
        min_word_length = self.get_config_value('naming', 'min_word_length')

        parts = []
        count = 0
        for part in (source or '').split(' '):
            if not part:  # empty string
                parts.append(' ')  # Preserve spaces
            else:
                parts.append(part)
                count += len(part) >= min_word_length
                if count == num_words:
                    break

        return ' '.join(parts)

    # -------------------------------------------------------------------------
    # Wrappers
    # -------------------------------------------------------------------------

    @staticmethod
    def _unidecode(target):
        return target and unidecode(target)

    def _mkdir(self, target_path):
        try:
            makedirs(target_path, exist_ok=True)
        except OSError as ex:
            message = 'Failed to create %s. %s'
            self.exception(OSError, message, target_path, ex)

    def _rmtree(self, target_path):
        try:
            rmtree(target_path)
        except OSError as ex:
            message = 'Failed to remove %s. %s'
            self.exception(OSError, message, target_path, ex)

    def get_config_value(self, section, key):
        return self._config.get_value(section, key)

    def set_config_value(self, section, key, value):
        return self._config.set_value(section, key, value)

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
        self.logger.abort(msg, exit_code=1, *args, **kwargs)

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
        self.logger.exception(exception_type, msg, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Windows commands
    # -------------------------------------------------------------------------

    def _execute_cmd(self, command, assert_success=True):
        exit_code = -1

        if self._os_name != "Windows":
            return exit_code

        try:
            exit_code = exec_cmd(command)
            if assert_success and exit_code != 0:
                message = 'Command failed with exit code %s: %s'
                self.exception(OSError, message, exit_code, command)
        except Exception as ex:
            message = 'Failed to execute  %s. %s'
            self.exception(Exception, message, command, ex)

        return exit_code

    def _execute_cmd_attrib(self, target_path, attrib_list):
        exit_code = -1

        if self._os_name != "Windows" or not path.exists(target_path):
            return exit_code

        regex_pattern = r'[+-][RASHOIXVPUB]'
        attributes = attrib_list[:]

        if isinstance(attributes, str):
            attributes = attributes.strip()
            attributes = re_sub(' +', ' ', attributes)
            attributes = attributes.split(' ')

        for attribute in attributes:
            if not re_match(regex_pattern, attribute, RE_IGNORECASE):
                message = 'Invalid attribute  %s.'
                self.exception(Exception, message, attribute)

        attributes = ' '.join(attributes)

        if path.exists(target_path):
            command = f'attrib {attributes} "{target_path}"'
            exit_code = self._execute_cmd(command, assert_success=True)

        return exit_code
