from data_exporter.base import Export

from data_exporter.tests.models import Poll


class PollExport(Export):
    filename = 'poll'
    directory = 'polls'
    columns = ('id', 'question')
    headers = ('id', 'question')

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
