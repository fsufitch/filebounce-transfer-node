import sys
from ipaddress import ip_address, IPv4Address, IPv6Address
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
            self.finish()
            return
        self.session = self.session_service.transfer_sessions[transfer_id]
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        addr = ip_address(remote_ip)
        self.session.add_recipient(
            ipv4=remote_ip if isinstance(addr, IPv4Address) else None,
            ipv6=remote_ip if isinstance(addr, IPv6Address) else None,
            identity="",
        )

        try:
            data_stream = self.session.get_data_stream()
        except UploadAlreadyStartedException:
            self.send_error(410)
            self.finish()
            return


        self.send_data(b'')  # Send headers
        self.session.get_data_stream().subscribe(
            lambda data: self.send_data(data),
            lambda exc: self.complete(exc),  # wtf
            lambda: self.complete(),
        )

    def send_data(self, data: bytes):
        if not self.headers_sent:
            disposition = 'attachment; filename={}'
            disposition = disposition.format(self.session.filename)
            self.set_header('Content-Type', self.session.mimetype)
            self.set_header('Content-Length', self.session.bytes_size)
            self.set_header('Content-Disposition', disposition)
        self.write(data)
        self.flush()  # Necessary?

    def complete(self, exc: Exception=None):
        if exc:
            self.send_error(500, exc_info=sys.exc_info())
        self.finish()
