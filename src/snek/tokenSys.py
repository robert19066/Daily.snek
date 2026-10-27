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

    def __init__(self, apienvkeyname: str = "DAILY_DEV_KEY"):
        dotenv.load_dotenv()
        self.token = os.getenv(apienvkeyname)
        if not self.token:
            raise ValueError(
                "Apienvkeyname is not set. Just type the name of your env variable with the token. "
            )

    def get_token(self) -> str:
        return self.token  # pyright: ignore[reportReturnType]
