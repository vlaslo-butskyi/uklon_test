import traceback

from flask_restx import Api

from src import settings
from src.logger import service_logger

from .driver_geo import ns as driver_geo_ns
from .health import ns as health_ns


logger = service_logger()

api = Api(version="1.0", title=f"{settings.config.get('SERVICE_NAME')} REST API")

api.add_namespace(health_ns, path="/health")
api.add_namespace(driver_geo_ns, path="/api/v1/driver-geo")


@api.errorhandler
def default_error_handler(e):
    message = "An unhandled exception occurred. Check logs for more details."
    logger.critical(
        msg=f"An unhandled exception occurred: {e}.",
        extra={"event_name": "restplus_exception", "traceback": traceback.format_exc()},
    )

    return {"message": message}, 500
