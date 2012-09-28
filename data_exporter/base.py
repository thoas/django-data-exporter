import os
import tablib

from datetime import datetime

from data_exporter import settings
from data_exporter.signals import export_done, combine_done


class Export(object):
    columns = ()
    headers = ()
    filename = None
    directory = None

    date_format = '%Y/%m/%d'
    filename_format = '%(filename)s'

    def get_query(self, *args, **kwargs):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError

    def format(self, key, obj):
        return getattr(obj, key)

    def get_directory(self):
        directory_path = os.path.join(settings.DATA_EXPORTER_DIRECTORY,
                                      self.directory, self.get_formatted_date())

        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path)
            except OSError:
                pass

        return directory_path

    def get_filename_format(self):
        return self.filename_format % {
            'filename': self.filename,
        }

    def get_file_root(self, mimetype, offset=None, limit=None):
        filename_format = self.get_filename_format()

        extension = '.%s' % mimetype

        chunk = ''

        if not offset is None and not limit is None:
            chunk = '_%s_%s' % (offset, limit)

        return os.path.join(self.get_directory(),
                            filename_format + chunk + extension)

    def get_formatted_date(self):
        return datetime.now().strftime(self.date_format)

    def write(self, data, mimetype, offset=None, limit=None, signal=True):
        dataset = self._generate_dataset(data)

        self.write_dataset(dataset, mimetype, offset=offset, limit=limit, signal=signal)

    def write_dataset(self, dataset, mimetype, offset=None, limit=None, signal=True):
        with open(self.get_file_root(mimetype, offset, limit), 'wb') as file:
            file.write(getattr(dataset, mimetype))

            if signal:
                export_done.send(sender=self, file=file)

            file.truncate()

    def _generate_dataset(self, data):
        return tablib.Dataset(*data, headers=self.headers)

    def combine(self, offsets, mimetype, signal=True):
        file_root = self.get_file_root(mimetype)

        with open(file_root, 'wb') as file:
            for i, current_offset in enumerate(offsets):
                offset, limit = current_offset

                with open(self.get_file_root(mimetype, offset, limit)) as chunk_file:
                    itr = chunk_file.xreadlines()
                    if i != 0:
                        next(itr)

                    for line in itr:
                        file.write(line)
            if signal:
                combine_done.send(sender=self, file=file)
