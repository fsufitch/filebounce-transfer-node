from ipaddress import ip_address

from rx import Observable
from rx.subjects import BehaviorSubject, Subject

from transfernode.models.exceptions import (
    UploadAlreadyStartedException, UploadAlreadyFinishedException,
    MissingUploadChunkException
)
from transfernode.protobufs.clientmessage_pb2 import RecipientsData

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
        self.recipients = []
        self.recipients_updates = Subject()

        self.chunk_buffer = []
        self.next_chunk = 0

        self._data = Subject()

    def set_upload_started(self):
        if not self.upload_started:
            self.recipients_updates.on_completed()
        self.upload_started = True

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

    def add_recipient(self, ipv4: str=None, ipv6: str=None,
                      identity: str=None):
        if not (ipv4 or ipv6):
            raise TypeError('IPv4 or IPv6 address required')
        if ipv4 and ipv6:
            raise TypeError('Both IPv4 and IPv6 recipient addresses specified')

        recipient = RecipientsData.Recipient(ipv4=ipv4, ipv6=ipv6, identity=identity)
        self.recipients.append(recipient)
        print(self.recipients)
        self.recipients_updates.on_next(self.recipients)

    def cleanup(self):
        self._data.on_completed()
