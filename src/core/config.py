import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./incidents.db")
    DATABASE_TESTS_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./incidents_test.db")


settings = Settings()
