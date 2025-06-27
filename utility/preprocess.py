import pandas as pd
from collections import defaultdict
import os
from openpyxl import load_workbook


def handle_non_tabular(path: str) -> bool:
    """
    Parses non-tabular Excel or CSV file with triplet-format rows.

    Args:
        path (str): Path to the file (.xlsx, .xls, .csv)

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[-1].lower()
    rows = []

    if ext == ".xlsx":
        wb = load_workbook(path, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))

    elif ext == ".xls":
        df = pd.read_excel(path, header=None, engine="xlrd")
        rows = df.values.tolist()

    elif ext == ".csv":
        df = pd.read_csv(path, header=None)
        rows = df.values.tolist()

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    date_row = rows[1]
    dates = list(date_row)[::3]

    date_to_entries = defaultdict(list)

    for row in rows[3:]:
        for i in range(0, len(row), 3):

            start_time = row[i]
            grade = row[i + 1]
            mould_size = row[i + 2]

            if grade is None or str(grade).strip() in ("-", "Grade"):
                continue

            entry = {
                "start_time": start_time,
                "grade": str(grade).strip(),
                "mould_size": mould_size,
            }

            try:
                date_key = dates[i // 3]
                if date_key:
                    date_to_entries[date_key].append(entry)
            except IndexError:
                continue

    # Save output
    os.makedirs("data/processed", exist_ok=True)
    processed_files = []
    for date, entries in date_to_entries.items():
        try:
            df = pd.DataFrame(entries)
            date_str = pd.to_datetime(date).strftime("%Y-%m-%d")
            output_path = f"data/processed/charge_schedule_{date_str}.csv"
            df.to_csv(output_path, index=False)
            processed_files.append(output_path)
        except Exception as e:
            return False

    return True


def sheet_to_pandas(path: str, skip=1) -> pd.DataFrame:
    """
    Load a spreadsheet (.xlsx, .xls, .csv) into a pandas DataFrame.
    Can be used for the simple case of a single sheet with tabular data:
    e.g. product_groups_monthly

    Args:
        path (str): Path to the spreadsheet file.

    Returns:
        pd.DataFrame: Parsed DataFrame.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[-1].lower()

    if ext == ".xlsx":
        return pd.read_excel(path, engine="openpyxl", skiprows=skip)

    elif ext == ".xls":
        return pd.read_excel(path, engine="xlrd", skiprows=skip)

    elif ext == ".csv":
        return pd.read_csv(path, encoding="utf-8", skiprows=skip)

    else:
        raise ValueError(f"Unsupported file format: {ext}")


def process_steel_grade(path: str, col_name: str = "Quality group") -> pd.DataFrame:
    """
    Load a spreadsheet (.xlsx, .xls, .csv) into a pandas DataFrame
    and process with forward fill and dropna.

    Args:
        path (str): Path to the spreadsheet file.

    Returns:
        pd.DataFrame: Parsed DataFrame.
    """
    df = sheet_to_pandas(path, 1)
    df = df.dropna(axis=1, how="all")
    df[col_name] = df[col_name].ffill()
    return df
