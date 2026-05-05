import asyncio
import pytest
import aiomqtt as mqtt
from unittest.mock import AsyncMock, patch
from test_service import make_service


@pytest.mark.asyncio
async def test_reconnects_after_mqtt_error():
    service = make_service()
    service.telegram.close = AsyncMock()

    call_count = 0

    async def fake_listen(client):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise mqtt.MqttError("down")
        raise asyncio.CancelledError()

    service._listen = fake_listen

    with patch("frigate_telegram.service.mqtt.Client", return_value=AsyncMock()):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(asyncio.CancelledError):
                await service.run()

    mock_sleep.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delay_doubles_on_repeated_failures():
    service = make_service()
    service.telegram.close = AsyncMock()

    call_count = 0

    class FakeClient:
        async def __aenter__(self):
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise mqtt.MqttError("down")
            raise asyncio.CancelledError()

        async def __aexit__(self, *args):
            pass

    with patch("frigate_telegram.service.mqtt.Client", side_effect=lambda *a, **kw: FakeClient()):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(asyncio.CancelledError):
                await service.run()

    delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert delays == [1, 2, 4]


@pytest.mark.asyncio
async def test_telegram_closes_on_exit():
    service = make_service()
    service.telegram.close = AsyncMock()

    async def fake_listen(client):
        raise asyncio.CancelledError()

    service._listen = fake_listen

    with patch("frigate_telegram.service.mqtt.Client", return_value=AsyncMock()):
        with pytest.raises(asyncio.CancelledError):
            await service.run()

    service.telegram.close.assert_called_once()
