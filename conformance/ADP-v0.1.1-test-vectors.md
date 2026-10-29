> Repository note: this document is the German-language v0.1.1 vector set, unchanged in substance (only internal file-system paths in cross-references were removed). Mentions of `ADP-v0.1.1.md`, `ADP-v0.1-test-vectors.md` and `ADP-v0.1-ERRATA.md` refer to internal German working documents that are not part of this release; their normative content is consolidated in the English specification. The English normative specification is `../spec/ADP-v0.1.2-EN.md`; its section 16 refers to this file. Licence: not yet decided.

# ADP v0.1.1 — Conformance Test Vectors — Errata-Release

Status: Entwurf, Grundlage für spätere Automatisierung. Gehört zu `ADP-v0.1.1.md`. Ersetzt `ADP-v0.1-test-vectors.md` (weiterhin unverändert archiviert). Siehe `ADP-v0.1-ERRATA.md` für die vollständige Herleitung jeder Wertänderung.

**Wichtig:** Alle Hash- und Signaturwerte in diesem Dokument wurden **tatsächlich berechnet**, mit einer **strikt RFC-8785-konformen** Kanonisierung (implementiert direkt aus dem RFC-Text, inklusive korrekter ECMAScript-Zahlenserialisierung — siehe §0 und `ADP-v0.1-ERRATA.md` Punkt 1) — nicht erfunden. Jeder Wert wurde durch unabhängiges Nachrechnen **und** Signaturprüfung verifiziert. Die verwendeten Schlüssel sind **ausschließlich Testschlüssel** und dürfen niemals produktiv verwendet werden.

**Cross-Language-Anspruch:** Jeder Vektor unten ist so angegeben, dass ihn ein Entwickler **ohne jeden Bezug zu Implementation A oder zu Python** — nur mit einem RFC-8785-fähigen JSON-Kanonisierer, SHA-256 und Ed25519 seiner Wahl — reproduzieren kann: Input-JSON, kanonische UTF-8-Bytes, SHA-256-Digest, Signing Input, Public Key, Signatur, erwartetes Verifikationsergebnis, erwartete Settlement-Entscheidung und (wo relevant) `chainHash`.

## 0. Erzeugungs- und Prüfmethode (damit Dritte reproduzieren können)

- **Canonicalization:** **RFC 8785 (JCS)**, vollständig, inklusive der ECMAScript-`Number::toString`-Zahlenregel (**ERRATA-korrigiert** gegenüber v0.1: `44.0` → `44`, nicht `44.0` — siehe `ADP-v0.1-ERRATA.md` Punkt 1). Referenzimplementierung: `implementations\python-reference\adp\canonical.py`, direkt aus dem RFC-Text implementiert (kein Drittanbieter-Paket).
- **Hash:** SHA-256, Ausgabe als Lowercase-Hex.
- **Signatur:** Ed25519 (RFC 8032) über die kanonisierten Bytes **ohne** das Feld `signature`.
- **Testschlüssel (NIEMALS PRODUKTIV VERWENDEN):**
  - Buyer/Verifier privater Schlüssel (32 Byte, hex): `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f`
  - Buyer/Verifier öffentlicher Schlüssel (Base64url, unpadded): `A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg`
  - (Ein zweiter, ungenutzter Provider-Testschlüssel wurde ebenfalls erzeugt, öffentlicher Teil: `dVxMuSVsp83ErP3Gz-7ahJAX5bn5UU6ZGRvWfgsNQnY` — in diesen Vektoren nicht weiter verwendet, da v0.1 keine Pflicht-`providerAck`-Signatur vorsieht, §3.6 der Hauptspezifikation.)
- **Nachrechenbarkeit:** Jeder Vektor unten enthält das vollständige signierte JSON-Objekt. Ein Prüfer entfernt das `signature`-Feld, kanonisiert nach obiger Methode, bildet SHA-256 (muss dem angegebenen `expectedObjectHash` entsprechen) und verifiziert `signature.sig` als Ed25519-Signatur über dieselben kanonisierten Bytes mit dem oben genannten öffentlichen Schlüssel.

---

