from rx import Observable, Observer

from transfernode.models.session import TransferSession
from transfernode.protobufs.clientmessage_pb2 import (
    RecipientsData, TransferNodeToClientMessage,
)
from transfernode.util import make_timestamp


class RecipientsController:
    def __init__(self, session: TransferSession,
                 incoming: Observable, outgoing: Observer):
        self.incoming = incoming
        self.outgoing = outgoing
        self.session = session

        print(self.incoming)
        self.incoming.subscribe(self.process_finished_data)

    def process_finished_data(self, data: [RecipientsData.Recipient]):
        self.outgoing.on_next(self._create_recipients_message(data))

    def _create_recipients_message(self, data: [RecipientsData.Recipient]) -> bytes:
        message = TransferNodeToClientMessage(
            type=TransferNodeToClientMessage.MessageType.Value('RECIPIENTS'),
            recipientsData=RecipientsData(
                recipients=data
            ),
            timestamp=make_timestamp(),
        )
        return message.SerializeToString()
