import json 
import logging
import aiomqtt as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from frigate_telegram.config import AppConfig
from frigate_telegram.frigate import FrigateClient
from frigate_telegram.telegram import TelegramClient

class Service: 
    def __init__(self, config: AppConfig):
        self.config = config
        self.frigate = FrigateClient(config.frigate_url)
        self.telegram = TelegramClient(config.telegram_token, config.telegram_chat_id)
        self.seen_events: set[str] = set()

    async def handle_event(self, payload: dict) -> None: 
        after = payload.get("after", {})
        event_id = after.get("id")
        label = after.get("label")
        camera = after.get("camera")
        score = after.get("score") or 0.0
        event_type = payload.get("type")

        log.info("event type=%s label=%s camera=%s score=%s id=%s", event_type, label, camera, score, event_id)

        if event_type != "new":
            return

        if event_id in self.seen_events: 
            return

        detection_cfg = self.config.notifications.detection
        if not detection_cfg.enabled:
            return 
        if label not in detection_cfg.labels:
            log.info("skip: label '%s' not in %s", label, detection_cfg.labels)
            return
        if score < detection_cfg.min_score:
            log.info("skip: score %.2f < min_score %.2f", score, detection_cfg.min_score)
            return 

        self.seen_events.add(event_id)

        caption = f"{camera}: {label} {round(score * 100)}%" 

        if detection_cfg.send_snapshot:
            snapshot = await self.frigate.get_snapshot(camera)
            await self.telegram.send_photo(snapshot, caption=caption)
        else: 
            await self.telegram.send_message(caption)  

    async def run(self) -> None:
        log.info("Запуск сервиса. Frigate: %s", self.config.frigate_url)
        async with mqtt.Client(self.config.mqtt_host, self.config.mqtt_port) as client:
            await client.subscribe("frigate/events")
            log.info("Подписка на frigate/events — ожидаем события...")
            async for message in client.messages: 
                payload = json.loads(message.payload)
                await self.handle_event(payload)             