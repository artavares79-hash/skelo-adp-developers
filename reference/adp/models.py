"""AcceptanceSpec and VerificationResult: structural validation, hashing,
signing and verification, per ADP-v0.1.md §3 and §4.

Design choice: ADP objects are represented as plain dicts (not classes
with hidden defaults), because the spec defines them as JSON objects
with an explicit, closed set of required fields — a plain dict keeps
the mapping between spec field names and code exact and auditable.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .canonical import object_hash
from .crypto import Keypair, require_valid_signature, sign_object, verify_object_signature
from .errors import (
    AcceptanceSpecMismatch,
    CanonicalizationErrorADP,
    InvalidSignature,
    UnauthorizedVerifier,
    VerificationExpired,
)

# ADP-v0.1.md §3.2 — 9 required fields (signature is the envelope, not counted here)
ACCEPTANCE_SPEC_REQUIRED_FIELDS = (
    "specVersion", "dealId", "subjectHash", "verificationMethod",
    "acceptanceCondition", "verifierAuthorization", "validity",
    "evidenceRequirements", "issuer",
)

# ADP-v0.1.md §4.2 — 9 required fields (signature is the envelope, not counted here)
VERIFICATION_RESULT_REQUIRED_FIELDS = (
    "resultVersion", "dealId", "acceptanceSpecHash", "deliveryHash",
    "verifierId", "result", "evidenceRefs", "timestamp", "nonce",
)

ACCEPTANCE_SPEC_VERSION = "adp-acceptance/0.1"
VERIFICATION_RESULT_VERSION = "adp-verification/0.1"


def _without(obj: dict, *fields: str) -> dict:
    return {k: v for k, v in obj.items() if k not in fields}


def _parse_rfc3339(s: str) -> datetime:
    # Accept the 'Z' suffix used throughout the spec's examples.
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------------------------------------------------------------- AcceptanceSpec

def build_acceptance_spec(
    *,
    deal_id: str,
    subject_hash: str,
    verification_method: dict,
    acceptance_condition: dict,
    verifier_authorization: dict,
    not_before: str,
    not_after: str,
    evidence_requirements: list[str],
    issuer: str,
) -> dict:
    """Construct an unsigned AcceptanceSpec dict with exactly the fields
    ADP-v0.1.md §3.2 requires. `sign_acceptance_spec` must be called
    before this is a valid, usable spec (§3.1: it must be signed)."""
    spec = {
        "specVersion": ACCEPTANCE_SPEC_VERSION,
        "dealId": deal_id,
        "subjectHash": subject_hash,
        "verificationMethod": verification_method,
        "acceptanceCondition": acceptance_condition,
        "verifierAuthorization": verifier_authorization,
        "validity": {"notBefore": not_before, "notAfter": not_after},
        "evidenceRequirements": list(evidence_requirements),
        "issuer": issuer,
    }
    validate_acceptance_spec_structure(spec)
    return spec


def validate_acceptance_spec_structure(spec: dict) -> None:
    missing = [f for f in ACCEPTANCE_SPEC_REQUIRED_FIELDS if f not in spec]
    if missing:
        raise CanonicalizationErrorADP(f"AcceptanceSpec missing required field(s): {missing}")
    if spec["specVersion"] != ACCEPTANCE_SPEC_VERSION:
        raise CanonicalizationErrorADP(f"unsupported specVersion: {spec['specVersion']!r}")
    va = spec["verifierAuthorization"]
    if va.get("mode") != "designated-key":
        # ADP-v0.1.md §3.4: v0.1 defines exactly one mode.
        raise CanonicalizationErrorADP(f"unsupported verifierAuthorization.mode: {va.get('mode')!r}")
    if "verifierKeyId" not in va or "verifierPubKey" not in va:
        raise CanonicalizationErrorADP("verifierAuthorization missing verifierKeyId/verifierPubKey")
    vm_type = spec["verificationMethod"].get("type")
    if vm_type not in ("hash-equals", "sandboxed-test-suite"):
        # ADP-v0.1.md §3.3: v0.1 defines exactly two method types.
        raise CanonicalizationErrorADP(f"unsupported verificationMethod.type: {vm_type!r}")


def acceptance_spec_hash(spec: dict) -> str:
    """acceptanceSpecHash per §6: SHA-256(JCS(spec without 'signature'))."""
    return object_hash(_without(spec, "signature", "providerAck"))


def sign_acceptance_spec(spec: dict, issuer_keypair: Keypair) -> dict:
    unsigned = _without(spec, "signature", "providerAck")
    signed = dict(spec)
    signed["signature"] = sign_object(unsigned, issuer_keypair)
    return signed


def verify_acceptance_spec_signature(spec: dict) -> bool:
    """Verifies against the key embedded in the spec's own
    verifierAuthorization is WRONG per §7.3 (issuer key != verifier
    key, in general). This function therefore requires the caller to
    supply the issuer's public key explicitly — see
    `verify_acceptance_spec_signature_with_key`. This is intentional,
    normatively confirmed by ADP-v0.1.1.md §7.3's key-resolution
    clarification (see ADP-v0.1-ERRATA.md item 4): kid resolution is
    entirely outside ADP, so this module cannot and must not resolve it
    itself — callers MUST supply the resolved key."""
    raise NotImplementedError(
        "AcceptanceSpec has no issuer public key field by design (key resolution is "
        "outside ADP, see ADP-v0.1.1.md §7.3) — use verify_acceptance_spec_signature_with_key"
    )


def verify_acceptance_spec_signature_with_key(spec: dict, issuer_pubkey_b64u: str) -> bool:
    unsigned = _without(spec, "signature", "providerAck")
    return verify_object_signature(unsigned, spec["signature"], issuer_pubkey_b64u)


# ------------------------------------------------------------- VerificationResult

def build_verification_result(
    *,
    deal_id: str,
    acceptance_spec_hash: str,
    delivery_hash: str,
    verifier_id: str,
    result: str,
    evidence_refs: list[dict],
    timestamp: str,
    nonce: str,
) -> dict:
    if result not in ("PASS", "FAIL"):
        # ADP-v0.1.md §4.3: v0.1 allows exactly these two values.
        raise CanonicalizationErrorADP(f"VerificationResult.result must be PASS or FAIL, got {result!r}")
    vr = {
        "resultVersion": VERIFICATION_RESULT_VERSION,
        "dealId": deal_id,
        "acceptanceSpecHash": acceptance_spec_hash,
        "deliveryHash": delivery_hash,
        "verifierId": verifier_id,
        "result": result,
        "evidenceRefs": list(evidence_refs),
        "timestamp": timestamp,
        "nonce": nonce,
    }
    validate_verification_result_structure(vr)
    return vr


def validate_verification_result_structure(vr: dict) -> None:
    missing = [f for f in VERIFICATION_RESULT_REQUIRED_FIELDS if f not in vr]
    if missing:
        raise CanonicalizationErrorADP(f"VerificationResult missing required field(s): {missing}")
    if vr["resultVersion"] != VERIFICATION_RESULT_VERSION:
        raise CanonicalizationErrorADP(f"unsupported resultVersion: {vr['resultVersion']!r}")
    if vr["result"] not in ("PASS", "FAIL"):
        raise CanonicalizationErrorADP(f"VerificationResult.result must be PASS or FAIL, got {vr['result']!r}")


def verification_result_hash(vr: dict) -> str:
    return object_hash(_without(vr, "signature"))


def sign_verification_result(vr: dict, verifier_keypair: Keypair) -> dict:
    unsigned = _without(vr, "signature")
    signed = dict(vr)
    signed["signature"] = sign_object(unsigned, verifier_keypair)
    return signed


def verify_verification_result_signature(vr: dict, verifier_pubkey_b64u: str) -> bool:
    unsigned = _without(vr, "signature")
    return verify_object_signature(unsigned, vr["signature"], verifier_pubkey_b64u)


# ------------------------------------------------------- cross-object checks

def check_verifier_authorized(spec: dict, vr: dict) -> None:
    """§4.5 / §5.1(4): VerificationResult.verifierId MUST equal
    AcceptanceSpec.verifierAuthorization.verifierKeyId exactly."""
    expected = spec["verifierAuthorization"]["verifierKeyId"]
    if vr["verifierId"] != expected:
        raise UnauthorizedVerifier(
            f"VerificationResult.verifierId={vr['verifierId']!r} does not match "
            f"AcceptanceSpec.verifierAuthorization.verifierKeyId={expected!r}"
        )


def check_acceptance_spec_binding(bound_acceptance_spec_hash: str, vr: dict) -> None:
    """§3.5 / §5.1(2): the acceptanceSpecHash referenced by the
    VerificationResult MUST equal the hash bound into the owner
    mandate (AP2 x-adp.deal_reference constraint) at ACCEPTANCE_LOCKED
    time. `bound_acceptance_spec_hash` is that externally-bound value
    (this reference implementation does not implement AP2 itself —
    see README "Out of scope" — callers supply the bound hash)."""
    if vr["acceptanceSpecHash"] != bound_acceptance_spec_hash:
        raise AcceptanceSpecMismatch(
            f"VerificationResult.acceptanceSpecHash={vr['acceptanceSpecHash']!r} != "
            f"mandate-bound acceptanceSpecHash={bound_acceptance_spec_hash!r}"
        )


def check_within_validity(spec: dict, vr: dict) -> None:
    """§5.1(6): notBefore <= VerificationResult.timestamp <= notAfter."""
    nb = _parse_rfc3339(spec["validity"]["notBefore"])
    na = _parse_rfc3339(spec["validity"]["notAfter"])
    ts = _parse_rfc3339(vr["timestamp"])
    if not (nb <= ts <= na):
        raise VerificationExpired(
            f"VerificationResult.timestamp={vr['timestamp']!r} outside "
            f"AcceptanceSpec.validity [{spec['validity']['notBefore']}, {spec['validity']['notAfter']}]"
        )
