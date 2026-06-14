# Youarebot Classifier

FastAPI service that receives chat messages, stores them in PostgreSQL, and returns
`is_bot_probability` for the whole dialog.

The public contract is intentionally small:

- `GET /health` returns service status.
- `POST /predict` accepts one message and returns a prediction for the dialog.

## Stack

- Python 3.12
- uv
- FastAPI + Uvicorn
- Pydantic v2
- PostgreSQL
- Transformers zero-shot classification pipeline

The default model is `typeform/distilbert-base-uncased-mnli`, a lightweight
DistilBERT MNLI model used through the Transformers zero-shot classification
pipeline.

## Local Run

Install dependencies:

```bash
uv sync
```

Start PostgreSQL locally, for example through Compose:

```bash
docker compose up -d postgres
```

Run the API:

```bash
DB_HOST=localhost uv run uvicorn src.main:app --reload
```

The service listens on `http://127.0.0.1:8000`.

Check health:

```bash
curl http://127.0.0.1:8000/health
```

## Docker Compose

Run the full stack:

```bash
docker compose up --build
```

Compose exposes the API as `http://localhost:443` on the host and keeps the
container listening on port `8000`.

## API

### `GET /health`

```json
{
  "status": "ok"
}
```

### `POST /predict`

Request:

```json
{
  "text": "Hi, how are you?",
  "dialog_id": "0f2d4682-d939-4af6-beb9-880a5da202a2",
  "id": "13ab658b-8463-4410-a747-33ea2dfb7b68",
  "participant_index": 0
}
```

Response:

```json
{
  "id": "814c9637-5f4a-4633-84d2-f86c7fa62a48",
  "message_id": "13ab658b-8463-4410-a747-33ea2dfb7b68",
  "dialog_id": "0f2d4682-d939-4af6-beb9-880a5da202a2",
  "participant_index": 0,
  "is_bot_probability": 0.42
}
```

`is_bot_probability` is validated by Pydantic and must stay in `[0, 1]`.

## Configuration

Environment variables:

```bash
DB_USER=student
DB_PASSWORD=student_pass
DB_HOST=postgres
DB_PORT=5432
DB_NAME=chat_db
MODEL_NAME=typeform/distilbert-base-uncased-mnli
```

The model is loaded lazily on the first `/predict` call.
