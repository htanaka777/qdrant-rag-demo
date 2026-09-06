import pytest
from pydantic import ValidationError

from app.schemas import AskRequest


def test_top_k_range():
    req = AskRequest(question="test", top_k=3)
    assert req.top_k == 3


def test_empty_question_is_rejected():
    with pytest.raises(ValidationError):
        AskRequest(question="", top_k=3)
