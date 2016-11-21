from uuid import uuid4
from transfernode.models.session import TransferSession


class SessionService:  # Singleton
    def __init__(self):
        self.transfer_sessions = {}

    __instance = None

    @classmethod
    def instance(cls) -> SessionService:
        if not cls.__instance:
            cls.__instance = SessionService()
        return cls.__instance

    def start_session(self) -> TransferSession:
        session = TransferSession(uuid4().hex)
        self.transfer_sessions[session.id] = session
        return session

    def cleanup_session(self, session_id: string):
        if session_id not in self.transfer_sessions:
            return
        self.transfer_sessions[session_id].cleanup()
        del self.transfer_sessions[session_id]
