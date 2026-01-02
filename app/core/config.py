from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/postgres"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    jwt_issuer: str = "ml-service"
    jwt_audience: str = "ml-service"
    admin_user: str = "admin"
    admin_password: str = "admin"
    delete_token: str = "delete-me"
    ocr_lang: str = "en"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
