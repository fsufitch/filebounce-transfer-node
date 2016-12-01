from rx import Observable
from rx.subjects import Subject

from transfernode.models.exceptions import (
    UploadAlreadyStartedException, UploadAlreadyFinishedException,
    MissingUploadChunkException
)


class TransferSession:
    def __init__(self, id):
        self.id = id
        self.filename = None
        self.mimetype = None
        self.bytes_size = None

        self.authenticated = False
        self.upload_started = False
        self.upload_finished = False
        self.bytes_progress = None

        self.chunk_buffer = []
        self.next_chunk = 0

        self._data = Subject()

    def get_data_stream(self) -> Observable:
        if self.upload_started:
            raise UploadAlreadyStartedException()
        return self._data.share()

    def enqueue_data(self, order: int, data: bytes):
        if self.upload_finished:
            raise UploadAlreadyFinishedException()
        self.chunk_buffer.append( (order, data) )

    def flush(self):
        sorted_order_chunks = sorted(self.chunk_buffer)
        for order in [x[0] for x in sorted_order_chunks]:
            if self.next_chunk != order:
                raise MissingUploadChunkException('Expected: %d; Got: %d' %
                    (self.next_chunk, order))
            self.next_chunk += 1

        for chunk in [x[1] for x in sorted_order_chunks]:
            self._data.on_next(chunk)
        self.chunk_buffer = []

    def cleanup(self):
        self._data.on_completed()
