from transfernode.proto.clientmessage_pb2 import UploadData


class UploadController:
    def __init__(self, incoming, outgoing):
        self.incoming = incoming
        self.outgoing = outgoing

        self.incoming.subscribe(self.process_upload_data)

    def process_upload_data(self, data: UploadData):
        print('processing upload data')
        print(data)
