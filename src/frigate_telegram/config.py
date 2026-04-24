from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict    

class DetectionConfig(BaseModel): 
    enabled: bool = True
    labels: list[str] = ["person", "car"] 
    min_score: float = 0.75
    send_snapshot: bool = True
    cameras: list[str] = []

class NotificationsConfig(BaseModel): 
    detection: DetectionConfig = DetectionConfig()

class AppConfig(BaseSettings): 
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8"
    )
    frigate_url: str
    mqtt_host: str
    mqtt_port: int = 1883
    telegram_token: str
    telegram_chat_id: str
    notifications: NotificationsConfig = NotificationsConfig() 