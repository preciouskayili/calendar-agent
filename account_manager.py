import os
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


class AccountManager:
    def __init__(self, client_secret_file: str = "credentials.json"):
        self.client_secret_file = client_secret_file
        self.accounts: Dict[str, Credentials] = {}
        self.token_dir = "token_files"

        # Ensure token directory exists
        if not os.path.exists(self.token_dir):
            os.makedirs(self.token_dir)

    def add_account(self, account_id: str) -> bool:
        """Add a new account by performing OAuth flow"""
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
        ]

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file, SCOPES
            )
            creds = flow.run_local_server(port=0, timeout=30)

            # Save credentials
            self.accounts[account_id] = creds
            self._save_credentials(account_id, creds)
            return True
        except Exception as e:
            print(f"Error adding account: {e}")
            return False

    def get_account(self, account_id: str) -> Optional[Credentials]:
        """Get credentials for an account"""
        if account_id in self.accounts:
            return self.accounts[account_id]

        # Try to load from file
        creds = self._load_credentials(account_id)
        if creds:
            self.accounts[account_id] = creds
            return creds

        return None

    def list_accounts(self) -> list:
        """List all available accounts"""
        return list(self.accounts.keys())

    def _save_credentials(self, account_id: str, creds: Credentials):
        """Save credentials to file"""
        token_file = os.path.join(self.token_dir, f"token_{account_id}.json")
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    def _load_credentials(self, account_id: str) -> Optional[Credentials]:
        """Load credentials from file"""
        token_file = os.path.join(self.token_dir, f"token_{account_id}.json")
        if not os.path.exists(token_file):
            return None

        try:
            SCOPES = [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
            ]
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._save_credentials(account_id, creds)

            return creds
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None


# Global instance
account_manager = AccountManager()
