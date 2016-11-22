from rx import Observable
from rx.subjects import Subject

from transfernode.models.exceptions import (
    UploadAlreadyStartedException, UploadAlreadyFinishedException
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

        self._data = Subject()

    def get_data_stream(self) -> Observable:
        if self.upload_started:
            raise UploadAlreadyStartedException()
        return self._data.share()

    def send_data(self, data: bytes):
        if self.upload_finished:
            raise UploadAlreadyFinishedException()
        self._data.on_next(data)

    def cleanup(self):
        self._data.on_completed()
