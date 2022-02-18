from bleach import clean
from flask_restful import Resource
from flask import json, request, g
from datetime import datetime, timedelta
from myapplication.models import Users, Activities
from myapplication import db
from myapplication.api.auth.auth import check_email, token_required
from myapplication.api.instructors.helpers import check_int, check_date_activities
from myapplication.global_helpers import limit_offset, valid_date_H_M
from myapplication.logger import get_logger

timestamp = str(datetime.utcnow())
log = get_logger(__name__)

class InstructorsApi(Resource):
    @limit_offset
    def get(self):
        cmd = """SELECT u.id, u.first_name, u.last_name, u.email FROM fit.users u WHERE u.is_instructor=1 OFFSET %d LIMIT %d""" % (g.offset, g.limit)
        instructors = db.session.execute(cmd).fetchall()

        if len(instructors) == 0:
            resp = {"message": {"description": "There is not even single instructor!", "name": "lack of instructors",
                                "status": 200, "method": "GET", "timestamp": timestamp},
                    "instructors": []}
            # 204 should be
            return resp, 200

        resp = {"message": {"description": "Instructors returned!", "name": "instructors",
                            "status": 200, "method": "GET", "timestamp": timestamp},
                "instructors": []}

        for instructor in instructors:
            resp["instructors"].append({"id": instructor[0], "first_name": instructor[1], "last_name": instructor[2], "email": instructor[3]})

        return resp, 200

    @limit_offset
    def post(self):
        """Getting activities with facilities involved with particular instructor"""
        post_data = request.get_json()
        email = post_data.get("email")

        email = clean(email)

        user = Users.query.filter_by(email=email).first()

        if user is None:
            err_resp = {"message": {"description": "There is not even single instructor!", "name": "lack of instructors",
                                "status": 200, "method": "GET", "timestamp": timestamp},
                    "activities": [],
                    "instructor": {}}
            # 204 should be
            return err_resp, 200
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
                            "status": 422, "method": "GET", "timestamp": timestamp},
                "activities": [],
                "instructor": {}}
            return err_resp, 422

        cmd = """SELECT u.first_name, u.last_name, u.email, f.city, f.street, f.house_number, f.postcode, f.contact_number,
                    f.email, a.date, t.name_of_service
                    FROM fit.users u
                    INNER JOIN fit.activities a ON u.id=a.instructor_id
                    INNER JOIN fit.facilities f ON f.id=a.facility_id
                    INNER JOIN fit.types_of_activities t ON t.id=a.type_of_service_id
                    WHERE u.email=\'%s\' AND u.is_instructor=1
                    ORDER BY a.date DESC OFFSET %d LIMIT %d""" % (email, g.offset, g.limit)

        instructors_activities = db.session.execute(cmd).cursor.fetchall()

        if len(instructors_activities) == 0:
            resp = {"message": {"description": "There are no activities involved with this instructor!",
                                "name": "activities&facilities {}".format(email),
                                "status": 200, "method": "POST", "timestamp": timestamp},
                    "activities": [],
                    "instructor": {"email": email}}
            # 204 should be
            return resp, 200

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
        #price_id = request.form.get('price_id')

        date = clean(date)

        if not valid_date_H_M(date):
            err_resp = {
                "message": {"description": "Bad format of date", "name": "Format of date is improper",
                            "status": 422, "method": "PUT", "timestamp": timestamp}}
            return err_resp, 422

        check = check_int(type_of_service_id=type_of_service_id, facility_id=facility_id)

        if check[0] is False:
            try:
                type_of_service_id = int(type_of_service_id)
                facility_id = int(facility_id)
            except Exception as e:
                err_resp = {
                    "message": {"description": "One of the fields couldn't be conversed "
                                               "to int {}, {}".format(type_of_service_id, facility_id),
                                "name": "Impossible conversion",
                                "status": 422, "method": "PUT", "timestamp": timestamp}}
                return err_resp, 422

        cmd = """SELECT t.name_of_service, (SELECT email FROM fit.users WHERE %d=id), 
                (SELECT city FROM fit.facilities WHERE %d=id), pr.price, pr.id
                FROM fit.types_of_services t 
                INNER JOIN fit.price_list pr ON pr.service_id=%d 
                WHERE %d=t.id""" % (g.user.id, facility_id, type_of_service_id, type_of_service_id)
        res = db.session.execute(cmd).cursor.fetchone()

        print(res)
        if res[0] is None or res[2] is None or res[3] is None:
            err_resp = {
                "message": {"description": "Such price, facility, or/and type_of_service doesn't/don't exist!",
                            "name": "Trying to add new activity",
                            "status": 404, "method": "PUT", "timestamp": timestamp}}
            return err_resp, 404

        print("CHECK HERE: ", date)
        new_activity = Activities(date=date, type_of_service_id=type_of_service_id, instructor_id=g.user.id,
                                  facility_id=facility_id, price_id=res[4])

        db.session.add(new_activity)
        db.session.commit()


        resp = {"message": {"description": "New activity has been created!",
                            "name": "Activity added",
                            "status": 201, "method": "POST", "timestamp": timestamp},
                "activity": {"date": date, "name_of_service": res[0], "email_instructor": res[1], "city": res[2],
                             "price": res[3], "id": res[4]}}
        return resp, 201







