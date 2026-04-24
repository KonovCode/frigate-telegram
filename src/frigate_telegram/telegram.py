import httpx


class TelegramClient: 

    def __init__(self, token: str, chat_id: list[str]):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}" 

    async def send_message(self, text: str) -> None:
        async with httpx.AsyncClient() as client:
            for cid in self.chat_id :
                await client.post(f"{self.base_url}/sendMessage", json={
                    "chat_id": cid,
                    "text": text,
                })    

    async def send_photo(self, photo: bytes, caption: str = "") -> None:
        async with httpx.AsyncClient() as client:
            for cid in self.chat_id :
                await client.post(f"{self.base_url}/sendPhoto", files={
                    "photo": ("snapshot.jpg", photo, "image/jpeg")},
                    data={
                        "chat_id": cid,
                        "caption": caption,
                    }
                )        