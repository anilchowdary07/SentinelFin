"""
integrations/document_parser.py

SentinelFin Document Intelligence Engine
Parses AML-relevant documents into structured transaction data.

Supported formats:
  - PDF  (bank statements, SWIFT confirmations, corporate docs)
  - CSV  (transaction monitoring exports, core banking exports)
  - TXT  (SWIFT MT103/MT202 messages, correspondent bank messages)
  - JSON (API exports, structured transaction feeds)

When raw text is extracted, Llama 3.1 via AWS Bedrock performs intelligent
entity and transaction extraction — exactly how UiPath Document Understanding
works in production (ML-based field extraction → structured output).
"""

import io
import csv
import json
import re
import datetime
from typing import Optional

import pdfplumber

# ── SWIFT MT103 Parser ────────────────────────────────────────────────────────

def parse_swift_mt103(text: str) -> list[dict]:
    """
    Parse SWIFT MT103 (Customer Credit Transfer) and MT202 (Bank Transfer)
    messages into structured transaction objects.

    The MT103 format is used by SWIFT for international wire transfers.
    Real banks use this format for every correspondent banking transaction.
    """
    transactions = []
    messages = re.split(r'\{1:', text)

    for block in messages:
        if not block.strip():
            continue

        txn = {
            "txn_id":    "",
            "date":      datetime.datetime.utcnow().isoformat() + "Z",
            "amount":    0,
            "type":      "WIRE_TRANSFER",
            "originator": {},
            "beneficiary": {},
            "purpose":   "",
            "swift_raw": block[:300],
        }

        # :20: Transaction reference
        ref = re.search(r':20:([^\r\n:]+)', block)
        if ref:
            txn["txn_id"] = ref.group(1).strip()

        # :32A: Value date, currency, amount (e.g., 260610USD250000,)
        val_date = re.search(r':32A:(\d{6})([A-Z]{3})([\d,]+)', block)
        if val_date:
            d = val_date.group(1)
            try:
                txn["date"] = f"20{d[:2]}-{d[2:4]}-{d[4:6]}T09:00:00Z"
            except Exception:
                pass
            txn["currency"] = val_date.group(2)
            try:
                txn["amount"] = int(float(val_date.group(3).replace(",", ".")))
            except Exception:
                pass

        # :50K: / :50A: Ordering customer (originator)
        orig = re.search(r':50[AKF]:(/([^\r\n]+))?\r?\n([^\r\n:]+)?\r?\n?([^\r\n:]+)?', block)
        if orig:
            txn["originator"] = {
                "account": (orig.group(2) or "").strip(),
                "name":    (orig.group(3) or "Unknown").strip(),
                "country": (orig.group(4) or "").strip(),
            }

        # :59: / :59A: Beneficiary customer
        bene = re.search(r':59[A-Z]?:(/([^\r\n]+))?\r?\n([^\r\n:]+)?\r?\n?([^\r\n:]+)?', block)
        if bene:
            txn["beneficiary"] = {
                "account": (bene.group(2) or "").strip(),
                "name":    (bene.group(3) or "Unknown").strip(),
                "country": (bene.group(4) or "").strip(),
            }

        # :52A: / :57A: Correspondent bank
        corr = re.search(r':52[AD]:([^\r\n:]+)', block)
        if corr:
            txn["correspondent_bank"] = corr.group(1).strip()

        # :70: Remittance information (purpose)
        remit = re.search(r':70:([^\r\n:]+)', block)
        if remit:
            txn["purpose"] = remit.group(1).strip()

        if txn["txn_id"] or txn["amount"] > 0:
            if not txn["txn_id"]:
                txn["txn_id"] = f"SWIFT-{len(transactions)+1:03d}"
            transactions.append(txn)

    return transactions


# ── CSV / Excel Parser ────────────────────────────────────────────────────────

