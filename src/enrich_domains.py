import argparse
import logging
from typing import Dict, Optional

import pandas as pd

from .ahrefs_client import AhrefsClient
from .config import THRESHOLD_ENV_WARNING, AppConfig, load_config
from .domain_normalizer import normalize_domain
from .file_io import build_output_path, read_input
from .moz_client import MozClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

AHREFS_DR = "Ahrefs_DR"
AHREFS_PR = "Ahrefs_PR"
AHREFS_KEYWORDS = "Ahrefs_Keywords"
MOZ_DA = "Moz_DA"
MOZ_PA = "Moz_PA"


class MetricCache:
    def __init__(self):
        self.store: Dict[str, Dict[str, Optional[float]]] = {}

    def get(self, domain: str) -> Optional[Dict[str, Optional[float]]]:
        return self.store.get(domain)

    def set(self, domain: str, metrics: Dict[str, Optional[float]]):
        self.store[domain] = metrics


def parse_args():
    parser = argparse.ArgumentParser(description="Enrich domains with Ahrefs and Moz metrics")
    parser.add_argument("--input", required=True, help="Path to input CSV/XLSX file")
    parser.add_argument("--output", help="Path to output file")
    parser.add_argument("--domain-column", default="domain", help="Column name with domains")
    parser.add_argument("--sheet", help="Sheet name for XLSX files")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter")
    parser.add_argument("--limit", type=int, help="Limit number of rows to process")
    return parser.parse_args()


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for column in [AHREFS_DR, AHREFS_PR, AHREFS_KEYWORDS, MOZ_DA, MOZ_PA]:
        if column not in df.columns:
            df[column] = None
    return df


def process_domain(
    domain: str,
    config: AppConfig,
    cache: MetricCache,
    ahrefs_client: Optional[AhrefsClient],
    moz_client: Optional[MozClient],
) -> Dict[str, Optional[float]]:
    cached = cache.get(domain)
    if cached is not None:
        return cached

    metrics = {"dr": None, "pr": None, "keywords": None, "da": None, "pa": None}

    if ahrefs_client:
        ahrefs_metrics = ahrefs_client.get_metrics(domain)
        metrics.update({"dr": ahrefs_metrics.get("dr"), "pr": ahrefs_metrics.get("pr"), "keywords": ahrefs_metrics.get("keywords")})
    else:
        log.warning("Skipping Ahrefs for %s: %s", domain, THRESHOLD_ENV_WARNING)

    if moz_client:
        moz_metrics = moz_client.get_metrics(domain)
        metrics.update({"da": moz_metrics.get("da"), "pa": moz_metrics.get("pa")})
    else:
        log.warning("Skipping Moz for %s: %s", domain, THRESHOLD_ENV_WARNING)

    cache.set(domain, metrics)
    return metrics


def main():
    args = parse_args()
    config = load_config()

    df = read_input(
        input_path=args.input,
        domain_column=args.domain_column,
        sheet_name=args.sheet,
        delimiter=args.delimiter,
        limit=args.limit,
    )
    df = prepare_dataframe(df)

    ahrefs_client = AhrefsClient(config.ahrefs) if config.ahrefs else None
    moz_client = MozClient(config.moz) if config.moz else None

    cache = MetricCache()
    total = len(df)
    log.info("Found %s rows to process", total)

    for index, raw_domain in enumerate(df[args.domain_column], start=1):
        normalized = normalize_domain(raw_domain, config.domain)
        if not normalized:
            log.warning("Skipping invalid domain at row %s: %s", index, raw_domain)
            continue

        metrics = process_domain(normalized, config, cache, ahrefs_client, moz_client)

        log.info("Processing %s/%s: %s", index, total, normalized)

        df.loc[index - 1, AHREFS_DR] = metrics.get("dr")
        df.loc[index - 1, AHREFS_PR] = metrics.get("pr")
        df.loc[index - 1, AHREFS_KEYWORDS] = metrics.get("keywords")
        df.loc[index - 1, MOZ_DA] = metrics.get("da")
        df.loc[index - 1, MOZ_PA] = metrics.get("pa")

    output_path = build_output_path(args.input, args.output)
    _, ext = output_path.lower().rsplit('.', 1) if '.' in output_path else (output_path, '')
    if ext == "csv":
        df.to_csv(output_path, index=False, sep=args.delimiter)
    elif ext in {"xlsx", "xls"}:
        df.to_excel(output_path, index=False)
    else:
        df.to_excel(f"{output_path}.xlsx", index=False)
        output_path = f"{output_path}.xlsx"

    log.info("Completed. Output saved to %s", output_path)


if __name__ == "__main__":
    main()
