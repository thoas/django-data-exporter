from data_exporter.base import Export

from data_exporter.tests.models import Poll


class PollExport(Export):
    filename = 'polls'
    columns = ('id', 'question')
    headers = ('id', 'question')

    def get_query(self, offset=None, limit=None):
        qs = Poll.objects.all()

        if offset and limit:
            return qs[offset:limit]

        if limit:
            return qs[:limit]

        if offset:
            return qs[offset:]

        return qs

    def get_count(self):
        return Poll.objects.count()
