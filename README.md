# UK/EU SMB Late Payment Admin Auto-Chaser & Statement Reconciliation Tool

Backend extraction module for a product that helps UK/EU SMBs automate late-payment chasing and statement reconciliation. It ingests supplier payment statements, maps each invoice to a canonical status, and returns structured records ready for downstream automation (email chasers, ledger reconciliation, dashboards).

## Archetype

This repository is the **backend processor** portion of the product. It is responsible for parsing incoming statement files and normalizing them into a consistent schema. A future phase will add DeepSeek-powered LLM extraction for unstructured documents.

## Poller Input Contract

The poller (or any caller) invokes the processing function with raw file bytes. In the demo phase, the file is expected to be CSV with a header row. Supported columns:

- `vendor`, `name`, `supplier`, or `payee` – primary entity (invoice title)
- `amount` – invoice amount
- `due_date`, `due date`, or `date` – due date (ISO `YYYY-MM-DD`, `DD/MM/YYYY`, or `MM/DD/YYYY`)
- `status` – human-readable status

### Status Mapping

| Input | Canonical Output |
| --- | --- |
| overdue, critical | `overdue:critical` |
| paid, good | `paid:good` |
| pending, warning | `pending:warning` |
| discrepancy | `discrepancy:critical` |
| unknown/missing | `pending:warning` |

## Output Schema

Each record contains:

- `title` (str) – primary entity (vendor name)
- `status` (str) – one of `overdue:critical`, `paid:good`, `pending:warning`, `discrepancy:critical`
- `details` (dict) – amount, normalized due date, and raw row data
- `due_date` (str) – ISO-8601 date or `None`

## Usage

```bash
pip install -r requirements.txt
python3 run_demo.py
python3 run_tests.py
```

## Files

- `processor.py` – core CSV extraction and status mapping
- `run_demo.py` – zero-argument demo with hardcoded CSV
- `run_tests.py` – unit tests
- `requirements.txt` – `openai`, `requests`

Dashboard: https://uk-eu-smb-late-payment-admin-auto-chaser.vokrix.co
Vercel: uk-eu-smb-late-payment-admin-auto-chaser
Railway: 4d9ed47b-2a0b-4144-bd21-7c68b3f538b5
Railway: uk-eu-smb-late-payment-admin-auto-chaser
Cloudflare: uk-eu-smb-late-payment-admin-auto-chaser.vokrix.co


Billing: price_1U02kK2c9uGCcgMSEFFm1lrt

Landing: https://vokrix.co/uk-eu-smb-late-payment-admin-auto-chaser