def parse_csv_transactions(content: str) -> list[dict]:
    """
    Parse CSV exports from:
    - Core banking systems (Temenos, FIS, Fiserv)
    - Transaction monitoring systems (NICE Actimize, FICO, Oracle FCCM)
    - Payment rails exports
    """
    transactions = []
    reader = csv.DictReader(io.StringIO(content))
    headers = [h.lower().strip() for h in (reader.fieldnames or [])]

    def find_col(candidates: list[str], row: dict) -> str:
        for c in candidates:
            for k in row:
                if c in k.lower():
                    return row[k] or ""
        return ""

    for i, row in enumerate(reader):
        amount_str = find_col(["amount", "value", "sum", "usd", "eur"], row)
        try:
            amount = int(float(re.sub(r'[^\d.]', '', amount_str or "0")))
        except Exception:
            amount = 0

        txn = {
            "txn_id":    find_col(["ref", "id", "txn", "transaction"], row) or f"CSV-{i+1:03d}",
            "date":      find_col(["date", "time", "timestamp", "value_date"], row) or datetime.datetime.utcnow().isoformat() + "Z",
            "amount":    amount,
            "type":      find_col(["type", "kind", "direction", "category"], row) or "WIRE",
            "originator": {
                "name":    find_col(["sender", "from", "originator", "payer", "debtor"], row),
                "account": find_col(["sender_acc", "from_acc", "debit_acc", "iban_from"], row),
                "country": find_col(["sender_country", "from_country", "origin"], row),
            },
            "beneficiary": {
                "name":    find_col(["receiver", "to", "beneficiary", "payee", "creditor"], row),
                "account": find_col(["receiver_acc", "to_acc", "credit_acc", "iban_to"], row),
                "country": find_col(["receiver_country", "to_country", "destination"], row),
            },
            "purpose":   find_col(["purpose", "description", "narrative", "details", "remit"], row),
        }

        # Normalize date
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
            try:
                dt = datetime.datetime.strptime(txn["date"][:10], fmt)
                txn["date"] = dt.isoformat() + "Z"
                break
            except Exception:
                pass

        if amount > 0 or txn["originator"]["name"]:
            transactions.append(txn)

    return transactions


# ── PDF Parser ────────────────────────────────────────────────────────────────

def parse_pdf(file_bytes: bytes) -> tuple[str, list[dict]]:
    """
    Extract text and attempt to parse transactions from PDF.
    Supports:
    - Bank statement PDFs
    - SWIFT MT confirmation letters
    - Corporate documents (ownership, registration)

    Returns (full_text, transactions_list)
    """
    full_text = ""
    transactions = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"

                # Try to parse tables from each page
                for table in (page.extract_tables() or []):
                    if not table:
                        continue
                    headers = [str(c).lower().strip() if c else "" for c in table[0]]
                    for row in table[1:]:
                        if not any(row):
                            continue
                        row_dict = {h: str(v).strip() if v else "" for h, v in zip(headers, row)}
                        # Check if this looks like a transaction row
                        amount_keys = [k for k in row_dict if any(x in k for x in ["amount", "value", "debit", "credit", "usd", "eur"])]
                        if amount_keys:
                            amount_str = row_dict.get(amount_keys[0], "0")
                            try:
                                amount = int(float(re.sub(r'[^\d.]', '', amount_str or "0")))
                            except Exception:
                                amount = 0
                            if amount > 0:
                                transactions.append({
                                    "txn_id":    row_dict.get("ref", row_dict.get("id", f"PDF-{len(transactions)+1:03d}")),
                                    "date":      row_dict.get("date", row_dict.get("value date", datetime.datetime.utcnow().isoformat() + "Z")),
                                    "amount":    amount,
                                    "type":      row_dict.get("type", "WIRE"),
                                    "originator": {"name": row_dict.get("from", row_dict.get("sender", "")) },
                                    "beneficiary": {"name": row_dict.get("to", row_dict.get("receiver", ""))},
                                    "source":    "PDF_TABLE",
                                })
    except Exception as e:
        full_text = f"[PDF parse error: {e}]"

    # Also try SWIFT format in the text
    if "{1:" in full_text or ":20:" in full_text:
        swift_txns = parse_swift_mt103(full_text)
        transactions.extend(swift_txns)

    return full_text, transactions


