from transfernode.proto.clientmessage_pb2 import FinishedData


class FinishController:
    def __init__(self, incoming, outgoing):
        self.incoming = incoming
        self.outgoing = outgoing

        self.incoming.subscribe(self.process_finished_data)

    def process_finished_data(self, data: FinishedData):
        print('processing finished message from client with data')
        print(data)
