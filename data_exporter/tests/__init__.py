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
