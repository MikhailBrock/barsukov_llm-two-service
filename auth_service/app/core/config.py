from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "auth-service"
    ENV: str = "local"
    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SQLITE_PATH: str = "./auth.db"

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    class Config:
        env_file = ".env"


settings = Settings()
