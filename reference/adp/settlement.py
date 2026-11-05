"""Settlement rule, ADP-v0.1.md §5. NOT a message/object — a local
check any payment adapter performs (§5.4). This module implements the
seven §5.1 conditions plus §4.6 replay protection and §5.6
double-settlement protection. It is deliberately rail-neutral: it
returns an ALLOWED/DENIED decision and a reason, and does not call any
payment rail (x402/ERC-8183 bindings are explicitly out of ADP Core,
§12, and out of scope for this implementation per the task).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import models
from .canonical import object_hash
from .crypto import verify_object_signature
from .errors import (
    AcceptanceSpecMismatch,
    AlreadySettled,
    DeliveryHashMismatch,
    InvalidSignature,
    UnauthorizedVerifier,
    VerificationExpired,
)


class SettlementDecision(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


@dataclass(frozen=True)
class SettlementResult:
    decision: SettlementDecision
    reason: str


class SettlementEngine:
    """Holds the two pieces of local state ADP-v0.1.md requires a
    conformant participant to keep (§4.6, §5.6) — an in-memory
    replacement for whatever persistence a real deployment would use.
    No database per task instructions; this is intentionally the
    smallest possible state to satisfy the two protections."""

    def __init__(self) -> None:
        self._seen_nonces: set[tuple[str, str, str]] = set()  # (dealId, verifierId, nonce)
        self._consumed: set[tuple[str, str]] = set()  # (dealId, acceptanceSpecHash)

    # ---- §4.6 replay protection -------------------------------------------------
    def check_and_register_nonce(self, vr: dict) -> None:
        key = (vr["dealId"], vr["verifierId"], vr["nonce"])
        if key in self._seen_nonces:
            raise ValueError(
                f"replay detected: (dealId, verifierId, nonce)={key} already seen — "
                "ADP-v0.1.md §4.6 requires this VerificationResult to be discarded"
            )
        self._seen_nonces.add(key)

    # ---- §5.6 double-settlement protection ---------------------------------------
    def is_consumed(self, deal_id: str, acceptance_spec_hash: str) -> bool:
        return (deal_id, acceptance_spec_hash) in self._consumed

    def mark_consumed(self, deal_id: str, acceptance_spec_hash: str) -> None:
        self._consumed.add((deal_id, acceptance_spec_hash))

    # ---- §5.1 the seven conditions -------------------------------------------
    def evaluate(
        self,
        *,
        spec: dict,
        issuer_pubkey_b64u: str,
        vr: dict,
        bound_acceptance_spec_hash: str,
        actual_delivery_hash: str,
        register_nonce: bool = True,
    ) -> SettlementResult:
        """Evaluate ADP-v0.1.md §5.1 conditions 1-7 for one
        VerificationResult against one AcceptanceSpec. Does NOT consume
        the settlement (call `mark_consumed` only after the caller has
        actually triggered rail-side release, per §5.6) — this mirrors
        the spec's separation between "settlement is allowed" and
        "settlement was actually performed".

        Returns ALLOWED only if vr.result == PASS and all 7 conditions
        hold. Any FAIL result, or any failed condition, returns DENIED
        with the reason — per §5.2, FAIL must never accidentally allow
        capture, so this function raises exceptions for the specific,
        named ADP error conditions (so a caller integrating this into a
        larger system gets the precise error code) but never raises for
        an ordinary, valid FAIL — that is a normal DENIED outcome, not
        an error.
        """
        # Structural sanity (cheap, must hold before anything else)
        models.validate_acceptance_spec_structure(spec)
        models.validate_verification_result_structure(vr)

        # Condition 1: dealId match
        if vr["dealId"] != spec["dealId"]:
            return SettlementResult(SettlementDecision.DENIED, "dealId mismatch between AcceptanceSpec and VerificationResult")

        # AcceptanceSpec signature must be valid before we trust any of its content
        # (including verifierAuthorization, which condition 4 below relies on).
        spec_unsigned = {k: v for k, v in spec.items() if k not in ("signature", "providerAck")}
        if not verify_object_signature(spec_unsigned, spec["signature"], issuer_pubkey_b64u):
            raise InvalidSignature("AcceptanceSpec signature does not verify")

        # Condition 4: authorized verifier. ADP-v0.1.md §4.5 is explicit that this
        # is checked "unabhaengig davon, ob seine Signatur technisch gueltig ist" —
        # i.e. a plain identity comparison, performed BEFORE the VerificationResult's
        # own signature is verified (a mismatched verifierId is rejected on identity
        # grounds alone, without needing to touch its signature at all).
        models.check_verifier_authorized(spec, vr)

        # Condition 5 (continued): VerificationResult signature, verified against the
        # single key that AcceptanceSpec.verifierAuthorization designates (v0.1's
        # only mode, "designated-key", embeds the key directly — see §3.4).
        vr_unsigned = {k: v for k, v in vr.items() if k != "signature"}
        verifier_pubkey_b64u = spec["verifierAuthorization"]["verifierPubKey"]
        if not verify_object_signature(vr_unsigned, vr["signature"], verifier_pubkey_b64u):
            raise InvalidSignature("VerificationResult signature does not verify")

        # Condition 2: valid AcceptanceSpec whose hash matches the mandate-bound hash
        models.check_acceptance_spec_binding(bound_acceptance_spec_hash, vr)
        if object_hash(spec_unsigned) != bound_acceptance_spec_hash:
            raise AcceptanceSpecMismatch(
                "the AcceptanceSpec object's own hash does not match the mandate-bound "
                "acceptanceSpecHash — the spec presented is not the one that was locked"
            )

        # Condition 3: delivery binding — the deliveryHash referenced by the
        # VerificationResult must correspond to the actually-received delivery.
        if vr["deliveryHash"] != actual_delivery_hash:
            raise DeliveryHashMismatch(
                f"VerificationResult.deliveryHash={vr['deliveryHash']!r} != actual delivery hash={actual_delivery_hash!r}"
            )

        # Condition 6: within validity window
        models.check_within_validity(spec, vr)

        # Replay protection (§4.6) — independent of, but performed alongside, settlement evaluation
        if register_nonce:
            self.check_and_register_nonce(vr)

        # Condition 7: not already consumed
        if self.is_consumed(vr["dealId"], vr["acceptanceSpecHash"]):
            raise AlreadySettled(
                f"(dealId, acceptanceSpecHash)=({vr['dealId']}, {vr['acceptanceSpecHash']}) already settled — §5.6"
            )

        # All 7 conditions hold. §5.2: FAIL must NEVER allow settlement, checked last
        # so that a FAIL result still goes through full structural/crypto validation
        # (a forged/invalid FAIL is still rejected as an error, not silently DENIED).
        if vr["result"] == "FAIL":
            return SettlementResult(SettlementDecision.DENIED, "VerificationResult.result == FAIL (§5.2: settlement forbidden)")

        return SettlementResult(SettlementDecision.ALLOWED, "all §5.1 conditions (1-7) satisfied, result == PASS")
