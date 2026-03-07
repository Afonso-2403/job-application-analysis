## Setup
The setup to access Google Sheets through this app was the [one available on gspread](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project) with the OAuth Client ID option.

The credentials are stored locally in the .config directory, and the only user with access to this project is me.

### Service account

For automation, it is necessary to have a service account so that there is no manual authentication step.  
To set this up, a service account was created, and access to the spreadsheet was given to this account.  
To send emails [resend](https://resend.com/emails) was used, with the simplest setup that only allows to send emails to my account.