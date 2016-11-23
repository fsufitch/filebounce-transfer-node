from tornado.web import RequestHandler, asynchronous

from transfernode.models.exceptions import UploadAlreadyStartedException
from transfernode.services.session import SessionService


class RecipientHandler(RequestHandler):
    def initialize(self):
        self.session_service = SessionService.instance()
        self.session = None
        self.headers_sent = False

    @asynchronous
    def get(self, transfer_id: str):
        if transfer_id not in self.session_service.transfer_sessions:
            self.send_error(404)
            return
        self.session = self.session_service.transfer_sessions[transfer_id]

        try:
            data_stream = self.session.get_data_stream()
        except UploadAlreadyStartedException:
            self.send_error(410)
            return

        self.session.get_data_stream().subscribe(
            lambda data: self.send_data(data),
            lambda exc: self.send_error(500),  # wtf
            lambda: self.complete(),
        )

    def send_data(data: bytes):
        if not self.headers_sent:
            disposition = 'attachment; filename={}'
            disposition = disposition.format(self.session.filename)
            self.set_header('Content-Type', self.session.mimetype)
            self.set_header('Content-Length', self.session.bytes_size)
            self.set_header('Content-Disposition', disposition)
        self.write(data)
        self.flush()  # Necessary?

    def complete():
        self.finish()
