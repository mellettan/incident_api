from databases import Database
from sqlalchemy import create_engine, MetaData
from src.core.config import settings

database = Database(settings.DATABASE_URL)
metadata = MetaData()

# Управляем БД через алембик. Тут engine для тестов, для создания таблиц перед запуском тестов
engine = create_engine(
    str(settings.DATABASE_URL).replace("+aiosqlite", ""),
    connect_args={"check_same_thread": False},
)
