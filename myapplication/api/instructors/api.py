from flask_restful import Resource
from flask import json, request, g
from datetime import datetime, timedelta
from myapplication.models import Users, Activities
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

        cmd = """SELECT u.id, u.first_name, u.last_name, u.email FROM fit.users u WHERE u.is_instructor=1 OFFSET %d LIMIT %d""" % (offset, limit)
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
            resp["instructors"].append({"id": instructor[0], "first_name": instructor[1], "last_name": instructor[2], "email": instructor[3]})

        return resp, 200

    def post(self):
        """Getting activities with facilities involved with particular instructor"""
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
                    "activities": [],
                    "instructor": {}}
            return err_resp, 204
        if email is None:
            err_resp = {
                "message": {"description": "Please provide json in body; optionally limit and offset, but email is a must!",
                            "name": "lack of instructors", "status": 400, "method": "GET", "timestamp": timestamp},
                "activities": [],
                "instructor": {}}
            return err_resp, 400

        if check_email(email) is False:
            err_resp = {
                "message": {"description": "Bad format of email!", "name": "lack of instructors",
                            "status": 400, "method": "GET", "timestamp": timestamp},
                "activities": [],
                "instructor": {}}
            return err_resp, 400

        cmd = """SELECT u.first_name, u.last_name, u.email, f.city, f.street, f.house_number, f.postcode, f.contact_number,
                    f.email, a.date, t.name_of_service
                    FROM fit.users u
                    INNER JOIN fit.activities a ON u.id=a.instructor_id
                    INNER JOIN fit.facilities f ON f.id=a.facility_id
                    INNER JOIN fit.types_of_activities t ON t.id=a.type_of_service_id
                    WHERE u.email=\'%s\' AND u.is_instructor=1
                    ORDER BY a.date DESC OFFSET %d LIMIT %d""" % (email, offset, limit)

        instructors_activities = db.session.execute(cmd).cursor.fetchall()

        if len(instructors_activities) == 0:
            resp = {"message": {"description": "There are no activities involved with this instructor!",
                                "name": "activities&facilities {}".format(email),
                                "status": 204, "method": "POST", "timestamp": timestamp},
                    "activities": [],
                    "instructor": {"email": email}}
            return resp, 204

        resp = {"message": {"description": "activities & facilities returned!", "name": "activities&facilities {}".format(email),
                            "status": 200, "method": "POST", "timestamp": timestamp},
                "activities": [],
                "instructor": {}}

        resp["instructor"]["first_name"] = instructors_activities[0][0]
        resp["instructor"]["last_name"] = instructors_activities[0][1]
        resp["instructor"]["email"] = instructors_activities[0][2]

        for instructor in instructors_activities:
            resp["activities"].append(
                {"city": instructor[3], "street": instructor[4], "house_number": instructor[5], "postcode": instructor[6],
                 "contact_number": instructor[7], "email_facility": instructor[8], "date": instructor[9],
                 "type_of_service": instructor[10]})

        return resp, 200

    @token_required
    def put(self):
        if g.user.is_instructor != 1:
            err_resp = {
                "message": {"description": "This user ain't instructor!", "name": "Forbidden method for this kind of users\
                                                                                  who are not instructors",
                            "status": 403, "method": "PUT", "timestamp": timestamp}}
            return err_resp, 403

        date = request.form.get('date')
        type_of_service_id = request.form.get('type_of_service_id')
        instructor_id = g.user.id
        facility_id = request.form.get('facility_id')
        price_id = request.form.get('price_id')

        cmd = """SELECT name_of_service, (SELECT email FROM fit.users WHERE %d=id), 
                (SELECT city FROM fit.facilities WHERE %d=id), (SELECT price FROM fit.price_list WHERE %d=id)
                FROM fit.types_of_services WHERE %d=id""" % (g.user.id, facility_id, price_id, type_of_service_id)
        res = db.session.execute(cmd).cursor.fetchone()

        if res[0] is None or res[2] is None or res[3] is None:
            err_resp = {
                "message": {"description": "Such price, facility, or/and type_of_service doesn't/don't exist!",
                            "name": "Trying to add new activity",
                            "status": 404, "method": "PUT", "timestamp": timestamp}}
            return err_resp, 404

        new_activity = Activities(date=date, type_of_service_id=type_of_service_id, instructor_id=g.user.id,
                                  facility_id=facility_id, price_id=price_id)

        db.session.add(new_activity)
        db.session.commit()


        resp = {"message": {"description": "New activity has been created!",
                            "name": "Activity added",
                            "status": 201, "method": "POST", "timestamp": timestamp},
                "activity": {"date": date, "name_of_service": res[0], "email_instructor": res[1], "city": res[2],
                             "price": res[3]}}
        return resp, 201







