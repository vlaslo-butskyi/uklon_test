from datetime import datetime

from flask import request
from flask_restx import fields, Namespace, Resource
from geopy.distance import geodesic

from src import check_db_connection, connect_to_db, db, temp_buffer, try_connect_db
from src.logger import service_logger
from src.models import GeoRecords
from src.prometheus_metrics import (
    abnormal_altitude_counter,
    coordinates_counter,
    request_counter,
    speeding_coordinates_counter,
    table_records_counter,
    unique_drivers_counter,
)
from src.settings import config


logger = service_logger()
ns = Namespace("driver_geo", description="Driver Geo.")


@ns.route("/")
class DriverGeo(Resource):
    @staticmethod
    @ns.expect(
        ns.model(
            "POST driver data",
            dict(
                driver_id=fields.Integer(required=True),
                latitude=fields.Float(required=True),
                longitude=fields.Float(required=True),
                speed=fields.Float(required=True),
                altitude=fields.Float(required=True),
            ),
        ),
        validate=True,
    )
    def post():
        body = request.json
        driver_id = body.get("driver_id")
        latitude = body.get("latitude")
        longitude = body.get("longitude")
        speed = body.get("speed")
        altitude = body.get("altitude")

        coordinates_counter.inc()
        if not GeoRecords.query.filter_by(driver_id=driver_id).first():
            unique_drivers_counter.inc()

        correct_behavior = DriverGeo.is_correct(driver_id, speed, altitude, latitude, longitude)

        new_record = GeoRecords(
            driver_id=driver_id,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            altitude=altitude,
            is_correct=correct_behavior,
        )
        if try_connect_db:
            temp_buffer.append(new_record)
        else:
            try:
                db.session.add(new_record)
                db.session.commit()
            except Exception:
                if not check_db_connection():
                    connect_to_db()
            else:
                table_records_counter.inc()
        request_counter.inc()
        return {}, 200

    @staticmethod
    def is_correct(driver_id, speed, altitude, latitude, longitude):
        result = True
        SPEED_LIMIT = config.get("SPEED_LIMIT")
        ALTITUDE_LIMIT = config.get("ALTITUDE_LIMIT")
        last_record = (
            GeoRecords.query.filter_by(driver_id=driver_id)
            .order_by(GeoRecords.datetime.desc(), GeoRecords.id.desc())
            .first()
        )
        if last_record:
            coordinates_delta_in_km = geodesic(
                (last_record.latitude, last_record.longitude), (latitude, longitude)
            ).kilometers
            time_delta = datetime.utcnow() - last_record.datetime
            if time_delta.seconds < 60 * 60:
                last_speed = coordinates_delta_in_km * 60 * 60 / time_delta.seconds
            else:
                last_speed = coordinates_delta_in_km / time_delta.seconds / 60 * 60

            if last_speed > SPEED_LIMIT:
                logger.warn(
                    msg=f"|||ANOMALY DATA||| - {driver_id = } drove "
                    f"{coordinates_delta_in_km} kilometer(s) in {time_delta} hour(s) "
                    f"at a speed of {last_speed} kmph",
                    extra={
                        "driver_id": driver_id,
                        "coordinates_delta_in_km": coordinates_delta_in_km,
                        "time_delta": time_delta,
                        "last_speed": last_speed,
                    },
                )
                result = False

        if speed > SPEED_LIMIT:
            logger.warn(
                msg=f"|||ANOMALY DATA||| - {driver_id = } drove at a speed of {speed} kmph",
                extra={
                    "driver_id": driver_id,
                    "speed": speed,
                },
            )
            speeding_coordinates_counter.inc()
            result = False
        elif altitude < 0 or altitude > ALTITUDE_LIMIT:
            logger.warn(
                msg=f"|||ANOMALY DATA||| - {driver_id = } drove at an altitude of {altitude} meter(s)",
                extra={
                    "driver_id": driver_id,
                    "altitude": altitude,
                },
            )
            abnormal_altitude_counter.inc()
            result = False

        return result
