import os
import dotenv

class ManualApiToken:
    def __init__(self, token: str):
        self.token = token

    def get_token(self) -> str:
        return self.token

class AutoApiToken:
    """
    Reads the API token from the DAILY_DEV_KEY environment variable or .env file.
    """
    def __init__(self):
        dotenv.load_dotenv()
        self.token = os.getenv("DAILY_DEV_KEY")
        if not self.token:
            raise ValueError(
                "DAILY_DEV_KEY is not set. Set it in your environment or .env file."
            )

    def get_token(self) -> str:
        return self.token