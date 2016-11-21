from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

from transfernode.handlers.client import ClientWebSocketHandler
from transfernode.handlers.recipient import RecipientHandler


class StatusHandler(RequestHandler):
    def get(self):
        self.write('Server is running and healthy')


def make_app():
    return Application([
        (r"/status", StatusHandler),
        (r"/client_ws", ClientWebSocketHandler),
        (r"/download/(.*)", RecipientHandler),
    ])


def main():
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
