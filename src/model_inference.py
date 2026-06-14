import logging

from transformers import pipeline

from .config import CANDIDATE_LABELS, HYPOTHESIS_TEMPLATE, MODEL_NAME

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
            device=-1,
        )
    return _classifier


def format_conversation(messages: list[dict]) -> str:
    """
    Formats dialog lines for subsequent analysis.
    Example:
        "0: Hello\n1: Hi!\n..."
    """
    return "\n".join(f"{msg['participant_index']}: {msg['text']}" for msg in messages)


def classify_text(messages: list[dict]) -> float:
    """
    Runs the dialog through the zero-shot classifier and returns
    the probability that a bot is present in the dialog.
    """
    classifier = load_model()
    conversation_text = format_conversation(messages)
    prompt = f"Determine if there is an AI bot in the dialog:\n\n{conversation_text}"

    result = classifier(
        prompt,
        candidate_labels=CANDIDATE_LABELS,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )

    bot_index = result["labels"].index(CANDIDATE_LABELS[0])
    probability = float(result["scores"][bot_index])
    return max(0.0, min(1.0, probability))
