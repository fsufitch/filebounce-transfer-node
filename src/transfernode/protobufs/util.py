from transfernode.protobufs.clientmessage_pb2 import (
    TransferNodeToClientMessage, ErrorData
)
from transfernode.util import make_timestamp


def create_client_error_message_bytes(exc: Exception,
                                      fatal: bool,
                                      title: str=None) -> bytes:
    title = title if title else exc.__class__.__name__
    message = TransferNodeToClientMessage(
      type=TransferNodeToClientMessage.MessageType.Value('ERROR'),
      errorData=ErrorData(
          title=title,
          jsonDetails=json.dumps(exc.args),
          fatal=False,
          ),
      timestamp=make_timestamp(),
    )
    return message.SerializeToString()
