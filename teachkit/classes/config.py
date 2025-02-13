# -*- coding: utf-8 -*-
from .parser import CommandLineInterface

from configparser import ConfigParser, NoOptionError, NoSectionError
from os import getcwd, path, environ

_LOG_STREAM_FORMAT = '%(levelname)s - %(message)s'
_LOG_FILE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Config(object):

    # -------------------------------------------------------------------------
    # Singleton
    # -------------------------------------------------------------------------

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    _app = None

    def __init__(self):
        if self._app is None:
            self._update_appfrom_defaults()
            self._udpate_from_app()

            cmd = CommandLineInterface()
            self._update_appfrom_group(cmd.cwd)

            self._update_appfrom_environment()
            self._update_appfrom_command_line()

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def app(self):
        return self._app

    # -------------------------------------------------------------------------
    # Set defaults
    # -------------------------------------------------------------------------

    def _update_appfrom_defaults(self):
        self._app = {
            'resources': {
                'folder': '~resources',
                'name': '.:[ Resources ]:.',
                'icon': '%SystemRoot%\\system32\\imageres.dll,-115',
                'infotip': 'Shared folder with the provided material.',
            },

            'metadata': {
                'folder': '.metadata',  # Cannot be obtained from the group
                'name': '.:[ Details ]:.',
                'icon': '%SystemRoot%\\system32\\imageres.dll,-186',
                'infotip': 'Information relating to training management.',
                'clsid': '{BB06C0E4-D293-4F75-8A90-CB05B6477EEE}',
            },

            'naming': {
                'reduce_spaces': True,
                'underscore': True,
                'merge_underscores': True,
                'max_len': 32,
                'num_words': 32,
                'min_word_length': 32,
                'convert_case': 'lower',
                'unidecode': True
            },

            'stream_logging': {
                'level': 'ERROR',
                'stream': 'stderr',
                'format': _LOG_STREAM_FORMAT,
            },

            'file_logging': {
                'level': 'INFO',
                'file': 'teachkit.log',
                'max_size': '10M',
                'backup_count': '5',
                'format': _LOG_FILE_FORMAT,
            }

        }

    # -------------------------------------------------------------------------
    # Update values from different sources
    # -------------------------------------------------------------------------

    def _udpate_from_app(self):
        self_path = path.dirname(__file__)
        ini_path = path.join(self_path, '..', 'config', 'default.ini')
        ini_path = path.abspath(ini_path)

        if path.exists(ini_path):
            self._load_from_ini(ini_path)

    def _update_appfrom_group(self, group_path=None):
        base_path = group_path[:] or getcwd()

        ini_path = path.join(base_path, '.metadata', 'default.ini')
        ini_path = path.abspath(ini_path)

        if path.exists(ini_path):
            self._load_from_ini(ini_path)

    def _update_appfrom_environment(self):
        for section, keys in self._app.items():

            for key in keys:

                env_var_name = f'{section.upper()}_{key.upper()}'
                if env_var_name not in environ:
                    continue

                current_type = type(self._app[section][key])
                env_value = environ[env_var_name]
                env_value = self._convert_env_value(env_value, current_type)
                if env_value is not None:
                    self._app[section][key] = env_value

    def _update_appfrom_command_line(self):
        cmd = CommandLineInterface()
        args = cmd.args_dict

        num_words = args.get('num_words', False)
        if isinstance(num_words, int) and num_words >= 0:
            self.set_value('naming', 'num_words', num_words)

        min_word_length = args.get('min_word_length', False)
        if isinstance(min_word_length, int) and min_word_length >= 0:
            self.set_value('naming', 'min_word_length', num_words)

    # -------------------------------------------------------------------------
    # Access methods
    # -------------------------------------------------------------------------

    def get_value(self, section, key):
        try:
            return self._app[section][key]
        except KeyError as e:
            message = f'Error retrieving "{key}" from section "{section}": {e}'
            raise Exception(message) from e

    def set_value(self, section, key, value):
        if section not in self._app:
            self._app[section] = {}

        self._app[section][key] = value

    # -------------------------------------------------------------------------
    # Auxiliary methods
    # -------------------------------------------------------------------------

    def _load_from_ini(self, ini_path):
        parser = ConfigParser(strict=False, interpolation=None)
        parser.read(ini_path)

        for section in parser.sections():
            if section not in self._app:
                continue

            for key, value in parser[section].items():
                if key not in self._app[section]:
                    continue

                current_value = self._app[section][key]
                current_type = type(current_value)
                value = self.safe_ini_get_value(
                    parser, section, key, current_type
                )
                if value:
                    self._app[section][key] = value

    def _convert_env_value(self, value, expected_type):
        try:
            if expected_type == bool:
                return value.lower() in ['1', 'true', 'yes', 'on']
            elif expected_type == int:
                return int(value)
            elif expected_type == float:
                return float(value)
            else:
                return value
        except ValueError:
            return None

    @staticmethod
    def safe_ini_get_value(parser, section, key, expected_type):
        try:
            if expected_type == bool:
                return parser.getboolean(section, key)
            elif expected_type == int:
                return parser.getint(section, key)
            elif expected_type == float:
                return parser.getfloat(section, key)
            else:
                return parser.get(section, key)
        except (ValueError, NoOptionError, NoSectionError):
            return None

    @staticmethod
    def write_to_ini_file(ini_path, data):
        parser = ConfigParser(strict=False, interpolation=None)

        for section_name, section_data in (data or {}).items():
            parser[section_name] = {}
            for key_name, key_value in (section_data or {}).items():
                parser[section_name][key_name] = str(key_value)

        with open(ini_path, 'w') as configfile:
            parser.write(configfile)
