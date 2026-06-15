from pydantic import BaseModel, Field, StrictStr, UUID4


class IncomingMessage(BaseModel):
    """
    Input schema for a single message that needs to be saved
    and used for dialog classification.
    """
    text: StrictStr
    dialog_id: UUID4
    id: UUID4
    participant_index: int


class Prediction(BaseModel):
    """
    Classification result:
    - id: unique identifier of the prediction
    - message_id: UUID of the message being responded to
    - dialog_id: ID of the dialog
    - participant_index: participant index
    - is_bot_probability: probability that this message is from bot
    """
    id: UUID4
    message_id: UUID4
    dialog_id: UUID4
    participant_index: int
    is_bot_probability: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
