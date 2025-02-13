from .base import Base

from os import getcwd, path


class Group(Base):

    def __init__(self):
        super(Group, self).__init__()

        self._code = self.arguments.get('code', None)

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    def create(self):
        base_path = path.abspath(self._cwd)

        if not path.exists(base_path):
            path_head, path_tail = path.split(path.normpath(base_path))
            if path_tail:
                folder_name = self._sanitize_filename(path_tail, shorten=False)
                base_path = path.join(path_head, folder_name)

        self._mkdir(base_path)
        if not self.group_path:
            self.exception('Something was wrong! Group folder is missing.')

        resources_folder = self.get_config_value('resources', 'folder')
        resources_path = path.join(base_path, resources_folder)
        self._mkdir(resources_path)
        if not self.resources_path:
            self.error('Something was wrong! Resources folder is missing.')

        metadata_folder = self.get_config_value('metadata', 'folder')
        metadata_path = path.join(base_path, metadata_folder)
        self._mkdir(metadata_path)
        if not self.metadata_path:
            self.exception('Something was wrong! Metadata folder is missing.')

        config_path = path.join(metadata_path, 'config')
        self._mkdir(config_path)
        if not self.config_path:
            self.error('Something was wrong! Configuration folder is missing.')

        logs_path = path.join(metadata_path, 'logs')
        self._mkdir(logs_path)
        if not self.logging_path:
            self.error('Something was wrong! Logging folder is missing.')

        unenrolled_path = path.join(metadata_path, 'unenrolled')
        self._mkdir(unenrolled_path)
        if not self.unenrolled_path:
            self.error('Something was wrong! Unenrolled folder is missing.')

        self.group_path = base_path

        group_name = self._make_group_name()
        self._create_desktop_ini(base_path, name=group_name)
        self._execute_cmd_attrib(base_path, '+s')

        self.update()

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def read(self):
        self.ensure_within_the_group(raise_exception=True)

        # for k, v in self.config_group.items():
        #     print(f'{k.title().ljust(10, ".")}: {v}')

        print(f'{"Folders".ljust(10, ".")}: {len(self.student_paths)}')

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(self):
        values = {
            'group': {
                # ...
            }
        }

        if self._name:
            values['group']['name'] = self._name

        if self._id:
            values['group']['id'] = self._id

        if self._code:
            values['group']['code'] = self._code

        base_path = self.config_path
        file_path = path.join(base_path, 'group.ini')

        try:
            self.config.write_to_ini_file(file_path, values)
        except Exception as ex:
            message = ('Fail to write the group configuration in "%s". '
                       'System says: %s.')
            self.error(message, repr(ex))

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    def delete(self):
        current_path = getcwd()
        group_path = self.group_path

        if current_path.startswith(group_path):
            message = 'You must leave the group directory before deleting it'
            self.exception(Exception, message)

        try:
            self.logger.close()
            self._rmtree(group_path)
        except Exception as ex:
            message = ('Failed to delete directory "%s". System says: %s')
            raise Exception(message % (group_path, repr(ex)))

    def _make_group_name(self):
        return self._name != '.' and self._name or path.basename(self._cwd)
