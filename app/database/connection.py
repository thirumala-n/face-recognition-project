from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
import pymysql
from app.config import settings
from app.core.logging_config import logger

Base = declarative_base()

# Primary application engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Tests connection liveness before checking out from pool
    pool_recycle=3600,   # Recycle connections older than 1 hour
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request.
    Analogous to Spring's @Transactional or EntityManager request scoping.
    Guarantees session closure in the finally block.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database_if_not_exists():
    """
    Connects to MySQL server instance without specifying DB name
    and creates the target database if it does not already exist.
    """
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT,
            charset="utf8mb4"
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        connection.commit()
        connection.close()
        logger.info(f"Database `{settings.DB_NAME}` verified / ready.")
    except Exception as e:
        logger.warning(f"Could not auto-create database `{settings.DB_NAME}`: {e}")

def init_db():
    """
    Ensures target database exists and creates all ORM schema tables.
    Models MUST be imported here before create_all so SQLAlchemy's
    metadata registry knows about all table definitions.
    """
    # Import all models to register them on Base.metadata
    from app.models.student import Student      # noqa: F401
    from app.models.attendance import Attendance  # noqa: F401
    from app.models.user import User            # noqa: F401

    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
