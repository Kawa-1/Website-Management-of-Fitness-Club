from flask import request
from flask_restful import Resource
from datetime import datetime
from myapplication import db

timestamp = str(datetime.utcnow())

class FacilitiesApi(Resource):
    def get(self, limit=5, offset=0, *args, **kwargs):
        limit_ = request.args.get("limit")
        offset_ = request.args.get("offset")

        #TODO: Decorator instead of copy paste...

        if limit_ is not None:
            try:
                limit = int(limit_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Argument limit must be int",
                    "status": 400, "name": "invalid format of parameter limit", "method": "GET",
                    "timestamp": timestamp}}
                return err_resp, 400

        if offset_ is not None:
            try:
                offset = int(offset_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Argument offset must be int",
                    "status": 400, "name": "invalid format of parameter offset", "method": "GET",
                    "timestamp": timestamp}}
                return err_resp, 400

        cmd = """SELECT id, city, street, house_number, postcode, contact_number, email FROM fit.facilities LIMIT %d OFFSET %d""" % (limit, offset)
        facilities_all = db.session.execute(cmd).cursor.fetchall()

        resp = {"message": {"description": "Facilities returned!", "name": "facilities api", "method": "GET", "status": 200,
                            "timestamp": timestamp},
                "facilities": []}

        for facility in facilities_all:
            resp["facilities"].append({"id": facility[0], "city": facility[1], "street": facility[2], "house_number": facility[3],
                                       "postcode": facility[4], "contact_number": facility[5], "email": facility[6]})

        return resp, 200

