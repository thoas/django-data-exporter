from data_exporter import settings

from celery.task import task, chord

from data_exporter.channels import get_channel


@task
def inline(name, mimetype, offset, limit):
    datas = []

    channel = get_channel(name)

    for obj in channel.get_query(offset, limit):
        datas.append([channel.format(column, obj)
                      for column in channel.columns])

    channel.write(datas, mimetype, offset, limit)

    return offset, limit


@task
def builder(name, mimetype, chunks=None):
    if not chunks:
        chunks = settings.DATA_EXPORTER_CHUNKS_LENGTH

    return chord(generate_subtasks_builder(name, mimetype, chunks))(compute.subtask(kwargs={
        'name': name,
        'mimetype': mimetype
    }))


@task
def compute(offsets, **kwargs):
    channel = get_channel(kwargs.get('name'))
    channel.combine(offsets, kwargs.get('mimetype'))


def generate_subtasks_builder(name, mimetype, chunks):
    return [inline.subtask((name, mimetype, i, chunks))
            for i in xrange(0, get_channel(name).get_count(), chunks)]
