import time
import uuid
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
import psycopg2

from . import database
from .schemas import IncomingMessage, Prediction
from .model_inference import classify_text
from .config import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Inference Service",
    description="Dialog classification"
)


@app.on_event("startup")
def on_startup() -> None:
    """
    Start the FastAPI application.
    Perform a loop to check PostgreSQL availability (just in case).
    After a successful connection, initialize the database.
    """
    while True:
        try:
            conn = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            logger.warning("Waiting for PostgreSQL to become available...")
            time.sleep(2)

    # Initialize the database schema/tables
    database.init_db()


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
        participant_index=msg.participant_index
    )

    # Load the entire dialog
    conversation_text = database.select_messages_by_dialog(msg.dialog_id)
    if not conversation_text:
        raise HTTPException(
            status_code=404,
            detail="No messages found for this dialog_id"
        )

    is_bot_probability = classify_text(conversation_text)
    prediction_id = uuid.uuid4()

    return Prediction(
        id=prediction_id,
        message_id=msg.id,
        dialog_id=msg.dialog_id,
        participant_index=msg.participant_index,
        is_bot_probability=is_bot_probability
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
