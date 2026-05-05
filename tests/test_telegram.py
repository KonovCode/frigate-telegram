import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from frigate_telegram.telegram import TelegramClient


def make_client(chat_ids=["111", "222"]):
    return TelegramClient(token="test_token", chat_id=chat_ids)


def ok_response():
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    return resp


def error_response():
    resp = MagicMock()
    resp.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("403", request=MagicMock(), response=MagicMock())
    )
    return resp


@pytest.mark.asyncio
async def test_send_message_to_all_chats():
    client = make_client(["111", "222"])
    client.client.post = AsyncMock(return_value=ok_response())

    await client.send_message("hello")

    assert client.client.post.call_count == 2


@pytest.mark.asyncio
async def test_send_message_continues_after_one_failure():
    client = make_client(["111", "222"])
    client.client.post = AsyncMock(side_effect=[error_response(), ok_response()])

    await client.send_message("hello")

    assert client.client.post.call_count == 2


@pytest.mark.asyncio
async def test_send_photo_to_all_chats():
    client = make_client(["111", "222"])
    client.client.post = AsyncMock(return_value=ok_response())

    await client.send_photo(b"image", caption="test")

    assert client.client.post.call_count == 2


@pytest.mark.asyncio
async def test_send_photo_continues_after_one_failure():
    client = make_client(["111", "222"])
    client.client.post = AsyncMock(side_effect=[error_response(), ok_response()])

    await client.send_photo(b"image", caption="test")

    assert client.client.post.call_count == 2
