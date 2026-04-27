import json 
import logging
import aiomqtt as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from frigate_telegram.config import AppConfig
from frigate_telegram.frigate import FrigateClient
from frigate_telegram.telegram import TelegramClient

LABELS_RU = {
    "person": "Человек",
    "car": "Машина",
    "motorcycle": "Мотоцикл",
    "bus": "Автобус",
    "truck": "Грузовик",
    "bicycle": "Велосипед",
    "dog": "Собака",
    "cat": "Кот",
}

class Service: 
    def __init__(self, config: AppConfig):
        self.config = config
        self.frigate = FrigateClient(config.frigate_url)
        self.telegram = TelegramClient(config.telegram_token, config.telegram_chat_id)
        self.seen_events: set[str] = set()
        self.pending_events: set[str] = set()

    async def handle_event(self, payload: dict) -> None: 
        after = payload.get("after", {})
        event_id = after.get("id")
        label = after.get("label")
        camera = after.get("camera")
        score = after.get("score") or 0.0
        event_type = payload.get("type")

        log.info("event type=%s label=%s camera=%s score=%s id=%s", event_type, label, camera, score, event_id)

        if event_type == "end":
            self.seen_events.discard(event_id)
            self.pending_events.discard(event_id)
            return

        if event_type not in ("new", "update"):
            return
        
        if event_type == "update" and event_id not in self.pending_events:
            return

        if event_id in self.seen_events: 
            return

        detection_cfg = self.config.notifications.detection
        if not detection_cfg.enabled:
            log.info("skip: notifications disabled")
            return 
        if label not in detection_cfg.labels:
            log.info("skip: label '%s' not in %s", label, detection_cfg.labels)
            return
        if detection_cfg.cameras and camera not in detection_cfg.cameras:
            log.info("skip: camera '%s' not in '%s'", camera, detection_cfg.cameras)
            return
        if score < detection_cfg.min_score:
            if event_type == "new":
                self.pending_events.add(event_id)
            log.info("skip: score %.2f < min_score %.2f", score, detection_cfg.min_score)
            return 

        self.pending_events.discard(event_id)
        self.seen_events.add(event_id)

        label_ru = LABELS_RU.get(label, label)
        caption = f"{camera}: {label_ru} {round(score * 100)}%" 

        try :
            if detection_cfg.send_snapshot:
                snapshot = await self.frigate.get_snapshot(camera)
                await self.telegram.send_photo(snapshot, caption=caption)
            else: 
                await self.telegram.send_message(caption)  
        except Exception:
            log.exception("Ошибка при отправке!")

    async def run(self) -> None:
        log.info("Запуск сервиса. Frigate: %s", self.config.frigate_url)
        try:
            async with mqtt.Client(self.config.mqtt_host, self.config.mqtt_port) as client:
                await client.subscribe("frigate/events")
                log.info("Подписка на frigate/events — ожидаем события...")
                async for message in client.messages: 
                    payload = json.loads(message.payload)
                    await self.handle_event(payload)             
        finally:  
            await self.telegram.close()      