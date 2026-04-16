import base64
import os
from email.message import EmailMessage

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


GMAIL_SEND_SCOPE = ["https://www.googleapis.com/auth/gmail.send"]


def _load_gmail_credentials():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Google API packages are not installed. Run 'pip install -r requirements.txt'."
        ) from exc

    token_path = settings.GMAIL_API_TOKEN_FILE
    credentials_path = settings.GMAIL_API_CREDENTIALS_FILE
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SEND_SCOPE)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
        return creds

    if creds and creds.valid:
        return creds

    if not os.path.exists(credentials_path):
        raise ImproperlyConfigured(
            "gmail_credentials.json was not found. Download an OAuth desktop app "
            "credentials file from Google Cloud and save it to the project root, "
            "or set GMAIL_API_CREDENTIALS_FILE."
        )

    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, GMAIL_SEND_SCOPE)
    creds = flow.run_local_server(port=0)
    with open(token_path, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())
    return creds


def send_gmail_api_message(to_email, subject, body):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Google API packages are not installed. Run 'pip install -r requirements.txt'."
        ) from exc

    creds = _load_gmail_credentials()
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to_email
    message["From"] = settings.GMAIL_API_SENDER
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service = build("gmail", "v1", credentials=creds)
        return (
            service.users()
            .messages()
            .send(userId="me", body={"raw": encoded_message})
            .execute()
        )
    except HttpError as exc:
        raise ImproperlyConfigured(f"Gmail API send failed: {exc}") from exc
