# Moneycheck Domain Enrichment

This repository contains a Python CLI that enriches domain lists with Ahrefs and Moz metrics.

## Requirements
- Python 3.10+
- Dependencies from `requirements.txt` (`pip install -r requirements.txt`)
- API credentials in environment variables or a local `.env`:
  - `AHREFS_API_TOKEN`
  - `MOZ_ACCESS_ID`
  - `MOZ_SECRET_KEY`

## Running the CLI
The main entry point is `src/enrich_domains.py`.

```bash
python -m src.enrich_domains \
  --input domains.xlsx \
  --output domains_with_metrics.xlsx \
  --domain-column domain
```

Supported options:
- `--input` (required): path to CSV/XLSX with a `domain` column (or use `--domain-column`).
- `--output`: explicit output path; defaults to adding `_with_metrics` to the input name.
- `--domain-column`: column containing domains (default: `domain`).
- `--sheet`: sheet name for XLSX input.
- `--delimiter`: CSV delimiter (default `,`).
- `--limit`: maximum number of rows to process (for quick tests).

During execution the script normalizes each domain, caches duplicate lookups, and logs progress plus any API warnings.

## Why is `index.php` empty?
`index.php` is only a placeholder; the project logic lives in the Python CLI under `src/`. The PHP file remains empty because there is no web front-end in this repository. If you need a PHP entry point later, you can repurpose or remove it without affecting the current workflow.
