import sys
import shutil
from pathlib import Path


def init(): 
    dest = Path("config.yaml")
    if dest.exists():
        print("config.yaml уже существует")
        sys.exit(1)

    example = Path(__file__).parent.parent.parent / "config.example.yaml"
    shutil.copy(example, dest)
    print("config.yaml создан. Заполни его и запусти: frigate-telegram start")

def start():
    from frigate_telegram.config import load_config

    config = load_config("config.yaml")   
    print(f"Запуск... Frigate: {config.frigate.url}") 

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