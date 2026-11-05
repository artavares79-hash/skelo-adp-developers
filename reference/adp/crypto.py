"""Ed25519 signing/verification (RFC 8032), per ADP-v0.1.md §7.

ADP defines no identity system (§7.3): a keyId ("kid") is an opaque,
externally-resolved reference. This module only implements the
signature *binding* mechanics (§7.2 envelope), never identity
resolution — callers pass in the already-resolved public key bytes.

No custom cryptography: this is a thin wrapper around the `cryptography`
package's Ed25519 primitives.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature as _CryptoInvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization

from .canonical import canonicalize
from .errors import InvalidSignature


def b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64u_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


@dataclass(frozen=True)
class Keypair:
    """A test/reference Ed25519 keypair. NEVER use keys generated or
    stored by this reference implementation for anything but ADP
    conformance testing."""

    kid: str
    private_key: Ed25519PrivateKey

    @property
    def public_key_b64u(self) -> str:
        pub = self.private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        return b64u_encode(pub)

    @classmethod
    def from_seed(cls, kid: str, seed32: bytes) -> "Keypair":
        if len(seed32) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes")
        return cls(kid=kid, private_key=Ed25519PrivateKey.from_private_bytes(seed32))

    @classmethod
    def generate(cls, kid: str) -> "Keypair":
        return cls(kid=kid, private_key=Ed25519PrivateKey.generate())


def sign_object(obj: dict, keypair: Keypair) -> dict:
    """Return the ADP-v0.1.md §7.2 signature envelope for `obj`.

    `obj` MUST already have its `signature` (and `providerAck`, if any)
    field(s) removed by the caller — this function signs exactly the
    dict it is given, per §6 point 2's "exclude before canonicalizing"
    rule, which is the caller's responsibility to have applied.
    """
    msg = canonicalize(obj)
    sig = keypair.private_key.sign(msg)
    return {"alg": "EdDSA", "kid": keypair.kid, "sig": b64u_encode(sig)}


def verify_object_signature(obj_without_signature: dict, signature: dict, public_key_b64u: str) -> bool:
    """Verify signature envelope against obj_without_signature (must
    already have 'signature'/'providerAck' stripped, per §6 point 2).
    Returns True/False; raises InvalidSignature only via
    `require_valid_signature` below, so callers that just want a
    boolean can call this directly."""
    if signature.get("alg") != "EdDSA":
        return False
    try:
        pub = Ed25519PublicKey.from_public_bytes(b64u_decode(public_key_b64u))
        pub.verify(b64u_decode(signature["sig"]), canonicalize(obj_without_signature))
        return True
    except (_CryptoInvalidSignature, ValueError, KeyError):
        return False


def require_valid_signature(obj_without_signature: dict, signature: dict, public_key_b64u: str) -> None:
    if not verify_object_signature(obj_without_signature, signature, public_key_b64u):
        raise InvalidSignature(
            f"signature by kid={signature.get('kid')!r} does not verify "
            "against the provided public key and canonicalized object"
        )
