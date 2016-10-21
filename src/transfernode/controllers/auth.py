from transfernode.proto.clientmessage_pb2 import AuthenticateData


class AuthController:
    def __init__(self, incoming, outgoing):
        self.incoming = incoming
        self.outgoing = outgoing

        self.incoming.subscribe(self.process_authenticate_data)

    def process_authenticate_data(self, data: AuthenticateData):
        print('processing authentication using data')
        print(data)