## 1. Grunddaten (gemeinsam für alle T1-Vektoren)

| Größe | Wert |
|---|---|
| `dealId` | `8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f` |
| Subject-Präimage | `normalize-and-sum-csv-by-category:v1` (UTF-8-Bytes) |
| `subjectHash` | `9837630e92998ac2ead4300b63ecd9569db49b7ffb15e3a50d8f298f0ebc70cd` |
| Delivery-Inhalt (PASS-Fall) | `{"totals":{"A":120.5,"B":44.0}}` |
| kanonische Bytes (RFC 8785, PASS-Fall) | `{"totals":{"A":120.5,"B":44}}` |
| `deliveryHash` (PASS-Fall) — **ERRATA korrigiert** | `5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10` |
| Delivery-Inhalt (getampert, 1 Feld geändert: `44.0`→`44.1`) | `{"totals":{"A":120.5,"B":44.1}}` |
| kanonische Bytes (getampert) | `{"totals":{"A":120.5,"B":44.1}}` (44.1 ist nicht ganzzahlig — von der Korrektur nicht betroffen) |
| `deliveryHash` (getampert) — unverändert | `5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6` |

---

## 2. POSITIVE TESTS

### P1 — Canonicalization/Hash-Determinismus — **ERRATA: Erwartungswert korrigiert (echtes JCS-Zahlenformat)**
**Eingabe:** `{"totals": {"A": 120.5, "B": 44.0}}` in beliebiger Feld-/Leerzeichen-Reihenfolge, z. B. auch `{"totals":{"B":44.0,"A":120.5}}`.
**Erwartung:** Beide Eingaben ergeben nach RFC-8785-Kanonisierung identische Bytes `{"totals":{"A":120.5,"B":44}}` (beachte: `44.0` → `44`, siehe `ADP-v0.1.1.md` §6 Punkt 5) und identischen Hash `5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10`.
**Zweck:** Prüft, dass zwei unabhängige Implementierungen bei Key-Reordering **und** bei ganzzahligen Fließkommawerten denselben Hash erzeugen (Kernforderung §6 der Hauptspezifikation).

### P2 — `AcceptanceSpec` gültig, Hash korrekt, Signatur gültig — **ERRATA: `expectedHash`/Hash/Signatur korrigiert**
**Objekt:**
```json
{
  "specVersion": "adp-acceptance/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "subjectHash": "9837630e92998ac2ead4300b63ecd9569db49b7ffb15e3a50d8f298f0ebc70cd",
  "verificationMethod": {"type": "hash-equals", "algorithm": "sha-256", "canonicalization": "JCS-RFC8785"},
  "acceptanceCondition": {"expectedHash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"},
  "verifierAuthorization": {"mode": "designated-key", "verifierKeyId": "did:key:buyer-verifier-1", "verifierPubKey": "A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg"},
  "validity": {"notBefore": "2026-09-22T10:00:00Z", "notAfter": "2026-09-22T10:10:00Z"},
  "evidenceRequirements": ["delivery-hash"],
  "issuer": "agent:buyer-a.example",
  "signature": {"alg": "EdDSA", "kid": "did:key:buyer-a-1",
    "sig": "c6TdGJyg9rZnfV8_etSlodXCZSZr7EUMcyB-Ct2_QcOwabOW9EXnRPZisLKmQE-BI8gmjMbZr2vHUC-bEshLBQ"}
}
```
**Signing Input (kanonische Bytes ohne `signature`):**
```
{"acceptanceCondition":{"expectedHash":"5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"},"dealId":"8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f","evidenceRequirements":["delivery-hash"],"issuer":"agent:buyer-a.example","specVersion":"adp-acceptance/0.1","subjectHash":"9837630e92998ac2ead4300b63ecd9569db49b7ffb15e3a50d8f298f0ebc70cd","validity":{"notAfter":"2026-09-22T10:10:00Z","notBefore":"2026-09-22T10:00:00Z"},"verificationMethod":{"algorithm":"sha-256","canonicalization":"JCS-RFC8785","type":"hash-equals"},"verifierAuthorization":{"mode":"designated-key","verifierKeyId":"did:key:buyer-verifier-1","verifierPubKey":"A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg"}}
```
**Public Key (Issuer, Ed25519, Base64url):** `A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg`
**Erwartetes `acceptanceSpecHash`:** `a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d`
**Erwartete Signaturprüfung:** GÜLTIG (Ed25519, Public Key wie oben) — **verifiziert** (siehe §0).

