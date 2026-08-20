"""MVP-01 trusted fixture: a pure function with an obvious mutation surface.

Repository-owned and trusted, as REQ-S29-003 requires — the vertical slice may not
accept an arbitrary project until PROFILE_A passes M6.

The body deliberately contains one integer constant and one arithmetic operator, so
the M01 (constant) and M02 (operator) strategies each have exactly one site to act on.
That keeps the slice's candidate set small and fully enumerable.
"""


def compute_series(n: int) -> int:
    """Return the sum of squares below n.

    >>> compute_series(5)
    30
    """
    total = 0
    for i in range(n):
        total = total + i * i
    return total
