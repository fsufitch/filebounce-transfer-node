from rx import Observable, Observer

from transfernode.models.exceptions import AuthenticationFailedException
from transfernode.models.session import TransferSession
from transfernode.protobufs.clientmessage_pb2 import (
    AuthenticateData, TransferNodeToClientMessage, AuthSuccessData, ErrorData,
)
from transfernode.protobufs.util import create_client_error_message_bytes
from transfernode.services.auth import AuthService
from transfernode.util import make_timestamp


class AuthController:
    def __init__(self, session: TransferSession,
                 incoming: Observable,
                 outgoing: Observer):
        self.incoming = incoming
        self.outgoing = outgoing
        self.session = session
        self.auth_service = AuthService.instance()

        self.incoming.subscribe(self.process_authenticate_data)

    def process_authenticate_data(self, data: AuthenticateData):
        if self.auth_service.validate_key(data.key):
            self.session.authenticated = True
            self.outgoing.on_next(self._create_success_message())
        else:
            self.session.authenticated = False
            self.outgoing.on_next(create_client_error_message_bytes(
                AuthenticationFailedException(), False
            ))

    def _create_success_message(self) -> bytes:
        message = TransferNodeToClientMessage(
            type=TransferNodeToClientMessage.MessageType.Value('AUTH_SUCCESS'),
            authSuccessData=AuthSuccessData(),
            timestamp=make_timestamp(),
        )
        return message.SerializeToString()
