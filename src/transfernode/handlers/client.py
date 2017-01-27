import sys
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.websocket import WebSocketHandler
from rx.subjects import Subject
from rx import Observable

from transfernode.controllers.auth import AuthController
from transfernode.controllers.recipients import RecipientsController
from transfernode.controllers.start_upload import StartUploadController
from transfernode.controllers.upload import UploadController
from transfernode.controllers.finish import FinishController
from transfernode.models.exceptions import UnexpectedWebsocketClose
from transfernode.protobufs.clientmessage_pb2 import ClientToTransferNodeMessage
from transfernode.protobufs.util import create_client_error_message_bytes
from transfernode.services.session import SessionService


class ClientWebSocketHandler(WebSocketHandler):
    def __init__(self, app: Application, request: HTTPServerRequest, **kwargs):
        super().__init__(app, request, **kwargs)
        self.incoming = Subject()
        self.outgoing = Subject()
        self.outgoing.subscribe(
            lambda msg: self.send(msg),
            lambda exc: self.error(exc),
            lambda: self.complete(),
            )

        self.session_service = SessionService.instance()
        self.session = self.session_service.start_session()
        self.expect_close = False

        self.incoming_caught = (
            self.incoming
            .catch_exception(self.catch_incoming_error)
            .share()
        )

        auth_messages = (
            self.incoming_caught
            .filter(self._message_has_type('AUTHENTICATE'))
            .map(lambda msg: msg.authData)
        )

        start_upload_messages = (
            self.incoming_caught
            .filter(self._message_has_type('START_UPLOAD'))
            .map(lambda msg: msg.startData)
        )

        upload_messages = (
            self.incoming_caught
            .filter(self._message_has_type('UPLOAD_DATA'))
            .map(lambda msg: msg.uploadData)
        )

        finish_messages = (
            self.incoming_caught
            .filter(self._message_has_type('FINISHED'))
            .map(lambda msg: msg.finishedData)
        )



        self.auth_controller = AuthController(self.session,
                                              auth_messages,
                                              self.outgoing)
        self.recipients_controller = RecipientsController(self.session,
                                                          self.session.recipients_updates,
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


    def catch_incoming_error(self, exc: Exception):
        print("Error in incoming stream", repr(exc), file=sys.stderr)
        return Observable.of()

    def on_message(self, msg: bytes):
        data = ClientToTransferNodeMessage.FromString(msg)
        self.incoming.on_next(data)

    def on_close(self):
        self.session_service.cleanup_session(self.session.id)
        if not self.expect_close:
            self.incoming.on_error(UnexpectedWebsocketClose())
        else:
            self.incoming.on_completed()

    def send(self, msg: bytes):
        self.write_message(msg, binary=True)

    def error(self, exc: Exception):
        message = create_client_error_message_bytes(exc, True)
        self.write_message(message, binary=True)
        self.complete()

    def complete(self):
        self.expect_close = True
        self.close()

    def _message_has_type(self, msg_type: str):
        type_value = ClientToTransferNodeMessage.MessageType.Value(msg_type)

        def inner(msg: ClientToTransferNodeMessage):
            return msg.type == type_value
        return inner

    def check_origin(self, origin):
        return True  # Allow any connections
