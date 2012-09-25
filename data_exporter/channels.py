from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from data_exporter import settings


def get_channel(name):
    try:
        lookup_label = settings.DATA_EXPORTER_CHANNELS[name]
    except KeyError:
        raise ImproperlyConfigured("settings.DATA_EXPORTER_CHANNELS not configured correctly for %r" % name)
    else:
        try:
            mod_path, cls_name = lookup_label.rsplit('.', 1)
            mod = import_module(mod_path)
            channel_class = getattr(mod, cls_name)
        except (AttributeError, ImportError) as e:
            raise ImproperlyConfigured(
                "Could not find channel '%s': %s" % (name, e))
        else:
            return channel_class()
