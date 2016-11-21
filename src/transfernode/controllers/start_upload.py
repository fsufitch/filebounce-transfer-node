import json
from rx import Observable, Observer

from transfernode.models.exceptions import (
    NotAuthenticatedException, InvalidUploadDataException
)
from transfernode.models.session import TransferSession
from transfernode.proto.clientmessage_pb2 import (
    StartUploadData, TransferNodeToClientMessage, TransferCreatedData,
)
from transfernode.proto.util import create_client_error_message_bytes
from transfernode.util import make_timestamp


class StartUploadController:
    def __init__(self, session: TransferSession,
                 incoming: Observable[StartUploadData],
                 outgoing: Observer[bytes]):
        self.incoming = incoming
        self.outgoing = outgoing

        self.incoming.subscribe(self.process_start_upload)

    def process_start_upload(self, data: StartUploadData):
        if not self.session.authenticated:
            self.outgoing.on_next(create_client_error_message_bytes(
                NotAuthenticatedException(), False
            ))

        try:
            self.validate_upload_data(data)
        except InvalidUploadDataException as e:
            self.outgoing.on_next(create_client_error_message_bytes(e))

        self.session.filename = data.filename
        self.session.mimetype = data.mimetype
        self.session.bytes_size = data.size
        self.outgoing.on_next(self._create_success_message(self.session.id))

    def validate_upload_data(self, data: StartUploadData):
        if not data:
            raise InvalidUploadDataException('Upload data is null')
        # Add more validation here

    def _create_success_message(self, session_id) -> bytes:
        message = TransferNodeToClientMessage(
            type=TransferNodeToClientMessage.MessageType.Value('TRANSFER_CREATED'),
            transferCreatedData=TransferCreatedData(
                transferId=session_id,
            ),
            timestamp=make_timestamp(),
        )
        return message.SerializeToString()
