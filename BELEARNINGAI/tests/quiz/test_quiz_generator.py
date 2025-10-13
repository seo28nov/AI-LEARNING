"""Placeholder test cho AI quiz builder."""
import pytest

from services import quiz_service


@pytest.mark.skip(reason="placeholder: sẽ kiểm thử khi tích hợp GenAI thật")
@pytest.mark.asyncio
async def test_generate_quiz_template_returns_questions():
    """Template demo phải trả về số câu hỏi đúng như yêu cầu."""

    result = await quiz_service.generate_quiz_template(topic="Đại số", num_questions=3)
    assert len(result.questions) == 3
