from check_loc import find_violations


def test_source_size_limits() -> None:
    assert find_violations() == []