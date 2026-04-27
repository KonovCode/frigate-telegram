import pytest
from unittest.mock import AsyncMock
from frigate_telegram.service import Service
from frigate_telegram.config import AppConfig

def make_config(**kwargs): 
    defaults = dict(
        frigate_url="http://frigate",
        mqtt_host="localhost",
        telegram_token="token",
        telegram_chat_id=["123"],
    )
    return AppConfig(**{**defaults, **kwargs})

def make_service():
    service = Service(make_config())
    service.frigate.get_snapshot = AsyncMock(return_value=b"image")
    service.telegram.send_photo = AsyncMock()
    service.telegram.send_message = AsyncMock()
    return service

def make_event(event_type="new", label="person", score=0.8, event_id="evt1", camera="cam1"):
    return {
        "type": event_type,
        "after": {
            "id": event_id,
            "label": label,
            "camera": camera,
            "score": score,
        }
    }

@pytest.mark.asyncio
async def test_sends_notification_on_valid_event():
    service = make_service()

    await service.handle_event(make_event())

    service.telegram.send_photo.assert_called_once()

@pytest.mark.asyncio
async def test_skips_event_with_low_score():
    service = make_service()

    await service.handle_event(make_event(score=0.3))

    service.telegram.send_photo.assert_not_called()  

@pytest.mark.asyncio
async def test_sends_notification_on_update_after_low_score():
    service = make_service()

    await service.handle_event(make_event(score=0.3))
    await service.handle_event(make_event(event_type="update", score=0.7))

    service.telegram.send_photo.assert_called_once()  

@pytest.mark.asyncio
async def test_sends_notification_only_once_when_both_scores_sufficient():
    service = make_service()

    await service.handle_event(make_event(score=0.9))
    await service.handle_event(make_event(event_type="update", score=0.95))

    service.telegram.send_photo.assert_called_once() 

@pytest.mark.asyncio
async def test_skips_event_with_unknown_label():
    service = make_service()

    await service.handle_event(make_event(label="dog"))

    service.telegram.send_photo.assert_not_called() 

@pytest.mark.asyncio
async def test_skips_event_from_unlisted_camera():
    service = make_service() 

    service.config.notifications.detection.cameras = ["cam2"]

    await service.handle_event(make_event(camera="cam1")) 

    service.telegram.send_photo.assert_not_called()   

@pytest.mark.asyncio
async def test_skips_event_when_notification_disabled():
    service = make_service() 
    service.config.notifications.detection.enabled = False

    await service.handle_event(make_event())

    service.telegram.send_photo.assert_not_called()

@pytest.mark.asyncio
async def test_end_allows_repeated_notification():
    service = make_service()

    await service.handle_event(make_event())
    await service.handle_event(make_event(event_type="end"))
    await service.handle_event(make_event())

    assert service.telegram.send_photo.call_count == 2                   