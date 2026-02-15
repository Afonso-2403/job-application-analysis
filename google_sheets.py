import gspread
from pathlib import Path
import pandas as pd


def get_spreadsheet_data(sheet_name: str):
    gc = gspread.oauth(
        credentials_filename=f"{Path(__file__).parent}/.config/credentials.json",
        authorized_user_filename=f"{Path(__file__).parent}/.config/authorized_user.json"
    )

    sheet = gc.open(sheet_name).sheet1

    # The records start from row 6 (0-indexed)
    # The header row is row 4
    all_values = sheet.get_all_values()
    headers = all_values[4]
    data = all_values[6:]

    df = pd.DataFrame(data, columns=headers)

    return df


def update_column_value(
    sheet_name: str,
    filter_column: str,
    filter_value: str,
    target_column: str,
    new_value: str,
):
    """Update cells in the spreadsheet for rows matching a filter criteria.

    Args:
        sheet_name: Name of the Google Spreadsheet.
        filter_column: Column name to filter rows by.
        filter_value: Value to match in the filter column.
        target_column: Column name to update.
        new_value: New value to set in the target column.

    Returns:
        Number of rows updated.
    """
    gc = gspread.oauth(
        credentials_filename=f"{Path(__file__).parent}/.config/credentials.json",
        authorized_user_filename=f"{Path(__file__).parent}/.config/authorized_user.json",
    )

    sheet = gc.open(sheet_name).sheet1
    all_values = sheet.get_all_values()

    # Header row is at index 4 (0-indexed), data starts at index 6
    headers = all_values[4]
    data_start_index = 6

    if filter_column not in headers:
        raise ValueError(f"Filter column '{filter_column}' not found. Available: {headers}")
    if target_column not in headers:
        raise ValueError(f"Target column '{target_column}' not found. Available: {headers}")

    target_col_idx = headers.index(target_column)

    # Use pandas to find matching row indices, then batch update in one API call
    data = all_values[data_start_index:]
    df = pd.DataFrame(data, columns=headers)
    matching_indices = df.index[df[filter_column] == filter_value]

    if matching_indices.empty:
        return 0

    # Build batch update: convert df indices to gspread A1 notation
    target_col_letter = gspread.utils.rowcol_to_a1(1, target_col_idx + 1)[:-1]
    cells = [
        {"range": f"{target_col_letter}{data_start_index + i + 1}", "values": [[new_value]]}
        for i in matching_indices
    ]
    sheet.batch_update(cells)

    return len(matching_indices)

def delete_column(sheet_name: str, column_name: str):
    """Delete an entire column from the spreadsheet by its header name.

    Args:
        sheet_name: Name of the Google Spreadsheet.
        column_name: Header name of the column to delete (matched from header row 4).
    """
    gc = gspread.oauth(
        credentials_filename=f"{Path(__file__).parent}/.config/credentials.json",
        authorized_user_filename=f"{Path(__file__).parent}/.config/authorized_user.json",
    )

    sheet = gc.open(sheet_name).sheet1
    headers = sheet.row_values(5)  # Header row is index 4 (0-based), row 5 (1-based)

    if column_name not in headers:
        raise ValueError(f"Column '{column_name}' not found. Available: {headers}")

    col_idx = headers.index(column_name) + 1  # 1-indexed for gspread
    sheet.delete_columns(col_idx)
