from . import settings
from .channels import get_channel

from celery.task import task, chord


@task
def inline(name, mimetype, offset, limit, *args, **kwargs):
    datas = []

    channel = get_channel(name, *args, **kwargs)

    query = channel.get_query(offset, limit)

    for obj in query:
        datas.append([channel.format(column, obj)
                      for column in channel.columns])

    channel.write(datas, mimetype, offset, limit)

    return offset, limit


@task
def builder(name, mimetype, chunks=None, *args, **kwargs):
    if not chunks:
        chunks = settings.DATA_EXPORTER_CHUNKS_LENGTH

    return chord(generate_subtasks_builder(name, mimetype, chunks, *args, **kwargs))(compute.subtask(kwargs=dict({
        'name': name,
        'mimetype': mimetype
    }, **kwargs)))


@task
def compute(offsets, *args, **kwargs):
    name = kwargs.pop('name')
    mimetype = kwargs.pop('mimetype')

    channel = get_channel(name, *args, **kwargs)
    channel.combine(offsets, mimetype)


def generate_subtasks_builder(name, mimetype, chunks, *args, **kwargs):
    return [inline.subtask(args=(name, mimetype, i, chunks, ) + args, kwargs=kwargs)
            for i in xrange(0, get_channel(name, *args, **kwargs).get_count(), chunks)]
