from itertools import chain

from celery.task import task, chord

from data_exporter.channels import get_channel


@task
def inline(name, offset, limit):
    datas = []

    channel = get_channel(name)

    for obj in channel.get_query(offset, limit):
        datas.append([channel.format(column, getattr(obj, column))
                      for column in channel.columns])

    return datas


@task
def builder(name, mimetype, chunks=100):
    return chord(generate_subtasks_builder(name, chunks))(compute.subtask(kwargs={
        'name': name,
        'mimetype': mimetype
    }))


@task
def compute(data_list, **kwargs):
    channel = get_channel(kwargs.get('name'))

    channel.write(list(chain.from_iterable(data_list)),
                  kwargs.get('mimetype'))


def generate_subtasks_builder(name, chunks):
    return [inline.subtask((name, i, i + chunks))
            for i in xrange(chunks, get_channel(name).get_count(), chunks)]
