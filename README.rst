django-data-exporter
====================

django-data-exporter is a simple Django application to export asynchronously
your data from your models.

It's based on Celery_ (>= 2.3) to use `Chords <http://celery.github.com/celery/userguide/tasksets.html#chords>`_ and tablib_ to export your data in multiple formats.

Installation
------------

1. Either check out the package from GitHub_ or it pull from a release via PyPI ::

       pip install django-data-exporter

2. Configure your Django project to use `djcelery <http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html>`_

3. Add 'data_exporter' to your ``INSTALLED_APPS`` ::

       INSTALLED_APPS = (
           'data_exporter',
       )

Utilisation
-----------

django-data-exporter uses channels to discover your exports and to transfer them
to celery. So let's say you have the following model in a ``polls`` application ::

    # polls/models.py
    from django.db import models


    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

        def __unicode__(self):
            return self.question


Now, you want to define your first exporter right? Create a ``exports.py`` file
in your ``polls`` application and extend ``Export`` to build your own Exporter ::

    # polls/exports.py
    from data_exporter.base import Export

    from polls.models import Poll


    class PollExport(Export):
        filename = 'poll'
        columns = ('id', 'question')
        headers = ('id', 'question')
        directory = 'polls'

        def get_query(self, offset=None, limit=None):
            qs = Poll.objects.all()

            if not offset is None and not limit is None:
                return qs[offset:limit]

            elif limit:
                return qs[:limit]

            elif offset:
                return qs[offset:]

            return qs

        def get_count(self):
            return Poll.objects.count()


Final step is to register this exporter in ``DATA_EXPORTER_CHANNELS`` in your
Django settings ::

    DATA_EXPORTER_CHANNELS = {
        'polls': 'polls.exports.PollExport'
    }


You can now use the celery tasks provided by django-data-exporter as so ::

    from data_exporter.tasks import builder
    builder.delay('polls', 'csv')

First parameter is the name of your channel and second parameter is the format
wanted.

As said before, we use the beautiful tablib_ library to export your data,
so as you may understood we support all formats provided by this library.

Configuration
-------------

``DATA_EXPORTER_CHANNELS``
..........................

All your registered channels.

``DATA_EXPORTER_DIRECTORY``
...........................

The directory used to export your data.

.. _Celery: http://celeryproject.org/
.. _GitHub: https://github.com/thoas/django-data-exporter
.. _tablib: http://docs.python-tablib.org/en/latest/index.html
