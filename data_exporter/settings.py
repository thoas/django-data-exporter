import os

from django.conf import settings


DATA_EXPORTER_DIRECTORY = os.path.join(settings.MEDIA_ROOT, 'exports')

DATA_EXPORTER_CHANNELS = getattr(settings, 'DATA_EXPORTER_CHANNELS', {})

DATA_EXPORTER_CHUNKS_LENGTH = 100
