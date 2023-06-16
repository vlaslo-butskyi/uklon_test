import time

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from src.logger import service_logger
from src.prometheus_metrics import REGISTRY, table_records_counter
from src.settings import config

logger = service_logger()

db = SQLAlchemy(session_options={"autoflush": False})
migrate = Migrate(compare_type=True)
temp_buffer = []
try_connect_db = False

from src.models import *


def create_app():
    app = Flask(__name__)
    app.config.update(config)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.get("DB_URL")
    init_metrics(app)

    db.init_app(app)
    db.app = app
    migrate.init_app(app, db)

    from src.api.restx import api

    api.init_app(app)

    return app


def init_metrics(app):
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app(REGISTRY)})


def check_db_connection():
    try:
        db.session.query(text("1")).from_statement(text("SELECT 1")).all()
        return True
    except Exception:
        return False


def connect_to_db():
    try_connect_db = True
    while try_connect_db:
        if check_db_connection():
            for data in temp_buffer:
                save_data_to_db(data)
            temp_buffer.clear()
            try_connect_db = False
        else:
            time.sleep(5)


def save_data_to_db(data):
    db.session.add(data)
    db.session.commit()
    table_records_counter.inc()


def main():
    logger.info(msg=f"Initializing {config.get('SERVICE_NAME')} ...", extra={"event_name": "initializing_server"})
    app = create_app()

    logger.info(
        msg=f">>> Starting development server at http://{config.get('SERVER_HOST')}:{config.get('SERVER_PORT')}/ <<<",
    )

    app.run(
        debug=config.get("FLASK_DEBUG"),
        port=config.get("SERVER_PORT"),
        host=config.get("SERVER_HOST"),
        use_reloader=True,
    )


if __name__ == "__main__":
    main()
