from rx import Observable, Observer

from transfernode.models.exceptions import DataSizeMismatchException
from transfernode.models.session import TransferSession
from transfernode.proto.clientmessage_pb2 import (
    UploadData, TransferNodeToClientMessage, ProgressData, ErrorData
)
from transfernode.util import make_timestamp


class UploadController:
    def __init__(self, session: TransferSession,
                 incoming: Observable, outgoing: Observer):
        self.incoming = incoming
        self.outgoing = outgoing
        self.session = session

        self.incoming.subscribe(self.process_upload_data)

    def process_upload_data(self, data: UploadData):
        size = data.size  # int
        raw_data = data.data  # bytes
        if (len(raw_data) != size):
            self.outgoing.on_error(DataSizeMismatchException())

        self.session.upload_started = True
        if not self.session.bytes_progress:
            self.session.bytes_progress = 0
        self.session.bytes_progress += size

        try:
            self.session.send_data(raw_data)
        except Exception as e:
            self.outgoing.on_error(e)
        else:
            self.outgoing.on_next(self._create_progress_message())

    def _create_progress_message(self, bytes_progress: int) -> bytes:
        message = TransferNodeToClientMessage(
            type=TransferNodeToClientMessage.MessageType.Value('PROGRESS'),
            progressData=ProgressData(
                bytesUploaded=self.session.bytes_progress
            ),
            timestamp=make_timestamp(),
        )
        return message.SerializeToString()
