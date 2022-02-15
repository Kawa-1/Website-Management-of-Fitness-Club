import jwt
from flask_restful import Resource
from flask import request, json, current_app
from datetime import datetime
from myapplication.api.activities.check import check_date_format, check_month_format, check_year_format
from myapplication.api.auth.auth import token_required
from myapplication import db
from myapplication.models import Participation

timestamp = str(datetime.utcnow())

# class involved with classes (classes ~ activity involved with fitness) table
class ActivityApi(Resource):
    #@token_required
    #current_user = None
    def get(self, date=None, limit=5):
        """Date parameter should be passed like: Year_Month_Day e.g. 2021_02_09 (YYYY_MM_DD) then we will receive all acitivites during this day
        if we are not passing any date parameter:
            then we will receive all activities from db
        if we are passing date like: 2020_12:
            then we will receive all activities from 2020's December
        if we are passing date like: 2020:
            then we will receive all activities from the year of 2020

        NOTE: Return is sorted; from the oldest to the newest
        """
        date: str

        limit_ = request.args.get("limit")

        if limit_ is not None:
            try:
                limit = int(limit_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Argument limit must be int",
                    "status": 400, "name": "invalid format of parameter limit", "method": "GET", "timestamp": timestamp}}
                return err_resp, 400

        if date is None:
            cmd = """SELECT c.date, c.type_of_classes, f.city, f.street, f.house_number, p.price, u.first_name, u.last_name, u.email 
                    FROM fit.classes c
                    INNER JOIN fit.facilities f ON c.facility_id=f.id
                    INNER JOIN fit.price_list p ON c.price_id=p.id
                    INNER JOIN fit.users u ON u.is_instructor=1 AND u.id=c.instructor_id
                    ORDER BY c.date DESC 
                    LIMIT %d""" % limit
            activity = db.session.execute(cmd).cursor.fetchall()
            if len(activity) == 0:
                resp = {"message": {
                    "description": "There are no activities at all",
                    "status": 204, "name": "lack of activities", "method": "GET", "timestamp": timestamp}}
                return resp, 204

            dictionary = {"activities": []}
            for obj in activity:
                dictionary['activities'].append(
                    {"date": obj[0], 'type_of_classes': obj[1], 'city': obj[2], 'street': obj[3],
                     'house_number': obj[4], 'price': obj[5], 'first_name': obj[6],
                     'last_name': obj[7], 'email': obj[8]})

            #dictionary['activities'] = sorted(dictionary['activities'], key=lambda i: i['date'], reverse=False)
            dictionary = json.dumps(dictionary, indent=4, sort_keys=True)
            return dictionary, 200

        err_resp = {"errors": [{"description": "Provided bad format of date",
                                "method": "GET", "name": "Failed obtaining classes", "status": 400, "timestamp": timestamp}]}
        err_resp = json.dumps(err_resp, indent=4, sort_keys=True)

        date = date.replace("_", "-")
        if not check_date_format(date) or not check_month_format(date) or not check_year_format(date):
            return err_resp, 400

        cmd = """SELECT c.date, c.type_of_classes, f.city, f.street, f.house_number, p.price, u.first_name, u.last_name, u.email
              FROM fit.classes c 
              INNER JOIN fit.facilities f ON c.facility_id=f.id
              INNER JOIN fit.price_list p ON c.price_id=p.id
              INNER JOIN fit.users u ON u.instructor.id=1 AND u.id=c.instructor_id
              WHERE c.date~*\'^%s.*\'
              ORDER BY c.date DESC
              LIMIT %d """  % date, limit
        activity = db.session.execute(cmd).cursor.fetchall()
        print(activity)
        print(len(activity))
        # It means there is no activities that day
        if len(activity) == 0:
            resp = {"message": {"description": "There are no activities", "status": 204, "method": "GET",
                                "timestamp": timestamp}}
            return resp, 204

        dictionary = {"message": {"description": "Activities returned", "name": "Activities returned",
                                  "method": "GET", "timestamp": timestamp}, "activities": []}
        for obj in activity:
            dictionary['activities'].append(
                {"date": obj[0], 'type_of_classes': obj[1], 'city': obj[2], 'street': obj[3],
                 'house_number': obj[4], 'price': obj[5], 'first_name': obj[6],
                 'last_name': obj[7], 'email': obj[8]})

        #dictionary['activities'] = sorted(dictionary['activities'], key = lambda i: i['date'], reverse=False)
        #dictionary = json.dumps(dictionary, indent=4, sort_keys=True)
        return dictionary, 200


