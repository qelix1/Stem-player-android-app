from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    redis_url: str = "redis://localhost:6379/0"
    data_dir: str = "/data"
    public_base_url: str = "http://localhost:8000"
    max_upload_mb: int = 50
    demucs_model: str = "htdemucs"
    demucs_device: str = "cpu"     # на машине без GPU в .env поставьте cpu
    # TODO: allowed_extensions, max_duration_sec

settings = Settings()
