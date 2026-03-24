"""Common utilities and shared resources for resume analysis."""
import re
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


class ToolStub:
    """Stub for grammar checking tool (disabled to avoid rate limits)."""

    def check(self, text):
        return []


tool = ToolStub()


def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    return text.lower().replace('\r', '').strip()


def get_nlp():
    """Get the loaded spaCy NLP model."""
    return nlp


def get_tool():
    """Get the grammar checking tool."""
    return tool
