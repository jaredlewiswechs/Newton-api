from core.schemas import Omega, StructureConstraint, CitationRequirement
from core.live_checker import compute_envelope_distance


def test_live_checker_wordcount_and_citations():
    omega = Omega(prompt='Test', word_count_min=100, word_count_max=200, citations=CitationRequirement(required=True, min_count=2))
    draft = 'Word ' * 120 + '(Smith 2020) ' + '(Doe 2019)'
    res = compute_envelope_distance(omega, draft)
    assert res['word_count'] >= 120
    assert res['citations'] >= 2
    assert res['overall_percentage'] >= 50.0
