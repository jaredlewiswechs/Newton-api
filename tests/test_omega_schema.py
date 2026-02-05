from datetime import datetime, timedelta

from core.schemas import Omega, StructureConstraint


def test_omega_basic_instantiation():
    now = datetime.utcnow()
    o = Omega(
        assignment_id="a1",
        title="Photosynthesis Essay",
        prompt="Explain the process of photosynthesis and its ecological importance.",
        due_date=now + timedelta(days=7),
        word_count_min=300,
        word_count_max=800,
        structure=[StructureConstraint(name="Introduction", min_words=50, required=True)],
    )

    assert o.prompt.startswith("Explain the process")
    assert o.word_count_min <= o.word_count_max
    assert any(s.name == "Introduction" for s in o.structure)
