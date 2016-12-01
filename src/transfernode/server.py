import sys, yaml

from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

from transfernode.config import TransferNodeConfiguration
from transfernode.handlers.client import ClientWebSocketHandler
from transfernode.handlers.recipient import RecipientHandler


class StatusHandler(RequestHandler):
    def get(self):
        self.write('Server is running and healthy')

def make_config(path):
    with open(path) as f:
        data = yaml.load(f)
    return TransferNodeConfiguration(data)

def make_app(config):
    return Application([
        (r"/status", StatusHandler),
        (r"/client_ws", ClientWebSocketHandler),
        (r"/download/(.*)", RecipientHandler),
    ])


def main():
    if len(sys.argv) < 2:
        print("Please specify a config file")
        sys.exit(1)
    config = make_config(sys.argv[1])
    app = make_app(config)
    app.listen(config.get_config('listen', 'port'))
    IOLoop.current().start()


if __name__ == "__main__":
    main()