class UserActivityApi(Resource):
    @token_required
    def get(self, current_user=None):
        user_id = current_user.id
        # TODO: Get every classes in which particular user took part; DESC - 1st row will be the newest
        cmd =  """SELECT c.type_of_classes, c.date, u.first_name, u.last_name, u.email, f.city, f.street, f.house_number, 
        (SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.class_id=c.id GROUP BY c.id), c.id, pr.price, pr.service 
                    FROM fit.classes c 
                    INNER JOIN fit.users u ON c.instructor_id=u.id AND u.instructor_id=1 
                    INNER JOIN fit.facilities f ON c.facility_id=f.id 
                    INNER JOIN fit.participation p ON p.class_id=c.id
                    INNER JOIN fit.price_list pr ON pr.id=c.price_id
                    WHERE %d IN (SELECT p1.user_id FROM fit.participation p1 WHERE p1.class_id=c.id)
                    GROUP BY c.id 
                    ORDER BY c.date DESC;""" % user_id

        classes_user_took = db.session.execute(cmd).cursor.fetchall()
        dictionary = {"message": {"description": "Activities returned", "name": "Activities returned",
                                  "method": "GET", "timestamp": timestamp}, "activities": []}

        for activity in classes_user_took:
            dictionary['activities'].append({"type_of_classes": classes_user_took[0], "date": classes_user_took[1],
                                             "instructor_name": classes_user_took[2], "instructor_surname": classes_user_took[3],
                                             "instructor_email": classes_user_took[4], "fitness_city": classes_user_took[4],
                                             "fitness_street": classes_user_took[5], "fitness_house_number": classes_user_took[6],
                                             "number_users_enrolled_total": classes_user_took[7], "id": classes_user_took[8],
                                             "price": classes_user_took[9], "service": classes_user_took[10]})

        return dictionary, 200

    @token_required
    def post(self, current_user=None):
        """Signing up for classes. ID indicates id of activity
            DESIRED BODY: e.g. {"id": 1}
        """
        body = request.get_json(silent=True)
        class_id = body.get('id')

        if not body or class_id is None:
            err_resp = {"message": {"description": "lack of information to which activity user want to be signed",
                                    "status": 400, "name": "lack of body; json", "method": "POST", "timestamp":
                                    timestamp}}
            return err_resp, 400

        cmd = "SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.class_id=%d" % class_id
        number_of_users = db.session.execute(cmd).cursor.fetchone()

        if number_of_users is None:
            err_resp = {"message": {
                "description": "Such activity doesn't exist",
                "status": 400, "name": "cannot sign up", "method": "POST", "timestamp": timestamp}}
            return err_resp, 400

        number_of_users = number_of_users[0]
        if number_of_users >= 15:
            err_resp = {"message": {"description": "User is not allowed to join this activity bcs number of users is max, it means 15",
                                    "status": 400, "name": "cannot sign up", "method": "POST", "timestamp": timestamp}}
            return err_resp, 400

        cmd = "SELECT user_id FROM fit.participation WHERE user_id=%d AND class_id=%d" %  (current_user.id, class_id)
        res = db.session.execute(cmd).cursor.fetchone()
        if res is not None:
            err_resp = {"message": {
                "description": "User is already signed for this activity",
                "status": 400, "name": "Already signed up", "method": "POST", "timestamp": timestamp}}
            return err_resp, 400


        db.session.add(Participation(user_id=current_user.id, class_id=class_id))
        db.session.commit()

        resp = {"message": {"description": "User properly signed up for activity with email: {} and class_id: {}".format(current_user.email, class_id),
                                    "status": 201, "name": "signed up for activity", "method": "POST", "timestamp": timestamp}}
        return resp, 201

    @token_required
    def delete(self, current_user=None, class_id=None):
        cmd = "SELECT id FROM fit.classes WHERE id=%d" % class_id
        res = db.session.execute(cmd).cursor.fetchone()

        if class_id is None or res is None:
            err_resp = {"message": {
                "description": "Such activity doesn't exist, cannot be deleted",
                "status": 400, "name": "cannot delete", "method": "DELETE", "timestamp": timestamp}}
            return err_resp, 400

        cmd = "DELETE FROM fit.participation WHERE user_id=%d AND class_id=%d" % (current_user.id, class_id)
        db.session.execute(cmd)
        db.session.commit()

        resp = {"message": {
            "description": "User properly signed off the activity user's email: {} and class_id: {}".format(current_user.email, class_id),
            "status": 202, "name": "User deleted from activity", "method": "DELETE", "timestamp": timestamp}}
        return resp, 202

















