from .base import Base
from os import path, listdir, makedirs
from datetime import datetime
from shutil import copytree, copy2

# STUDENT_ICON = '%SystemRoot%\\system32\\imageres.dll,-123'


class Student(Base):

    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)

        value = kwargs.get('num_words', None)
        self._num_words = value if isinstance(value, int) else 2

        value = kwargs.get('min_word_length', None)
        self._min_word_length = value if isinstance(value, int) else 3

    def create(self):
        self.ensure_within_the_group(raise_exception=True)

        if not self._name:
            raise Exception('The name is required to create new student.')

        base_name = self._make_folder_name()
        base_path = path.join(self._cwd, base_name)
        self._mkdir(base_path)
        self._execute_cmd_attrib(base_path, '+s')

        student_name = self._limit_words(self._name)
        self._create_desktop_ini(base_path, student_name.title())

    def read(self):
        self.ensure_within_the_group(raise_exception=True)

        folders = self.student_paths
        if not folders:
            self._print('There are no students in this group yet.')
        else:
            lines = []
            sizes = [0, 0, 0, 0, 0, 0]

            fields = ['P', 'C. date', 'D', 'A. date', 'A. time', 'Name']
            lines.append(fields)
            self._update_line_sizes(sizes, fields)

            for index, folder in enumerate(sorted(folders)):
                full_path = path.abspath(path.join(self.group_path, folder))

                cdt = path.getctime(full_path)
                cdt = datetime.fromtimestamp(cdt)

                adt = path.getatime(full_path)
                adt = datetime.fromtimestamp(adt)

                days = self._date_diff(cdt, adt)

                cdate = cdt.strftime('%Y-%m-%d')
                adate = adt.strftime('%Y-%m-%d')
                atime = adt.strftime('%H:%M:%S')

                fields = [index, cdate, days, adate, atime, folder]
                self._update_line_sizes(sizes, fields)

                lines.append(fields)

            separator = ['-' * size for size in sizes]
            lines.insert(1, separator)

            for pos, line in enumerate(lines):
                args = [
                    self._adjust(line[0], sizes[0], fill=True),
                    self._adjust(line[1], sizes[1]),
                    self._adjust(line[2], sizes[2]),
                    self._adjust(line[3], sizes[3]),
                    self._adjust(line[4], sizes[4]),
                    self._adjust(line[5], sizes[5]),
                ]

                self._print('{}  {}  {}  {}  {}  {}', *args)

    def update(self):
        folders = listdir(self.group_path)
        if not folders:
            self._print('There are no students in this group yet.')
        else:
            resources_path = self.resources_path
            for index, folder in enumerate(sorted(folders)):
                dest_path = path.abspath(path.join(self.group_path, folder))
                if path.isdir(dest_path) and folder[0].isalpha():
                    self._copy_folder(
                        resources_path, dest_path, overwrite=self._force)

    def delete(self):

        base_name = self._make_folder_name()
        base_path = path.join(self._cwd, base_name)

        self._rmtree(base_path)
        self._print(f'Student "{self._name}" folder has been removed.')

    @staticmethod
    def _update_line_sizes(sizes, fields):
        for index, field in enumerate(fields):
            sizes[index] = max(sizes[index], len(str(field)))

    @staticmethod
    def _adjust(value, size, fill=False):
        if isinstance(value, int):
            if fill:
                value = str(value).zfill(size)
            else:
                value = str(value).rjust(size)
        else:
            value = str(value).ljust(size)

        return value

    @staticmethod
    def _date_diff(date_start, date_stop):
        if isinstance(date_start, datetime):
            date_start = date_start.date()

        if isinstance(date_stop, datetime):
            date_stop = date_stop.date()

        delta = date_stop - date_start

        return abs(delta.days)

    @classmethod
    def _copy_folder(cls, source, target, drop_dest=False, overwrite=False):
        if not path.exists(source):
            message = f'Source folder "{source}" does not exist.'
            raise FileNotFoundError(message)

        try:

            if not path.exists(target):
                makedirs(target)

            for item in listdir(source):
                src_path = path.join(source, item)
                dest_path = path.join(target, item)

                if path.isdir(src_path):
                    if not path.exists(dest_path):
                        copytree(src_path, dest_path)
                    else:
                        cls._copy_folder(src_path, dest_path)
                elif item == 'desktop.ini':
                    pass
                elif not overwrite and path.exists(dest_path):
                    pass
                else:
                    copy2(src_path, dest_path)

        except Exception as ex:
            message = f'Failed to copy {source} to {target}. {ex}'
            raise Exception(message) from ex

    def _make_folder_name(self):
        base_name = self._limit_words(self._name)
        base_name = self._sanitize_filename(base_name)
        base_name = self._unidecode(base_name)
        base_name = base_name.lower()

        return base_name
