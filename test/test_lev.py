from src.app import get_puns


def test_get_puns():
    puns = get_puns('apple', limit=1)
    assert puns == ["she’ll be apple"]
