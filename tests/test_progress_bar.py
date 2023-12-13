import pytest
from uqload_dl.progress_bar import ProgressBar


@pytest.fixture
def progress_bar() -> ProgressBar:
    return ProgressBar(100)


def test_init_valid_total() -> None:
    progress_bar = ProgressBar(100)
    assert progress_bar.total == 100


@pytest.mark.parametrize("value", [("test"), (""), (True), ([]), ((1, 1)), ({})])
def test_init_non_numeric_total(value) -> None:
    with pytest.raises(ValueError):
        ProgressBar(value)


def test_update(progress_bar: ProgressBar) -> None:
    progress_bar.update(50)
    assert progress_bar.get_pct_completed == 50
    progress_bar.update(100)
    assert progress_bar.get_pct_completed == 100


@pytest.mark.parametrize("value", [("test"), (""), (True), ([]), ((1, 1)), ({})])
def test_update_invalid_value(value, progress_bar: ProgressBar) -> None:
    with pytest.raises(ValueError):
        progress_bar.update(value)