# ── AI-Powered Extraction (Llama 3.1 fallback) ───────────────────────────────

def extract_with_llm(document_text: str, llm_client) -> list[dict]:
    """
    When structured parsing fails, use Llama 3.1 to intelligently extract
    transaction data from unstructured text. This mirrors how UiPath's
    Document Understanding ML models work — reading any document and
    producing structured JSON output.
    """
    prompt = f"""You are an expert AML (Anti-Money Laundering) document analyst.
Extract ALL financial transactions from the following document.
Return ONLY valid JSON array, no other text.

Each transaction must follow this exact schema:
{{
  "txn_id": "unique reference (string)",
  "date": "ISO 8601 date string",
  "amount": numeric dollar amount (integer, no commas),
  "type": "WIRE_IN" or "WIRE_OUT" or "WIRE_TRANSFER" or "CRYPTO" or "CASH",
  "originator": {{"name": "sender name", "country": "country", "account": "account number"}},
  "beneficiary": {{"name": "recipient name", "country": "country", "account": "account number"}},
  "purpose": "stated purpose/description"
}}

If you cannot find a specific field, use empty string "".
Return [] if no transactions are found.

DOCUMENT:
{document_text[:8000]}

TRANSACTIONS JSON:"""

    try:
        response = llm_client.converse(
            modelId="meta.llama3-70b-instruct-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 2048, "temperature": 0.0},
        )
        raw = response["output"]["message"]["content"][0]["text"].strip()
        # Extract JSON array
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"[DOC PARSER] LLM extraction failed: {e}")

    return []


# ── Main Parser Entry Point ───────────────────────────────────────────────────

def parse_document(filename: str, file_bytes: bytes, llm_client=None) -> dict:
    """
    Main entry point for document parsing.
    Routes to the appropriate parser based on file extension.

    Returns:
        {
            "filename": str,
            "format": str,
            "raw_text": str,
            "transactions": list[dict],
            "entity_hints": list[str],
            "parse_method": str,
            "confidence": float,
        }
    """
    ext = filename.rsplit(".", 1)[-1].lower()
    raw_text = ""
    transactions = []
    parse_method = "unknown"

    print(f"[DOC PARSER] Processing '{filename}' (type: {ext}, size: {len(file_bytes)} bytes)")

    if ext == "pdf":
        raw_text, transactions = parse_pdf(file_bytes)
        parse_method = "PDF+SWIFT" if transactions else "PDF_TEXT"

    elif ext in ("csv", "tsv"):
        raw_text = file_bytes.decode("utf-8", errors="replace")
        transactions = parse_csv_transactions(raw_text)
        parse_method = "CSV"

    elif ext in ("txt", "swift", "mt103", "mt202"):
        raw_text = file_bytes.decode("utf-8", errors="replace")
        # Try SWIFT first
        transactions = parse_swift_mt103(raw_text)
        parse_method = "SWIFT_MT103" if transactions else "TEXT"

    elif ext == "json":
        raw_text = file_bytes.decode("utf-8", errors="replace")
        try:
            data = json.loads(raw_text)
            if isinstance(data, list):
                transactions = data
            elif isinstance(data, dict):
                transactions = data.get("transactions", [data])
            parse_method = "JSON"
        except Exception:
            parse_method = "JSON_INVALID"

    # If no transactions found, use LLM extraction
    if not transactions and raw_text and llm_client:
        print(f"[DOC PARSER] Structured parse found 0 transactions. Trying LLM extraction...")
        transactions = extract_with_llm(raw_text, llm_client)
        parse_method = f"{parse_method}+LLM"

    # Extract entity hints from raw text
    entity_hints = extract_entity_hints(raw_text)

    confidence = min(1.0, len(transactions) * 0.2 + 0.3) if transactions else 0.1

    print(f"[DOC PARSER] Extracted {len(transactions)} transactions via {parse_method} (confidence: {confidence:.0%})")
    return {
        "filename":     filename,
        "format":       ext.upper(),
        "raw_text":     raw_text[:2000],  # Preview only
        "transactions": transactions,
        "entity_hints": entity_hints,
        "parse_method": parse_method,
        "confidence":   confidence,
        "tx_count":     len(transactions),
    }


