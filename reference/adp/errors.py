"""ADP-v0.1.md §9 error model. Exactly the 9 codes defined there — no
error hierarchy, no sub-codes, per the spec's explicit minimalism
requirement. Identity/key resolution itself is out of ADP's scope
(§7.3); these exceptions cover only what ADP normatively defines."""
from __future__ import annotations


class ADPError(Exception):
    code: str = "ADP_ERROR"


class InvalidSignature(ADPError):
    code = "INVALID_SIGNATURE"


class UnknownDeal(ADPError):
    code = "UNKNOWN_DEAL"


class DealIdCollision(ADPError):
    code = "DEAL_ID_COLLISION"


class AcceptanceSpecMismatch(ADPError):
    code = "ACCEPTANCE_SPEC_MISMATCH"


class UnauthorizedVerifier(ADPError):
    code = "UNAUTHORIZED_VERIFIER"


class DeliveryHashMismatch(ADPError):
    code = "DELIVERY_HASH_MISMATCH"


class VerificationExpired(ADPError):
    code = "VERIFICATION_EXPIRED"


class AlreadySettled(ADPError):
    code = "ALREADY_SETTLED"


class CanonicalizationErrorADP(ADPError):
    code = "CANONICALIZATION_ERROR"


ERROR_CODES = {
    "INVALID_SIGNATURE": InvalidSignature,
    "UNKNOWN_DEAL": UnknownDeal,
    "DEAL_ID_COLLISION": DealIdCollision,
    "ACCEPTANCE_SPEC_MISMATCH": AcceptanceSpecMismatch,
    "UNAUTHORIZED_VERIFIER": UnauthorizedVerifier,
    "DELIVERY_HASH_MISMATCH": DeliveryHashMismatch,
    "VERIFICATION_EXPIRED": VerificationExpired,
    "ALREADY_SETTLED": AlreadySettled,
    "CANONICALIZATION_ERROR": CanonicalizationErrorADP,
}
assert len(ERROR_CODES) == 9  # ADP-v0.1.md §9: exactly 9 codes
