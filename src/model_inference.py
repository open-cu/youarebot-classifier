import logging
from transformers import pipeline
from .config import MODEL_NAME, CANDIDATE_LABELS

logger = logging.getLogger(__name__)
_classifier = None


def load_model():
    """
    Loads (or returns an already loaded) zero-shot classifier.
    """
    global _classifier
    if _classifier is None:
        logger.info("Loading zero-shot-classification pipeline...")
        _classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_NAME,
            device=-1
        )
    return _classifier


def format_conversation(messages):
    """
    Formats dialog lines for subsequent analysis.
    Example:
        "0: Hello\n1: Hi!\n..."
    """
    return "\n".join(
        [f"{msg['participant_index']}: {msg['text']}" for msg in messages]
    )


def classify_text(messages) -> float:
    """
    Runs the dialog through the zero-shot classifier and returns
    the probability that a bot is present in the dialog.
    """
    classifier = load_model()
    conversation_text = format_conversation(messages)
    prompt = f"Determine if there is an AI bot in the dialog:\n\n{conversation_text}"

    result = classifier(
        prompt,
        candidate_labels=CANDIDATE_LABELS
    )

    bot_index = result["labels"].index(CANDIDATE_LABELS[0])
    return result["scores"][bot_index]
