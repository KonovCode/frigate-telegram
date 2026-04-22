from pydantic import BaseModel
import yaml
from pathlib import Path

class FrigateConfig(BaseModel):
    url: str

class MqttConfig(BaseModel):
    host: str
    port: int = 1883

class TelegramConfig(BaseModel): 
    token: str
    chat_id: str        

class DetectionConfig(BaseModel): 
    enabled: bool = True
    labels: list[str] = ["person", "car"] 
    min_score: float = 0.75
    send_snapshot: bool = True
    cameras: list[str] = []

class NotificationsConfig(BaseModel): 
    detection: DetectionConfig = DetectionConfig()

class AppConfig(BaseModel): 
    frigate: FrigateConfig
    mqtt: MqttConfig
    telegram: TelegramConfig
    notifications: NotificationsConfig = NotificationsConfig()



def load_config(path: str = "config.yaml") -> AppConfig: 
    config_path = Path(path)
    with open(config_path) as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)    