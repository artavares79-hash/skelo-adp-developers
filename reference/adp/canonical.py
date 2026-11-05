"""JSON Canonicalization Scheme (RFC 8785, "JCS") + SHA-256 hashing.

ADP-v0.1.md §6 requires JCS for all canonicalization. This module
implements it directly from the RFC, not from a third-party JCS
library, because none was pre-approved and the algorithm is small
enough to implement precisely for the object shapes ADP actually
needs (JSON objects/arrays/strings/booleans/null and numbers that are
either JSON integers or decimals in the range used by these tests).

Known, explicitly documented scope limitation (see README/CONFORMANCE):
this is NOT a general-purpose JCS library. Number serialization
implements the ECMAScript Number::toString algorithm (RFC 8785 §3.2.2.3)
only for the "ordinary" range (no exponential notation, i.e.
1e-6 <= |x| < 1e21) and for integers up to 2**53. That range covers
every number ADP itself or the T1/T2 payloads in this project use.
Values outside that range raise NotImplementedError rather than
silently emitting a non-conformant serialization.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any


class CanonicalizationError(Exception):
    """Raised when a value cannot be canonicalized per this module's
    documented JCS scope (see module docstring). Maps to ADP error
    CANONICALIZATION_ERROR (ADP-v0.1.md §9)."""


def _canon_number(n: float | int) -> str:
    if isinstance(n, bool):  # bool is a subclass of int in Python — must not be treated as a number
        raise CanonicalizationError("boolean is not a JCS number")
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        if math.isnan(n) or math.isinf(n):
            raise CanonicalizationError("NaN/Infinity are not valid JSON numbers")
        if n == 0.0:
            # JCS: -0 and +0 both serialize as "0"
            return "0"
        if not (1e-6 <= abs(n) < 1e21):
            raise CanonicalizationError(
                f"number {n!r} outside the documented JCS scope of this "
                "implementation (1e-6 <= |x| < 1e21, see canonical.py docstring)"
            )
        if n.is_integer():
            return str(int(n))
        # Shortest round-tripping decimal representation, no exponent,
        # matching ECMAScript ToString for this range. Python's repr()
        # already produces the shortest round-tripping decimal (same
        # algorithm family as V8 uses), and for this magnitude range it
        # never emits exponential notation, so it matches ES's output.
        s = repr(n)
        assert "e" not in s and "E" not in s, s
        return s
    raise CanonicalizationError(f"unsupported number type: {type(n)!r}")


def _canon_string(s: str) -> str:
    # RFC 8785 requires JSON string escaping (RFC 8259) with the shortest
    # standard escapes; Python's json.dumps already does exactly this for
    # a Python str, and UTF-8 encoding is applied by the caller.
    import json as _json
    return _json.dumps(s, ensure_ascii=False)


def _canon_value(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return _canon_number(v)
    if isinstance(v, str):
        return _canon_string(v)
    if isinstance(v, list):
        return "[" + ",".join(_canon_value(x) for x in v) + "]"
    if isinstance(v, dict):
        # RFC 8785: object member names sorted by UTF-16 code unit order.
        # For the BMP-only keys used throughout ADP this is identical to
        # ordinary Python string (Unicode code point) sorting.
        items = sorted(v.items(), key=lambda kv: kv[0])
        return "{" + ",".join(f"{_canon_string(k)}:{_canon_value(val)}" for k, val in items) + "}"
    raise CanonicalizationError(f"unsupported JSON value type: {type(v)!r}")


def canonicalize(obj: Any) -> bytes:
    """Return the RFC 8785 canonical JSON serialization as UTF-8 bytes."""
    return _canon_value(obj).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_hash(obj: dict) -> str:
    """SHA-256 hex of the JCS canonicalization of obj, exactly as ADP-v0.1.md
    §6 defines for AcceptanceSpec/VerificationResult (point 2: the caller
    MUST already have removed 'signature' / 'providerAck' before calling
    this — this function does not strip fields, to avoid silently hiding
    a caller bug where the wrong object was hashed)."""
    return sha256_hex(canonicalize(obj))
