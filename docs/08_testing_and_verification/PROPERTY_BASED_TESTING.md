# Hypothesis Property-Based Testing (PBT) Specification

> **Subsystem:** Invariant Fuzzing & Property Verification  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S10-001`, `REQ-S11-001`

---

## 1. Property-Based Testing Rules & Strategies

```python
from hypothesis import given, strategies as st
from decimal import Decimal

# Property 1: Pareto Dominance Asymmetry Invariant
@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=5),
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=5)
)
def test_pareto_dominance_asymmetry_pbt(m_a, m_b):
    """หาก a ชนะ b แล้ว b ต้องไม่มีวันชนะ a (Strict Asymmetry)"""
    a_dom_b = dominates(m_a, m_b)
    b_dom_a = dominates(m_b, m_a)
    assert not (a_dom_b and b_dom_a), "Pareto dominance must be strictly asymmetric!"

# Property 2: Canonical Decimal String Roundtrip Invariant
@given(st.decimals(min_value=Decimal("-1000000000.0"), max_value=Decimal("1000000000.0"), places=6))
def test_decimal_canonical_roundtrip_pbt(d):
    """ค่า Decimal เมื่อแปลงเป็น String แล้วแปลงกลับต้องได้ค่าเดิมตรงกัน 100%"""
    serialized = canonical_decimal_serialize(d)
    deserialized = canonical_decimal_deserialize(serialized)
    assert deserialized == d
    assert isinstance(serialized, str)
```