### P3 — `VerificationResult` PASS, vollständig gültig — **ERRATA: Werte korrigiert**
**Objekt:**
```json
{
  "resultVersion": "adp-verification/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "acceptanceSpecHash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d",
  "deliveryHash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10",
  "verifierId": "did:key:buyer-verifier-1",
  "result": "PASS",
  "evidenceRefs": [{"type": "delivery-hash", "hash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"}],
  "timestamp": "2026-09-22T10:04:12Z",
  "nonce": "a1e3f9c2-4b7d-4e21-9a10-000000000001",
  "signature": {"alg": "EdDSA", "kid": "did:key:buyer-verifier-1",
    "sig": "8ZqhcPOb4_tMGG84ovW4dcoisiLheH43LpN1X5Hc_HzR-SbHLI5Iam_9yihglyoYtxUvGX1ltCvrNhfzVd4ABQ"}
}
```
**Signing Input (kanonische Bytes ohne `signature`):**
```
{"acceptanceSpecHash":"a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d","dealId":"8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f","deliveryHash":"5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10","evidenceRefs":[{"hash":"5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10","type":"delivery-hash"}],"nonce":"a1e3f9c2-4b7d-4e21-9a10-000000000001","result":"PASS","resultVersion":"adp-verification/0.1","timestamp":"2026-09-22T10:04:12Z","verifierId":"did:key:buyer-verifier-1"}
```
**Public Key (Verifier, Ed25519, Base64url):** `A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg` (im T1-Beispiel: Buyer agiert als eigener Verifier, siehe `verifierAuthorization`)
**Erwarteter Objekt-Hash:** `f04cddf009898aa361d6c033925ecfc06a0f7bb7382d5720afb5bb0e610911af`
**Erwartete Signaturprüfung:** GÜLTIG — **verifiziert**.
**Erwartetes Verification Result:** `PASS` (deliveryHash == AcceptanceSpec.acceptanceCondition.expectedHash).
**Erwartete Settlement-Entscheidung (§5.1) angewendet:** alle sieben Bedingungen erfüllbar ⇒ **ALLOWED (Settlement erlaubt).**

### P4 — `DealRecord`-`chainHash` unabhängig reproduzierbar — **ERRATA: Werte korrigiert**
**Eingabe (`entries`, absichtlich in unsortierter Reihenfolge gegeben, um Sortierpflicht zu testen; alle `type`-Werte sind paarweise verschieden, siehe §13.10 Punkt 1a):**
```json
[
  {"type": "x402.settlement", "hash": "bcd7b2ff52e703ec73de8603f71a0ccff8b5e41922107b7b35d966c561d22d5c"},
  {"type": "a2a.task", "hash": "9749c77a6ce453ed84e4c632473c1f2f2c8c508b40dd29554d4f0f758dbe705f"},
  {"type": "ap2.open_mandate", "hash": "a9471792f92278a53800b2858ab8f0f205dc9947fdb56d894d23dfed360616bf"},
  {"type": "adp.verification_result", "hash": "f04cddf009898aa361d6c033925ecfc06a0f7bb7382d5720afb5bb0e610911af"},
  {"type": "a2a.artifact", "hash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"},
  {"type": "adp.acceptance_spec", "hash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d"}
]
```
**Verfahren:** je `type` höchstens ein Eintrag (§13.10 Punkt 1a) → nach `type` aufsteigend sortieren (Unicode-Codepoint) → dann `accᵢ = SHA-256(accᵢ₋₁ ∥ bytes.fromhex(hashᵢ))`, `acc₀ = SHA-256(b"")`.
**Sortierte Reihenfolge (erwartet):** `a2a.artifact, a2a.task, adp.acceptance_spec, adp.verification_result, ap2.open_mandate, x402.settlement`
**Erwarteter `chainHash`:** `8690a4fa86ed8331bd54622a39212c6e46d2c7f1b5257a044ddeb516e9b9f7e2`
**Zweck:** Zeigt, dass zwei Parteien mit denselben sechs Hashes, aber unterschiedlicher Sammelreihenfolge, nach der normativen Sortierregel (§13.10 Punkt 1) denselben `chainHash` erzeugen — **verifiziert** durch zweifache, unabhängige Neuberechnung mit vertauschter Ausgangsreihenfolge (identisches Ergebnis).

