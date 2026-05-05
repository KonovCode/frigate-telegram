# frigate-telegram

Sends Telegram notifications when [Frigate NVR](https://frigate.video) detects objects on your cameras.

## Quick start

**1. Create `.env`**

```env
FRIGATE_URL=http://192.168.1.10:5000
MQTT_HOST=192.168.1.10
TELEGRAM_TOKEN=123456:your-bot-token
TELEGRAM_CHAT_ID=["123456789"]
```

**2. Run**

```bash
docker run -d \
  --name frigate-telegram \
  --restart unless-stopped \
  --env-file .env \
  ghcr.io/konovcode/frigate-telegram:latest
```

## Configuration

### Required

| Variable | Description |
|---|---|
| `FRIGATE_URL` | Frigate HTTP address |
| `MQTT_HOST` | MQTT broker address |
| `TELEGRAM_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | List of chat IDs, e.g. `["123456789"]` |

### Optional

| Variable | Default | Description |
|---|---|---|
| `MQTT_PORT` | `1883` | MQTT broker port |
| `NOTIFICATIONS__DETECTION__MIN_SCORE` | `0.75` | Minimum confidence (0.0–1.0) |
| `NOTIFICATIONS__DETECTION__LABELS` | `["person","car"]` | Object types to notify about |
| `NOTIFICATIONS__DETECTION__CAMERAS` | `[]` (all) | Whitelist specific cameras |
| `NOTIFICATIONS__DETECTION__SEND_SNAPSHOT` | `true` | Attach camera snapshot |
| `NOTIFICATIONS__DETECTION__ENABLED` | `true` | Enable/disable notifications |

## Full `.env` example

```env
# Frigate
FRIGATE_URL=http://192.168.1.10:5000

# MQTT
MQTT_HOST=192.168.1.10
MQTT_PORT=1883

# Telegram
TELEGRAM_TOKEN=123456:your-bot-token
TELEGRAM_CHAT_ID=["123456789", "987654321"]  # one or multiple chat IDs

# Minimum detection confidence (0.0–1.0). Below this threshold — no notification
NOTIFICATIONS__DETECTION__MIN_SCORE=0.75

# Object types to notify about. Supported: person, car, motorcycle, bus, truck, bicycle, dog, cat
NOTIFICATIONS__DETECTION__LABELS=["person","car"]

# Cameras to watch. Empty list = all cameras
NOTIFICATIONS__DETECTION__CAMERAS=["cam1","cam2"]

# Attach a camera snapshot to the notification
NOTIFICATIONS__DETECTION__SEND_SNAPSHOT=true

# Disable notifications without stopping the service
NOTIFICATIONS__DETECTION__ENABLED=true
```

## Getting your chat ID

1. Send any message to your bot
2. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat": {"id": 123456789}` — that's your ID

Group chat IDs start with `-100`.

## Docker Compose

```yaml
services:
  frigate-telegram:
    image: ghcr.io/konovcode/frigate-telegram:latest
    restart: unless-stopped
    env_file: .env
```
