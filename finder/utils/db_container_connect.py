from django.conf import settings
from sqlalchemy import create_engine


def get_db_engine():
    """Создает и возвращает SQLAlchemy engine"""
    db_url = (
        f"postgresql://{settings.DATABASES['default']['USER']}:"
        f"{settings.DATABASES['default']['PASSWORD']}@"
        f"db:{settings.DATABASES['default']['PORT']}/"
        f"{settings.DATABASES['default']['NAME']}"
    )
    return create_engine(db_url)