---

## 3. NEGATIVE TESTS

### N1 — Delivery-Hash-Mismatch (T1-Negativtest, 1 Byte verändert) — **ERRATA: `acceptanceSpecHash`/Signatur korrigiert; `deliveryHash` unverändert (44.1 nicht ganzzahlig)**
**Eingabe:** Delivery-Inhalt `{"totals":{"A":120.5,"B":44.1}}` statt `{"totals":{"A":120.5,"B":44.0}}` (ein Wert um `0.1` verändert).
**Berechneter `deliveryHash`:** `5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6`
**Vergleich mit `AcceptanceSpec.acceptanceCondition.expectedHash`** (`5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10`): **UNGLEICH.**
**Erwartetes Ergebnis:** `VerificationResult.result = "FAIL"`, Fehlercode-Klasse äquivalent zu `DELIVERY_HASH_MISMATCH` bei jeder Fremdprüfung.
**`VerificationResult` (FAIL, vollständig, signiert):**
```json
{
  "resultVersion": "adp-verification/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "acceptanceSpecHash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d",
  "deliveryHash": "5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6",
  "verifierId": "did:key:buyer-verifier-1",
  "result": "FAIL",
  "evidenceRefs": [{"type": "delivery-hash", "hash": "5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6"}],
  "timestamp": "2026-09-22T10:04:12Z",
  "nonce": "a1e3f9c2-4b7d-4e21-9a10-000000000002",
  "signature": {"alg": "EdDSA", "kid": "did:key:buyer-verifier-1",
    "sig": "4pSx1t0FNjzKNHCxCPN2vq6I5-Dr7n4AeBufZgJWZPHdhxcCKUZuOyhDQtAq5ZHLexz4e1Z0Up3AgoL-VQCmDQ"}
}
```
**Erwarteter Objekt-Hash:** `c530273dc816fa4ac9ba7fae1016f272b41a3c4b1d8a542e72a62f7237dbdc94`
**Erwartete Signaturprüfung:** GÜLTIG (die Signatur selbst ist korrekt — sie bescheinigt korrekt ein FAIL) — **verifiziert**.
**Erwartete Settlement-Entscheidung (§5.2) angewendet:** `result = FAIL` ⇒ **DENIED (Settlement NIEMALS erlaubt)**, unabhängig von der Gültigkeit der Signatur.

### N2 — `ACCEPTANCE_SPEC_MISMATCH` — **ERRATA: referenzierter korrekter Hash aktualisiert**
**Szenario:** Ein `VerificationResult` referenziert `acceptanceSpecHash = "0000000000000000000000000000000000000000000000000000000000000"` (nicht der tatsächliche Hash aus P2).
**Erwartung:** Der im AP2-Mandat gebundene `x-adp.deal_reference.acceptanceSpecHash` (`a371ac92c8…`) stimmt nicht überein ⇒ Fehler `ACCEPTANCE_SPEC_MISMATCH`, **kein** Settlement, unabhängig vom `result`-Feld.

