import logging
import time
import uuid
from contextlib import asynccontextmanager

import psycopg2
import uvicorn
from fastapi import FastAPI, HTTPException

from . import database
from .config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)
from .model_inference import classify_text
from .schemas import IncomingMessage, Prediction

logger = logging.getLogger(__name__)


def wait_for_postgres() -> None:
    """
    Wait until PostgreSQL is reachable before accepting requests.
    """
    while True:
        try:
            conn = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            logger.warning("Waiting for PostgreSQL to become available...")
            time.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_postgres()
    database.init_db()
    yield


app = FastAPI(
    title="Inference Service",
    description="Dialog classification",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=Prediction)
def predict(msg: IncomingMessage) -> Prediction:
    """
    Endpoint to save a message and get the probability
    that a bot is participating in the dialog.

    1. Save the incoming message to the `messages` table.
    2. Retrieve all messages for the given `dialog_id`.
    3. Apply the zero-shot classifier.
    4. Return a `Prediction` object.
    """

    database.insert_message(
        id=msg.id,
        text=msg.text,
        dialog_id=msg.dialog_id,
        participant_index=msg.participant_index,
    )

    # Load the entire dialog
    conversation_text = database.select_messages_by_dialog(msg.dialog_id)
    if not conversation_text:
        raise HTTPException(
            status_code=404,
            detail="No messages found for this dialog_id",
        )

    is_bot_probability = classify_text(conversation_text)
    prediction_id = uuid.uuid4()

    return Prediction(
        id=prediction_id,
        message_id=msg.id,
        dialog_id=msg.dialog_id,
        participant_index=msg.participant_index,
        is_bot_probability=is_bot_probability,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
