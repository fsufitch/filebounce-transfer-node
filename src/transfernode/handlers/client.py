from tornado.websocket import WebSocketHandler
from rx.subjects import Subject

from transfernode.controllers.auth import AuthController
from transfernode.controllers.start_upload import StartUploadController
from transfernode.controllers.upload import UploadController
from transfernode.controllers.finish import FinishController
from transfernode.proto.clientmessage_pb2 import ClientToTransferNodeMessage


class ClientWebSocketHandler(WebSocketHandler):
    def __init__(self, app, request, **kwargs):
        super().__init__(app, request, **kwargs)
        self.incoming = Subject()
        self.outgoing = Subject()

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

        self.auth_controller = AuthController(auth_messages, self.outgoing)
        self.start_controller = StartUploadController(start_upload_messages,
                                                      self.outgoing)
        self.upload_controller = UploadController(upload_messages,
                                                  self.outgoing)
        self.finish_controller = FinishController(finish_messages,
                                                  self.outgoing)

        self.outgoing.subscribe(lambda msg: self.send(msg))

    def on_message(self, msg: str):
        data = ClientToTransferNodeMessage.FromString(msg.encode())
        self.incoming.on_next(data)

    def send(msg: bytes):
        self.write_message(msg, binary=True)

    def _message_has_type(self, msg_type: str):
        type_value = ClientToTransferNodeMessage.MessageType.Value(msg_type)

        def inner(msg: ClientToTransferNodeMessage):
            return msg.type == type_value
        return inner
