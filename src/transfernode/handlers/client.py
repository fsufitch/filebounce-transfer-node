from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.websocket import WebSocketHandler
from rx.subjects import Subject

from transfernode.controllers.auth import AuthController
from transfernode.controllers.start_upload import StartUploadController
from transfernode.controllers.upload import UploadController
from transfernode.controllers.finish import FinishController
from transfernode.proto.clientmessage_pb2 import ClientToTransferNodeMessage
from transfernode.proto.util import create_client_error_message_bytes
from transfernode.services.session import SessionService


class ClientWebSocketHandler(WebSocketHandler):
    def __init__(self, app: Application, request: HTTPServerRequest, **kwargs):
        super().__init__(app, request, **kwargs)
        self.incoming = Subject()
        self.outgoing = Subject()
        self.session_service = SessionService.instance()
        self.session = self.session_service.start_session()

        auth_messages = (
            self.incoming
            .filter(self._message_has_type('AUTHENTICATE'))
            .map(lambda msg: msg.authData)
        )

        start_upload_messages = (
            self.incoming
            .filter(self._message_has_type('START_UPLOAD'))
            .map(lambda msg: msg.startData)
        )

        upload_messages = (
            self.incoming
            .filter(self._message_has_type('UPLOAD_DATA'))
            .map(lambda msg: msg.uploadData)
        )

        finish_messages = (
            self.incoming
            .filter(self._message_has_type('FINISHED'))
            .map(lambda msg: msg.finishedData)
        )

        self.auth_controller = AuthController(self.session,
                                              auth_messages,
                                              self.outgoing)
        self.start_controller = StartUploadController(self.session,
                                                      start_upload_messages,
                                                      self.outgoing)
        self.upload_controller = UploadController(self.session,
                                                  upload_messages,
                                                  self.outgoing)
        self.finish_controller = FinishController(self.session,
                                                  finish_messages,
                                                  self.outgoing)

        self.outgoing.subscribe(
            lambda msg: self.send(msg),
            lambda exc: self.error(exc),
            lambda: self.complete(),
            )

    def on_message(self, msg: str):
        data = ClientToTransferNodeMessage.FromString(msg.encode())
        self.incoming.on_next(data)

    def send(msg: bytes):
        self.write_message(msg, binary=True)

    def error(exc: Exception):
        message = create_client_error_message_bytes(exc, true)
        self.write_message(message, binary=True)
        self.complete()

    def complete():
        self.session_service.cleanup(self.session.id)
        self.close()

    def _message_has_type(self, msg_type: str):
        type_value = ClientToTransferNodeMessage.MessageType.Value(msg_type)

        def inner(msg: ClientToTransferNodeMessage):
            return msg.type == type_value
        return inner

    def check_origin(self):
        return True  # Allow any connections
