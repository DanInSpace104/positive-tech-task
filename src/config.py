import os


class Settings:
    ENV: str = 'development'
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY") or ''

    SERVER_HOST: str = '127.0.0.1'
    SERVER_PORT: int = 5000
    SERVER_RELOAD: bool = True


settings = Settings()
