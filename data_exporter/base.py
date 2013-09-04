import os
import tablib

from datetime import datetime

from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile

from . import settings
from .signals import export_done, combine_done


class Export(object):
    columns = ()
    headers = ()
    filename = None
    directory = None

    date_format = '%Y/%m/%d'
    filename_format = '%(filename)s'

    def __init__(self, *args, **kwargs):
        storage_class = get_storage_class(kwargs.pop('storage_class',
                                                     settings.DATA_EXPORTER_STORAGE_CLASS))

        self.storage = kwargs.pop('storage',
                                  storage_class(location=settings.DATA_EXPORTER_DIRECTORY))

        self.args = args
        self.kwargs = kwargs

    def get_query(self, *args, **kwargs):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError

    def format(self, key, obj):
        value = getattr(obj, key)

        if callable(value):
            return unicode(value())

        return unicode(value)

    def get_directory(self):
        return os.path.join(self.directory, self.get_formatted_date())

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
        self.pre_export(dataset, mimetype, offset=offset, limit=limit)

        file_root = self.get_file_root(mimetype, offset, limit)

        self.storage.save(file_root, ContentFile(getattr(dataset, mimetype)))

        if signal:
            export_done.send(sender=self, file=file)

        self.post_export(file, dataset, mimetype, offset=offset, limit=limit)

    def _generate_dataset(self, data):
        return tablib.Dataset(*data, headers=self.headers)

    def combine(self, offsets, mimetype, signal=True):
        self.pre_combine(offsets, mimetype)

        file_root = self.get_file_root(mimetype)

        parts = []

        for i, current_offset in enumerate(offsets):
            offset, limit = current_offset

            with self.storage.open(self.get_file_root(mimetype, offset, limit)) as file:

                for chunk in file.chunks():
                    parts.append(chunk)

        self.storage.save(file_root, ContentFile(''.join(parts)))

        if signal:
            combine_done.send(sender=self, file=file)

        self.post_combine(file, offsets, mimetype)

    def pre_export(self, dataset, mimetype, offset=None, limit=None):
        pass

    def post_export(self, file, dataset, mimetype, offset=None, limit=None):
        pass

    def pre_combine(self, offsets, mimetype):
        pass

    def post_combine(self, file, offsets, mimetype):
        pass
