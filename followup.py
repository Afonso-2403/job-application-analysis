import pandas as pd


def get_needs_followup(
    applications_df: pd.DataFrame,
    days_with_communication: int = 7,
    days_without_communication: int = 14,
) -> pd.DataFrame:
    """Return pending applications that need follow-up.

    Uses differentiated thresholds:
    - `days_with_communication` for applications with a Last Communication Date.
    - `days_without_communication` for applications using Application Date as fallback.
    """
    # Find the Application Date column (name includes line break from spreadsheet)
    app_date_col = [col for col in applications_df.columns if col.startswith("Application Date")][0]

    # Filter applications where Offer is empty (no response yet)
    pending = applications_df[applications_df["Offer"].isna() | (applications_df["Offer"] == "")].copy()

    pending["Last Communication Date"] = pd.to_datetime(pending["Last Communication Date"], errors="coerce")
    pending[app_date_col] = pd.to_datetime(pending[app_date_col], errors="coerce")

    pending["Used_Application_Date"] = pending["Last Communication Date"].isna()
    pending["Effective Date"] = pending["Last Communication Date"].fillna(pending[app_date_col])
    pending["Days Since Contact"] = (pd.Timestamp.now() - pending["Effective Date"]).dt.days

    needs_followup = pending[
        (
            ((~pending["Used_Application_Date"]) & (pending["Days Since Contact"] > days_with_communication))
            | ((pending["Used_Application_Date"]) & (pending["Days Since Contact"] > days_without_communication))
        )
    ]

    return needs_followup
