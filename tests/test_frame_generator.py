from core.frame_generator import generate_handles_from_prompt


def test_generate_handles_basic():
    prompt = "Discuss the causes and effects of the Industrial Revolution."
    out = generate_handles_from_prompt(prompt)
    assert "chronological" in out
    assert "thematic" in out
    assert isinstance(out["chronological"], list)
    assert len(out["chronological"]) >= 3
