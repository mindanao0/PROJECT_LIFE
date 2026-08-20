"""The single capability test the vertical slice runs (capability_tests: 1)."""

from math_kernel import compute_series


def test_sum_of_squares_below_five() -> None:
    assert compute_series(5) == 30
