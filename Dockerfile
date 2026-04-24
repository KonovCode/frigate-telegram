FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY .env.example .

RUN pip install -e .

CMD ["frigate-telegram", "start"]
