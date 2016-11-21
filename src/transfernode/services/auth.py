class AuthService:  # Singleton
    __instance = None

    @classmethod
    def instance(cls) -> AuthService:
        if not cls.__instance:
            cls.__instance = AuthService()
        return cls.__instance

    def validate_key(self, key) -> bool:
        return True if key else False