### N3 — `UNAUTHORIZED_VERIFIER` — **ERRATA: Prüfreihenfolge präzisiert, siehe §4.5 in `ADP-v0.1.1.md`**
**Szenario:** Ein `VerificationResult` mit identischem Inhalt wie P3, aber `verifierId: "did:key:someone-else"` und signiert mit einem **anderen** privaten Schlüssel als dem in `AcceptanceSpec.verifierAuthorization.verifierPubKey` hinterlegten.
**Erwartung:** Der Identitätsabgleich `verifierId ≠ verifierAuthorization.verifierKeyId` **MUSS vor** der Signaturprüfung erfolgen (§4.5-Präzisierung) ⇒ Fehler `UNAUTHORIZED_VERIFIER` **unabhängig davon, ob die Signatur (mit dem falschen Schlüssel) technisch gültig wäre**, **kein** Settlement. Eine Implementierung, die stattdessen zuerst gegen den in der Spec benannten Schlüssel signaturprüft, würde hier korrekt `INVALID_SIGNATURE` melden (die fremde Signatur passt nicht zum designierten Schlüssel) — beide Implementierungen lehnen ab, aber nur die erste ist ADP-v0.1.1-konform in ihrem **Fehlercode**.

### N4 — Signatur-Tampering nach dem Signieren — **ERRATA: Werte korrigiert**
**Szenario:** Das gültige P3-Objekt wird genommen, danach **wird nur das Feld `result` von `"PASS"` auf `"FAIL"` geändert**, ohne neu zu signieren (Signatur bleibt die alte aus P3).
**Neu berechneter Objekt-Hash (ohne `signature`, mit geändertem `result`):** `b8c1a237b4bf356e415f7280b9a0e02daf66798c099b712e8df7891193044b94`
**Vergleich mit der ursprünglich signierten Nachricht (Hash `f04cddf009898aa361d6c033925ecfc06a0f7bb7382d5720afb5bb0e610911af`):** **UNGLEICH.**
**Erwartung:** Signaturprüfung schlägt fehl (die alte Signatur passt nicht zu den neuen, kanonisierten Bytes) ⇒ Fehler `INVALID_SIGNATURE`. **Verifiziert:** Ja — der neu berechnete Hash unterscheidet sich nachweislich vom Original, wodurch `Ed25519.verify(sig_original, neue_bytes)` fehlschlägt.

### N5 — Replay (identische `nonce` zweimal für denselben `dealId`) — unverändert (keine Hashwerte betroffen)
**Szenario:** Zwei `VerificationResult`-Objekte mit identischem `dealId` **und** identischem `nonce` (`a1e3f9c2-4b7d-4e21-9a10-000000000001`), aber unterschiedlichem `timestamp`.
**Erwartung:** Das zweite Objekt **MUSS** verworfen werden (§4.6) — unabhängig davon, ob seine Signatur gültig ist.

### N6 — `ALREADY_SETTLED` (Double-Settlement-Versuch) — unverändert (referenziert P3 begrifflich, keine Hashwerte im Text)
**Szenario:** Nach erfolgreicher Konsumierung von P3 (Settlement ausgelöst) wird ein **zweites**, ebenfalls gültiges `VerificationResult` mit **neuer** `nonce`, aber identischem `dealId` **und** identischem `acceptanceSpecHash` und `result: PASS` vorgelegt.
**Erwartung:** Der Payment-Adapter **MUSS** dies mit `ALREADY_SETTLED` ablehnen (§5.6), obwohl das Objekt für sich genommen technisch gültig wäre.

### N7 — Abgelaufene Gültigkeit — unverändert
**Szenario:** `VerificationResult.timestamp = "2026-09-22T10:15:00Z"` (nach `AcceptanceSpec.validity.notAfter = "2026-09-22T10:10:00Z"`).
**Erwartung:** Fehler `VERIFICATION_EXPIRED`, **kein** Settlement — unabhängig von `result`. Zustand geht nach `REJECTED` über (§5.3, §8).

### N8 — Deal-ID-Kollision — unverändert
**Szenario:** Eine zweite `AcceptanceSpec` mit identischem `dealId = "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f"`, aber anderem `subjectHash` und anderem `issuer`, wird bei einem Teilnehmer eingereicht, der bereits die P2-Spec für diesen `dealId` kennt.
**Erwartung:** Fehler `DEAL_ID_COLLISION` (§2.3) — die zweite Spec **MUSS** abgelehnt werden.

