from pathlib import Path
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent


class DatabaseSettings(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15  # minutes
    refresh_token_expire_days: int = 30  # days


class ApiPrefix(BaseModel):
    users: str = "/users"
    tasks: str = "/tasks"
    notes: str = "/notes"
    notifications: str = "/notifications"
    comments: str = "/comments"
    jwt: str = "/jwt"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    # Database
    db: DatabaseSettings
    # Authenticate
    auth_jwt: AuthJWT = AuthJWT()
    # Prefix
    prefix: ApiPrefix = ApiPrefix()


settings = Settings()
