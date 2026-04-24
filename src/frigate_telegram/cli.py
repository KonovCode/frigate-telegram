import sys
import shutil
from pathlib import Path


def init(): 
    dest = Path(".env")
    if dest.exists():
        print(".env уже существует")
        sys.exit(1)

    example = Path(__file__).parent.parent.parent / ".env.example"
    shutil.copy(example, dest)
    print(".env создан. Заполни его и запусти: frigate-telegram start")

def start():
    import asyncio
    from frigate_telegram.config import AppConfig
    from frigate_telegram.service import Service

    config = AppConfig()
    service = Service(config)
    
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        print("Сервис остановлен")


def main():
    if len(sys.argv) < 2:
        print("Использование: frigate-telegram [init|start]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init": 
        init()
    elif command == "start":
        start()
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)                    