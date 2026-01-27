import gspread
from pathlib import Path
import pandas as pd

SHEET_NAME = "Job_Application_Tracker"


def get_spreadsheet_data():
    gc = gspread.oauth(
        credentials_filename=f"{Path(__file__).parent}/.config/credentials.json",
        authorized_user_filename=f"{Path(__file__).parent}/.config/authorized_user.json"
    )

    sheet = gc.open(SHEET_NAME).sheet1

    # The records start from row 6 (0-indexed)
    # The header row is row 4
    all_values = sheet.get_all_values()
    headers = all_values[4]
    data = all_values[6:]

    df = pd.DataFrame(data, columns=headers)
    
    return df
