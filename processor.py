import csv
import io
import os
from datetime import datetime
from openai import OpenAI

# DeepSeek client placeholder (not used in the demo phase)
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com"
        )
    return _client


def process_file(file_bytes: bytes) -> list[dict]:
    """Process file bytes (CSV assumed) and return a list of extraction records.

    Returns:
        list[dict]: each dict has keys:
            title (str)     – primary entity (vendor name)
            status (str)    – one of: overdue:critical, paid:good, pending:warning, discrepancy:critical
            details (dict)  – additional extracted fields
            due_date (str)  – ISO‑8601 date string or None
    """
    records = []

    # Decode bytes to text
    try:
        text = file_bytes.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode('latin-1').strip()
        except Exception:
            return records   # not text, return empty

    # Attempt CSV parsing
    try:
        sample = text[:4096]
        dialect = csv.Sniffer().sniff(sample)
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        if not reader.fieldnames:
            return records

        # Normalise field names
        fieldnames = [f.strip().lower() for f in reader.fieldnames]

        for raw_row in reader:
            row = {k.strip().lower(): v.strip() for k, v in raw_row.items()}

            vendor = (row.get('vendor') or row.get('name') or
                      row.get('supplier') or row.get('payee') or 'Unknown')
            status_raw = row.get('status', '')
            amount = row.get('amount', '0')
            due_date_str = (row.get('due_date') or row.get('due date') or
                            row.get('date'))

            # Map status
            status = map_status(status_raw)

            # Parse due_date to ISO
            due_date_iso = None
            if due_date_str:
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                    try:
                        due_date_iso = datetime.strptime(due_date_str, fmt).date().isoformat()
                        break
                    except ValueError:
                        continue

            records.append({
                "title": vendor,
                "status": status,
                "details": {
                    "amount": amount,
                    "due_date": due_date_iso,
                    "raw": dict(raw_row)
                },
                "due_date": due_date_iso
            })

    except Exception:
        # Not valid CSV – in a full implementation we could send the text to
        # the DeepSeek LLM for extraction, but that is out of scope for the demo.
        pass

    return records


def map_status(status_str: str) -> str:
    """Map a human‑readable status string to the required exact status code."""
    s = status_str.strip().lower()
    if s in ('overdue', 'critical', 'overdue:critical'):
        return 'overdue:critical'
    if s in ('paid', 'good', 'paid:good'):
        return 'paid:good'
    if s in ('pending', 'warning', 'pending:warning'):
        return 'pending:warning'
    if s in ('discrepancy', 'discrepancy:critical'):
        return 'discrepancy:critical'
    return 'pending:warning'   # default safe value


def extract_with_llm(text: str) -> list[dict]:
    """Future DeepSeek‑powered extraction (not implemented in this phase)."""
    # client = _get_client()
    # …
    return []
