import django.dispatch

export_done = django.dispatch.Signal(providing_args=['file'])
combine_done = django.dispatch.Signal(providing_args=['file'])
