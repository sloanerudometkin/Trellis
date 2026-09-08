import os

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config.application import DevelopmentConfig, ProductionConfig
from trellis.errors import register_error_handlers
from trellis.extensions import db, limiter


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_object=None) -> Flask:
    app = Flask(__name__)
    default_config = ProductionConfig if os.getenv("FLASK_ENV") == "production" else DevelopmentConfig
    app.config.from_object(config_object or default_config)

    db.init_app(app)
    limiter.init_app(app)

    from trellis import models  # noqa: F401

    from trellis.routes import api

    app.register_blueprint(api, url_prefix="/api/v1")
    register_error_handlers(app)
    return app
