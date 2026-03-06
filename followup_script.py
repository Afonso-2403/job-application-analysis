import os

from dotenv import load_dotenv
import pandas as pd
import requests

from google_sheets import open_google_sheet, get_applications_spreadsheet_data
from followup import get_applications_that_need_followup, format_followup_report

load_dotenv()


DOCUMENT_NAME = "Job_Application_Tracker"


def send_email(subject: str, body: str):
    api_key = os.environ["RESEND_API_KEY"]
    sender = os.environ["RESEND_SENDER_EMAIL"]
    recipient = os.environ["FOLLOWUP_RECIPIENT_EMAIL"]

    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "text": body,
        },
    )
    response.raise_for_status()


def main():
    spreadsheet = open_google_sheet(DOCUMENT_NAME, use_service_account=True)
    df = get_applications_spreadsheet_data(spreadsheet.sheet1)
    needs_followup = get_applications_that_need_followup(df)

    if needs_followup.empty:
        return

    report = format_followup_report(needs_followup)
    send_email("Job Applications - Follow-up Report", report)


if __name__ == "__main__":
    main()
