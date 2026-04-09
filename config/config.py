import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "..", "servicesync_dev.db"),
    )


class ProductionConfig(Config):
    DEBUG = False
    _db_url = os.environ.get("DATABASE_URL", "")
    # Railway/Render supply postgres:// — SQLAlchemy requires postgresql://
    SQLALCHEMY_DATABASE_URI = _db_url.replace("postgres://", "postgresql://", 1) if _db_url else None


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/servicesync_test",
    )
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
