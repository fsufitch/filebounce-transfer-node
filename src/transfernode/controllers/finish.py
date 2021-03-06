from rx import Observable, Observer

from transfernode.models.session import TransferSession
from transfernode.protobufs.clientmessage_pb2 import FinishedData


class FinishController:
    def __init__(self, session: TransferSession,
                 incoming: Observable, outgoing: Observer):
        self.incoming = incoming
        self.outgoing = outgoing
        self.session = session

        self.incoming.subscribe(self.process_finished_data)

    def process_finished_data(self, data: FinishedData):
        self.session.flush()
        self.outgoing.on_completed()