### N9 — `chainHash`-Tampering-Erkennung im `DealRecord` — **ERRATA: Werte korrigiert**
**Szenario:** In der Eintragsliste aus P4 wird der Eintrag `a2a.artifact` durch den **getamperten** Delivery-Hash (`5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6` statt `5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10`) ersetzt.
**Erwarteter `chainHash` (getampert):** `40be016aed3772df4a55fd8ce9982728a43947bca62d46ee0037b349547e6397`
**Vergleich mit dem Original-`chainHash`** (`8690a4fa86ed8331bd54622a39212c6e46d2c7f1b5257a044ddeb516e9b9f7e2`): **UNGLEICH** — **verifiziert**, damit erkennbar unterschiedlich, jede nachträgliche Veränderung eines referenzierten Hashes ändert den `chainHash` deterministisch.

### N10 — `DUPLICATE_ENTRY_TYPE` im `DealRecord` (ERRATA, neu — siehe `ADP-v0.1-ERRATA.md` Punkt 3)
**Szenario:** Die Eintragsliste aus P4 wird um einen **zweiten** Eintrag mit bereits vorhandenem `type` ergänzt: `{"type": "a2a.artifact", "hash": "0101010101010101010101010101010101010101010101010101010101010101"}`
(64-mal `01`, ein beliebiger, syntaktisch gültiger, aber inhaltlich irrelevanter zweiter Hash für denselben Typ).
**Erwartung:** Nach §13.10 Punkt 1a **MUSS** die `chainHash`-Berechnung verweigert werden — das `DealRecord` gilt als ungültig, **bevor** überhaupt sortiert oder gehasht wird. Es gibt **keinen** erwarteten `chainHash`-Wert für diesen Fall.

---

## 4. Testvektor-Zusammenfassung (Tabelle für Automatisierung)

| ID | Typ | Objekt | Erwartetes Ergebnis |
|---|---|---|---|
| P1 | Positiv | Delivery-JSON (Key-Reordering) | Hash `5770e1a4…f83d10` in beiden Fällen |
| P2 | Positiv | `AcceptanceSpec` | Hash `a371ac92…18633d`, Signatur gültig |
| P3 | Positiv | `VerificationResult` PASS | Hash `f04cddf0…10911af`, Signatur gültig, Settlement ALLOWED |
| P4 | Positiv | `DealRecord`-Einträge (unsortiert, eindeutige Typen) | `chainHash 8690a4fa…9b9f7e2`, reihenfolgeunabhängig |
| N1 | Negativ | `VerificationResult` mit getampertem Delivery | `result: FAIL`, Settlement DENIED |
| N2 | Negativ | falscher `acceptanceSpecHash` | `ACCEPTANCE_SPEC_MISMATCH` |
| N3 | Negativ | falscher `verifierId`/Schlüssel | `UNAUTHORIZED_VERIFIER` (geprüft vor Signatur, §4.5) |
| N4 | Negativ | Feld nach Signatur verändert | `INVALID_SIGNATURE` (Hash weicht ab: `b8c1a237…3044b94` ≠ Original) |
| N5 | Negativ | doppelte `nonce` | zweites Result verworfen |
| N6 | Negativ | zweites gültiges PASS nach Settlement | `ALREADY_SETTLED` |
| N7 | Negativ | `timestamp` nach `notAfter` | `VERIFICATION_EXPIRED` |
| N8 | Negativ | `dealId`-Wiederverwendung mit anderem Inhalt | `DEAL_ID_COLLISION` |
| N9 | Negativ | getamperter `DealRecord`-Eintrag | `chainHash` weicht ab: `40be016a…9547e6397` ≠ Original |
| N10 | Negativ | doppelter `entries[].type` | `DealRecord` ungültig, keine `chainHash`-Berechnung (ERRATA, neu) |

**14 Testvektoren** (4 positiv, 10 negativ — ein Vektor mehr als v0.1: N10 ist neu, siehe `ADP-v0.1-ERRATA.md` Punkt 3). Alle Hash-/Signaturwerte real berechnet mit strikter RFC-8785-Kanonisierung und mindestens einmal unabhängig nachgerechnet (Erzeugungsprotokoll: `research\vectors_v011\gen.py`, ausgeführt am 22.09.2026; Implementation-A-Konformitätslauf: `implementations\python-reference\CONFORMANCE.md`).
