from flask_restful import Resource
from flask import json, request
from datetime import datetime, timedelta
from myapplication.models import Users
from myapplication import db
from myapplication.api.auth.auth import check_email, token_required

timestamp = str(datetime.utcnow())

class InstructorsApi(Resource):
    def get(self, limit=5, offset=0):
        limit_ = request.args.get("limit")
        offset_ = request.args.get("offset")

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

        cmd = """SELECT u.first_name, u.last_name, u.email, FROM fit.users u\
                            WHERE u.is_instructor=1 OFFSET %d LIMIT %d""" % (offset, limit)
        instructors = db.session.execute(cmd).fetchall()

        if len(instructors) == 0:
            resp = {"message": {"description": "There is not even single instructor!", "name": "lack of instructors",
                                "status": 204, "method": "GET", "timestamp": timestamp},
                    "instructors": []}
            return resp, 204

        resp = {"message": {"description": "Instructors returned!", "name": "instructors",
                            "status": 200, "method": "GET", "timestamp": timestamp},
                "instructors": []}

        for instructor in instructors:
            resp["instructors"].append({"first_name": instructor[0], "last_name": instructor[1], "email": instructor[2]})

        return resp, 200

    def post(self):
        """Getting classes with facilities involved with particular instructor"""
        post_data = request.get_json()
        email = post_data.get("email")
        limit = post_data.get("limit")
        offset = post_data.get("offset")

        user = Users.query.filter_by(email=email).first()

        if limit is None:
            limit = 10
        if offset is None:
            offset = 0
        if user is None:
            err_resp = {"message": {"description": "There is not even single instructor!", "name": "lack of instructors",
                                "status": 204, "method": "GET", "timestamp": timestamp},
                    "classes": [],
                    "instructor": {}}
            return err_resp, 204
        if email is None:
            err_resp = {
                "message": {"description": "Please provide json in body; optionally limit and offset, but email is a must!",
                            "name": "lack of instructors", "status": 400, "method": "GET", "timestamp": timestamp},
                "classes": [],
                "instructor": {}}
            return err_resp, 400

        if check_email(email) is False:
            err_resp = {
                "message": {"description": "Bad format of email!", "name": "lack of instructors",
                            "status": 400, "method": "GET", "timestamp": timestamp},
                "classes": [],
                "instructor": {}}
            return err_resp, 400

        cmd = """SELECT u.first_name, u.last_name, u.email, f.city, f.street, f.house_number, f.postcode, f.contact_number,
                    f.email, c.date, c.type_of_classes 
                    FROM fit.users u
                    INNER JOIN fit.classes c ON u.id=c.instructor_id
                    INNER JOIN fit.facilities f ON f.id=c.facility_id
                    WHERE u.email=\'%s\' AND u.is_instructor=1
                    ORDER BY c.date DESC OFFSET %d LIMIT %d""" % (email, offset, limit)

        instructors_activities = db.session.execute(cmd).cursor.fetchall()

        if len(instructors_activities) == 0:
            resp = {"message": {"description": "There are no activities involved with this instructor!",
                                "name": "classes&facilities {}".format(email),
                                "status": 204, "method": "POST", "timestamp": timestamp},
                    "classes": [],
                    "instructor": {"email": email}}
            return resp, 204

        resp = {"message": {"description": "classes & facilities returned!", "name": "classes&facilities {}".format(email),
                            "status": 200, "method": "POST", "timestamp": timestamp},
                "classes": [],
                "instructor": {}}

        resp["instructor"]["first_name"] = instructors_activities[0][0]
        resp["instructor"]["last_name"] = instructors_activities[0][1]
        resp["instructor"]["email"] = instructors_activities[0][2]

        for instructor in instructors_activities:
            resp["classes"].append(
                {"city": instructor[3], "street": instructor[4], "house_number": instructor[5], "postcode": instructor[6],
                 "contact_number": instructor[7], "email_facility": instructor[8], "date": instructor[9],
                 "type_of_classes": instructor[10]})

        return resp, 200

    @token_required
    def put(self, current_user=None):
        if current_user.is_instructor != 1:
            err_resp = {
                "message": {"description": "This user ain't instructor!", "name": "Forbidden method for this kind of users\
                                                                                  who are not instructors",
                            "status": 403, "method": "PUT", "timestamp": timestamp}}
            return err_resp, 403
        # TODO: continue creating activities
        pass






