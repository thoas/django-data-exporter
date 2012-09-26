import os
import tablib
from datetime import datetime

from data_exporter import settings
from data_exporter.signals import export_done


class Export(object):
    columns = ()
    headers = ()
    filename = None

    date_format = '%Y-%m-%d'
    filename_format = '%(filename)s-%(date)s'

    def get_query(self, *args, **kwargs):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError

    def format(self, key, value):
        return value

    def get_directory(self):
        return settings.DATA_EXPORTER_DIRECTORY

    def get_file_root(self, mimetype):
        filename_format = self.filename_format % {
            'filename': self.filename,
            'date': self.get_formatted_date()
        }

        return os.path.join(self.get_directory(),
                            filename_format + '.%s' % mimetype)

    def get_formatted_date(self):
        return datetime.now().strftime(self.date_format)

    def write(self, data, mimetype):
        data = self._generate_dataset(data)

        with open(self.get_file_root(mimetype), 'wb') as file:
            file.write(getattr(data, mimetype))

            export_done.send(sender=self, file=file)

    def _generate_dataset(self, data):
        return tablib.Dataset(*data, headers=self.headers)
