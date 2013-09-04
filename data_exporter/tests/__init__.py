from mock import patch

import os
import shutil

from datetime import datetime

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from data_exporter import channels, tasks, settings
from data_exporter.base import Export
from data_exporter.tests.models import Poll
from data_exporter.signals import export_done, combine_done


class BaseTests(TestCase):
    def setUp(self):
        self.channel = channels.get_channel('polls')
        self.storage = self.channel.storage

        try:
            shutil.rmtree(self.storage.location)
        except OSError:
            pass


class ChannelTests(BaseTests):
    def test_get_unknown_channel(self):
        self.assertRaises(ImproperlyConfigured, channels.get_channel, 'random')

    def test_import_module_fails_channel(self):
        settings.DATA_EXPORTER_CHANNELS['choices'] = 'data_exporter.tests.exports.ChoiceExport'

        self.assertRaises(ImproperlyConfigured, channels.get_channel, 'choices')


class ExportTests(BaseTests):
    def test_format(self):
        obj = type('lamdbaobject', (object,), {'key': 'value'})()

        self.assertEqual(self.channel.format('key', obj), 'value')

    def test_get_file_root(self):
        with patch.object(Export, 'get_formatted_date') as get_formatted_date_method:
            date_format = datetime.now().strftime(self.channel.date_format)

            get_formatted_date_method.return_value = date_format

            self.assertEqual(self.channel.get_directory(), os.path.join(self.channel.directory, date_format))

            self.assertEqual(self.channel.get_file_root('xls'),
                             os.path.join(self.channel.get_directory(),
                                          self.channel.filename_format % {
                                              'filename': self.channel.filename,
                                              'date': date_format
                                          } + '.xls'))

    def test_generate_dataset(self):
        dataset = self.channel._generate_dataset([
            [1, 'test']
        ])

        self.assertEqual(dataset.headers, list(self.channel.headers))

    def test_write(self):
        data = [[1, 'test']]

        self.channel.write(data, 'csv')

        file_root = self.channel.get_file_root('csv')

        self.assertTrue(self.storage.exists(file_root))

    def test_export_signals_sent(self):
        def callback(sender, **kwargs):
            self.export = True

        export_done.connect(callback)

        self.export = False

        data = [[1, 'test']]

        self.channel.write(data, 'csv')

        self.assertTrue(self.export)

    def test_combine_signals_sent(self):
        def callback(sender, **kwargs):
            self.export = True

        combine_done.connect(callback)

        self.export = False

        tasks.inline('polls', 'csv', 0, 100)  # NOQA

        self.channel.combine(((0, 100),), 'csv')

        self.assertTrue(self.export)


class TasksTests(BaseTests):
    length = 1000

    def setUp(self):
        super(TasksTests, self).setUp()

        for i in xrange(self.length):
            Poll.objects.create(question='Fake question n.%d' % i)

    def test_inline_task(self):
        tasks.inline('polls', 'csv', 0, 100)  # NOQA

        file_root = self.channel.get_file_root('csv', 0, 100)

        file = self.storage.open(file_root)

        lines = file.readlines()

        self.assertEqual(len(lines), 101)

        self.assertEqual(len(lines[0].split(',')), len(channels.get_channel('polls').columns))

    def test_builder_task(self):
        self.assertEqual(len(tasks.generate_subtasks_builder('polls', 'csv', 100)), 10)
