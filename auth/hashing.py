import bcrypt


class HashingPassword:
    # Хешируем пароль
    @staticmethod
    def hash_password(
        password: str,
    ) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_bytes.decode()

    # Проверяем пароль (валидируем)
    @staticmethod
    def validate_password(
        password: str,
        hashed_password: str,
    ) -> bool:
        return bcrypt.checkpw(
            password=password.encode(),
            hashed_password=hashed_password.encode(),
        )


hashing_password = HashingPassword()
