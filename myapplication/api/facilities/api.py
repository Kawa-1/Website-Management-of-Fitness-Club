from flask import g
from flask_restful import Resource
from datetime import datetime
from myapplication.global_helpers import limit_offset
from myapplication import db

timestamp = str(datetime.utcnow())

class FacilitiesApi(Resource):
    @limit_offset
    def get(self):
        cmd = """SELECT id, city, street, house_number, postcode, contact_number, email FROM fit.facilities LIMIT %d OFFSET %d""" % (g.limit, g.offset)
        facilities_all = db.session.execute(cmd).cursor.fetchall()

        resp = {"message": {"description": "Facilities returned!", "name": "facilities api", "method": "GET", "status": 200,
                            "timestamp": timestamp},
                "facilities": []}

        for facility in facilities_all:
            resp["facilities"].append({"id": facility[0], "city": facility[1], "street": facility[2], "house_number": facility[3],
                                       "postcode": facility[4], "contact_number": facility[5], "email": facility[6]})

        return resp, 200

