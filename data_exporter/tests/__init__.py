from mock import patch, MagicMock

import os

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from data_exporter import channels
from data_exporter.tests.exports import PollExport
from data_exporter import settings


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
        self.assertEqual(self.channel.get_file_root('xls'),
                         os.path.join(self.channel.get_directory(),
                                      self.channel.filename + '.xls'))

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
