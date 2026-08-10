"""
BanglaMind — Database Connection
====================================
Supabase (PostgreSQL) অথবা SQLite (local dev) সংযোগ করে।

Environment variable:
  DATABASE_URL=postgresql://user:pass@host:5432/dbname

DATABASE_URL না থাকলে → SQLite ব্যবহার করে (local ফাইল)।
এভাবে DB ছাড়াও অ্যাপ পুরোপুরি কাজ করে।
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.app.database.models import Base

logger = logging.getLogger(__name__)

# ─── Connection URL ───────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Supabase ও অন্যান্য PostgreSQL সার্ভিস "postgres://" ব্যবহার করে
# কিন্তু SQLAlchemy-র জন্য "postgresql://" লাগে
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# psycopg2-binary "pgbouncer" অপশন সাপোর্ট করে না, তাই সেটা বাদ দিতে হবে
if "?pgbouncer=true" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?pgbouncer=true", "")
if "&pgbouncer=true" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("&pgbouncer=true", "")

# ─── Engine তৈরি করো ─────────────────────────────────────────
def _create_engine():
    if DATABASE_URL:
        logger.info("PostgreSQL (Supabase) সংযোগ করছি...")
        return create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,   # সংযোগ জীবিত আছে কি না চেক করে
            echo=False,
        )
    else:
        # Fallback: local SQLite
        base_dir  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path   = os.path.join(base_dir, "data", "banglamind.db")
        sqlite_url = f"sqlite:///{db_path}"
        logger.info(f"SQLite ব্যবহার করছি (local dev): {db_path}")
        return create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=False)


# ─── Singleton engine ─────────────────────────────────────────
try:
    engine         = _create_engine()
    SessionLocal   = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    DB_AVAILABLE   = True
    logger.info("Database engine তৈরি হয়েছে।")
except Exception as e:
    engine       = None
    SessionLocal = None
    DB_AVAILABLE = False
    logger.error(f"Database সংযোগ ব্যর্থ: {e}. JSON fallback mode চলছে।")


def init_db():
    """সব টেবিল তৈরি করো (যদি না থাকে)।"""
    if not DB_AVAILABLE:
        logger.warning("DB unavailable — init_db() skip করা হলো।")
        return False
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables ready!")
        return True
    except Exception as e:
        logger.error(f"init_db() ব্যর্থ: {e}")
        return False


def get_db() -> Session:
    """
    FastAPI Dependency Injection-এর জন্য।
    প্রতিটি request-এ একটি নতুন session দেয়।

    ব্যবহার:
        @router.get("/example")
        async def example(db: Session = Depends(get_db)):
            ...
    """
    if not DB_AVAILABLE or SessionLocal is None:
        raise RuntimeError("Database সংযোগ নেই।")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def health_check() -> dict:
    """Database connection স্বাস্থ্য পরীক্ষা করে।"""
    if not DB_AVAILABLE:
        return {"connected": False, "type": "none", "message": "JSON fallback mode"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "postgresql" if DATABASE_URL else "sqlite"
        return {"connected": True, "type": db_type, "message": "সংযোগ সফল"}
    except Exception as e:
        return {"connected": False, "type": "error", "message": str(e)}
