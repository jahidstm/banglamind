"""Database package init — makes `from backend.app.database import ...` work."""
from backend.app.database.connection import init_db, get_db, health_check, DB_AVAILABLE
from backend.app.database.models import Base, Business, Message, FAQ

__all__ = ["init_db", "get_db", "health_check", "DB_AVAILABLE", "Base", "Business", "Message", "FAQ"]