def extract_entity_hints(text: str) -> list[str]:
    """Extract probable entity names and account numbers from raw text."""
    hints = []
    # Look for IBAN-like patterns
    ibans = re.findall(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b', text)
    hints.extend(ibans[:5])
    # Look for capitalized company names
    companies = re.findall(r'\b([A-Z][a-z]+ (?:Corp|Ltd|LLC|GmbH|Holdings|Trading|Finance|Bank|Co|Inc)[,.]?)\b', text)
    hints.extend(companies[:5])
    return list(set(hints))[:10]


# ── Sample Documents for Demo ─────────────────────────────────────────────────

SAMPLE_SWIFT_MT103 = """{1:F01DEUTDEBBAXXX0000000000}{2:I103CITIUS33XXXXN}{3:{108:MT103}}{4:
:20:CAS2026007REF
:23B:CRED
:32A:260610USD250000,
:50K:/CY-999123
UNKNOWN ENTITY A
OFFSHORE DRIVE 1
GEORGE TOWN, CAYMAN ISLANDS
:52A:BOFAUS3N
:57A:CITIUS33
:59:/PA-888456
SHELL CORP B
PANAMA CITY, PANAMA
:70:INVESTMENT PORTFOLIO MANAGEMENT
:71A:SHA
-}{5:{CHK:ABCDEF123456}}
{1:F01DEUTDEBBAXXX0000000001}{2:I103CITIUS33XXXXN}{4:
:20:CAS2026007REF2
:23B:CRED
:32A:260611USD120000,
:50K:/ACC-554433
TRANSIT ACCOUNT
NEW YORK, USA
:59:/CP-777789
HOLDINGS C
LIMASSOL, CYPRUS
:70:CONSULTING FEES
:71A:SHA
-}
"""

SAMPLE_CSV = """ref,date,amount,type,sender,sender_account,sender_country,receiver,receiver_account,receiver_country,purpose
TXN-301,2026-06-08,890000,WIRE_IN,Aryan Trading Co,IR-445566,Iran,Global Import LLC,AE-112233,UAE,Trade goods payment
TXN-302,2026-06-09,870000,WIRE_OUT,Global Import LLC,AE-112233,UAE,Hezbollah Finance,LB-998877,Lebanon,Investment
TXN-303,2026-06-10,850000,WIRE_OUT,Hezbollah Finance,LB-998877,Lebanon,Offshore Shell X,VG-556644,BVI,Asset management
TXN-304,2026-06-11,820000,WIRE_OUT,Offshore Shell X,VG-556644,BVI,Final Corp Z,CH-334455,Switzerland,Portfolio rebalancing
"""

SAMPLE_JSON = json.dumps({
    "alert_type": "SUSPECTED_LAYERING",
    "alert_id": "CAS-2026-CRYPTO",
    "source_system": "NICE Actimize SAM",
    "transactions": [
        {"txn_id": "CRYPTO-001", "date": "2026-06-14T03:00:00Z", "amount": 2100000, "type": "CRYPTO_IN",
         "originator": {"name": "Tornado Cash Mixer", "country": "Decentralized", "account": "0xAB...FF11"},
         "beneficiary": {"name": "OTC Desk Alpha", "country": "Hong Kong", "account": "HK-OTC-001"}},
        {"txn_id": "CRYPTO-002", "date": "2026-06-14T06:30:00Z", "amount": 2050000, "type": "WIRE_OUT",
         "originator": {"name": "OTC Desk Alpha", "country": "Hong Kong", "account": "HK-OTC-001"},
         "beneficiary": {"name": "PJSC Gazprombank", "country": "Russia", "account": "RU-GAZP-999"}},
    ]
}, indent=2)
