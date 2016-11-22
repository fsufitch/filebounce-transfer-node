class AuthService:  # Singleton
    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = AuthService()
        return cls.__instance

    def validate_key(self, key) -> bool:
        print(key)
        return True if key else False
