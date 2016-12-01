from rx import Observable, Observer

from transfernode.config import TransferNodeConfiguration
from transfernode.models.exceptions import DataSizeMismatchException
from transfernode.models.session import TransferSession
from transfernode.protobufs.clientmessage_pb2 import (
    UploadData, TransferNodeToClientMessage, ProgressData, ErrorData
)
from transfernode.util import make_timestamp


class UploadController:
    def __init__(self, session: TransferSession,
                 incoming: Observable, outgoing: Observer):
        self.incoming = incoming
        self.outgoing = outgoing
        self.session = session

        config = TransferNodeConfiguration.instance()
        self.chunk_size = config.get_config('upload', 'chunkSize')
        self.request_chunks = config.get_config('upload', 'requestChunks')

        self.incoming.subscribe(self.process_upload_data)

    def process_upload_data(self, data: UploadData):
        size = data.size  # int
        raw_data = data.data  # bytes
        if (len(raw_data) != size):
            self.outgoing.on_error(DataSizeMismatchException("got %s expected %s" % (len(raw_data), size)))
        order = data.order

        self.session.upload_started = True
        if not self.session.bytes_progress:
            self.session.bytes_progress = 0
        self.session.bytes_progress += size

        request_more = False
        try:
            self.session.enqueue_data(order, raw_data)
            if len(self.session.chunk_buffer) >= self.request_chunks:
                self.session.flush()
                request_more = True
        except Exception as e:
            self.outgoing.on_error(e)
        else:
            self.outgoing.on_next(self._create_progress_message(request_more))

    def _create_progress_message(self, request_more=False) -> bytes:
        message = TransferNodeToClientMessage(
            type=TransferNodeToClientMessage.MessageType.Value('PROGRESS'),
            progressData=ProgressData(
                bytesUploaded=self.session.bytes_progress,
                chunkSize=self.chunk_size,
                requestChunks=self.request_chunks if request_more else 0,
            ),
            timestamp=make_timestamp(),
        )
        return message.SerializeToString()
