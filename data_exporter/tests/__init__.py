from mock import patch, MagicMock

import os

from datetime import datetime

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from data_exporter import channels
from data_exporter.base import Export
from data_exporter.tests.exports import PollExport
from data_exporter import settings
from data_exporter.signals import export_done


class ChannelTests(TestCase):
    def test_get_channel(self):
        channel = channels.get_channel('polls')

        self.assertTrue(isinstance(channel, PollExport))

    def test_get_unknown_channel(self):
        self.assertRaises(ImproperlyConfigured, channels.get_channel, 'random')

    def test_import_module_fails_channel(self):
        settings.DATA_EXPORTER_CHANNELS['choices'] = 'data_exporter.tests.exports.ChoiceExport'

        self.assertRaises(ImproperlyConfigured, channels.get_channel, 'choices')


class ExportTests(TestCase):
    def setUp(self):
        self.channel = channels.get_channel('polls')

    def test_format(self):
        self.assertEqual(self.channel.format('key', 'value'), 'value')

    def test_get_file_root(self):
        self.assertEqual(self.channel.get_directory(), settings.DATA_EXPORTER_DIRECTORY)

        with patch.object(Export, 'get_formatted_date') as get_formatted_date_method:
            date_format = datetime.now().strftime(self.channel.date_format)

            get_formatted_date_method.return_value = date_format

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
        with patch('__builtin__.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=file)

            data = [[1, 'test']]

            self.channel.write(data, 'csv')

            file_handle = mock_open.return_value.__enter__.return_value

            file_handle.write.assert_called_with(self.channel._generate_dataset(data).csv)

    def test_write_signals_sent(self):
        with patch('__builtin__.open', create=True) as mock_open:
            def callback(sender, **kwargs):
                self.export = True

            export_done.connect(callback)

            self.export = False

            mock_open.return_value = MagicMock(spec=file)

            data = [[1, 'test']]

            self.channel.write(data, 'csv')

            self.assertTrue(self.export)
