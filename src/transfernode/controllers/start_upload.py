from transfernode.proto.clientmessage_pb2 import StartUploadData


class StartUploadController:
    def __init__(self, incoming, outgoing):
        self.incoming = incoming
        self.outgoing = outgoing

        self.incoming.subscribe(self.process_start_upload)

    def process_start_upload(self, data: StartUploadData):
        print('starting upload using data:')
        print(data)
