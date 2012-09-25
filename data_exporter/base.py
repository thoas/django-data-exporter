import os
import tablib

from data_exporter import settings


class Export(object):
    columns = ()
    headers = ()
    filename = None

    def get_query(self, *args, **kwargs):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError

    def format(self, key, value):
        return value

    def get_directory(self):
        return settings.DATA_EXPORTER_DIRECTORY

    def get_file_root(self, mimetype):
        return os.path.join(self.get_directory(),
                            self.filename + '.%s' % mimetype)

    def write(self, data, mimetype):
        data = tablib.Dataset(*data, headers=self.headers)

        with open(self.get_file_root(mimetype), 'wb') as file:
            file.write(getattr(data, mimetype))
