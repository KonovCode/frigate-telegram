import httpx


class FrigateClient: 
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.http = httpx.AsyncClient()

    async def get_status(self) -> dict:
        response = await self.http.get(f"{self.base_url}/api/stats")
        response.raise_for_status()
        return response.json()
        
    async def get_snapshot(self, cam: str="cam1") -> bytes:
        response = await self.http.get(f"{self.base_url}/api/{cam}/latest.jpg")
        response.raise_for_status()
        return response.content
    
    async def close(self) -> None: 
        await self.http.aclose()

