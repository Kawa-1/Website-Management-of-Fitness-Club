from flask import g
from flask_restful import Resource
from datetime import datetime
from myapplication import db
from myapplication.logger import get_logger

timestamp = str(datetime.utcnow())
log = get_logger(__name__)

class PriceOnService(Resource):
    def get(self, service_id=None):
        if service_id is None:
            cmd = """
                      SELECT p.id, p.price, p.service_id, t.name_of_service, t.is_subscription 
                      FROM fit.types_of_services t 
                      INNER JOIN fit.price_list p ON p.service_id=t.id
                  """

            price_on_service = db.session.execute(cmd).cursor.fetchall()
            resp = {"message": {
                "description": "Price with services returned",
                "status": 200, "name": "Price based on service", "method": "GET",
                "timestamp": timestamp},
                    "price_service": []}

            for obj in price_on_service:
                resp["price_service"].append({"price_id": obj[0], "price": obj[1], "service_id": obj[2], "service_name": obj[3],
                                              "is_subscription": obj[4]})

            return resp, 200

        if not isinstance(service_id, int):
            try:
                service_id = int(service_id)
            except Exception as e:
                err_resp = {"message": {
                    "description": "service_id bad type",
                    "status": 422, "name": "cannot process this request", "method": "GET", "timestamp": timestamp}}
                return err_resp, 422

        cmd = """
                    SELECT p.id, p.price, p.service_id, t.name_of_service, t.is_subscription 
                    FROM fit.types_of_services t 
                    INNER JOIN fit.price_list p ON p.service_id=t.id
					WHERE p.service_id=%d
              """ % service_id

        price_on_service = db.session.execute(cmd).cursor.fetchall()
        resp = {"message": {
            "description": "Price based on service returned",
            "status": 200, "name": "Price based on service", "method": "GET",
            "timestamp": timestamp},
            "price_service": []}

        for obj in price_on_service:
            resp["price_service"].append(
                {"price_id": obj[0], "price": obj[1], "service_id": obj[2], "service_name": obj[3],
                 "is_subscription": obj[4]})

        return resp, 200

