from flask_restx import Namespace, Resource

from src import check_db_connection


ns = Namespace("health", description="Health of service.")


@ns.route("/")
class Health(Resource):
    @staticmethod
    def get():
        return "OK", 200


@ns.route("/db-health")
class DatabaseHealth(Resource):
    @staticmethod
    def get():
        if check_db_connection():
            return "OK", 200
        else:
            return "Database connection error", 500
