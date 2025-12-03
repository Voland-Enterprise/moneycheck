import os
from typing import Optional

import pandas as pd


def _infer_output_path(input_path: str) -> str:
    base, ext = os.path.splitext(input_path)
    return f"{base}_with_metrics{ext}"


def read_input(
    input_path: str,
    domain_column: str,
    sheet_name: Optional[str] = None,
    delimiter: str = ",",
    limit: Optional[int] = None,
) -> pd.DataFrame:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    _, ext = os.path.splitext(input_path.lower())
    if ext == ".csv":
        df = pd.read_csv(input_path, delimiter=delimiter)
    elif ext in {".xlsx", ".xls"}:
        df = pd.read_excel(input_path, sheet_name=sheet_name)
    else:
        raise ValueError("Unsupported file extension. Use CSV or XLSX.")

    if domain_column not in df.columns:
        raise ValueError(f"Domain column '{domain_column}' not found in the file.")

    if limit is not None:
        df = df.head(limit)

    return df


def write_output(df: pd.DataFrame, output_path: Optional[str]) -> str:
    path = output_path or _infer_output_path("output")
    _, ext = os.path.splitext(path.lower())

    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in {".xlsx", ".xls"}:
        df.to_excel(path, index=False)
    else:
        # default to xlsx if extension absent
        if not ext:
            path = f"{path}.xlsx"
            df.to_excel(path, index=False)
        else:
            raise ValueError("Unsupported output extension. Use CSV or XLSX.")

    return path


def build_output_path(input_path: str, provided_output: Optional[str]) -> str:
    if provided_output:
        return provided_output
    return _infer_output_path(input_path)
