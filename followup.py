import pandas as pd


def get_applications_that_need_followup(
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

def format_followup_report(needs_followup: pd.DataFrame) -> str:
    lines = []
    lines.append(f"Applications needing follow-up: {len(needs_followup)}")
    lines.append(f"  - With last communication (>7 days): {len(needs_followup[~needs_followup['Used_Application_Date']])}")
    lines.append(f"  - Without last communication (>14 days): {len(needs_followup[needs_followup['Used_Application_Date']])}")
    lines.append("")
    lines.append("=" * 80)

    for _, row in needs_followup.sort_values("Days Since Contact", ascending=False).iterrows():
        date_source = "Application Date" if row["Used_Application_Date"] else "Last Communication"
        lines.append(f"Company:      {row['Company']}")
        lines.append(f"Role:         {row['Role Title']}")
        lines.append(f"Days:         {row['Days Since Contact']} (based on {date_source})")
        comments = row["Comments"] if pd.notna(row["Comments"]) and row["Comments"] != "" else "N/A"
        lines.append(f"Comments:     {comments}")
        lines.append("-" * 80)

    return "\n".join(lines)
