import os
from dotenv import load_dotenv
from pathlib import Path

# Do not initialize config here. It will be initialized in the fixture.
class Config:
    def __init__(self, env: str = "dev"):
        self.env = env
        self._load_environment()

    def _load_environment(self):
        """Load environment variables from the correct .env file."""
        env_file = Path(__file__).parent / "environments" / f".env.{self.env}"
        if not env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {env_file}")
        load_dotenv(env_file, override=True)
        print(f"Loaded environment variables from: {env_file}")

    @property
    def facebook_base_url(self):
        """Get the base URL from environment variables."""
        url = os.getenv("FACEBOOK_BASE_URL")
        if not url:
            raise ValueError(f"FACEBOOK_BASE_URL not found in .env.{self.env} file")
        return url

    @property
    def timeout(self):
        """Get the timeout value from environment variables."""
        return int(os.getenv("TIMEOUT", "30"))

    @property
    def browserstack_username(self):
        """Get BrowserStack username from environment variables."""
        username = os.getenv("BROWSERSTACK_USERNAME")
        if not username:
            raise ValueError(f"BROWSERSTACK_USERNAME not found in .env.{self.env} file")
        return username

    @property
    def browserstack_access_key(self):
        """Get BrowserStack access key from environment variables."""
        access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
        if not access_key:
            raise ValueError(f"BROWSERSTACK_ACCESS_KEY not found in .env.{self.env} file")
        return access_key

    @property
    def lambdatest_username(self):
        """Get LambdaTest username from environment variables."""
        username = os.getenv("LT_USERNAME")
        if not username:
            raise ValueError(f"LT_USERNAME not found in .env.{self.env} file")
        return username

    @property
    def lambdatest_access_key(self):
        """Get LambdaTest access key from environment variables."""
        access_key = os.getenv("LT_ACCESS_KEY")
        if not access_key:
            raise ValueError(f"LT_ACCESS_KEY not found in .env.{self.env} file")
        return access_key