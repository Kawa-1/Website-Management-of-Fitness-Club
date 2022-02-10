import jwt
from flask_restful import Resource
from flask import request, json, current_app
from datetime import datetime
from myapplication.api.activities.check import check_date_format, check_month_format, check_year_format
from myapplication.api.auth.auth import token_required
from myapplication import db

# class involved with classes (classes ~ activity involved with fitness) table
class ActivityApi(Resource):
    @token_required
    def get(self, date=None):
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

        if date is None:
            cmd = "SELECT * FROM fit.classes"
            activity = db.session.execute(cmd).cursor.fetchall()
            if len(activity) == 0:
                return ("", 204)

            dictionary = {"activities": []}
            for obj in activity:
                cmd = "SELECT f.city, f.street, f.house_number, (SELECT p.price FROM fit.price_list p WHERE p.id='%s') \
                                FROM fit.facilities f WHERE f.id='%s'" % (obj[5], obj[4])
                foreign = db.session.execute(cmd).cursor.fetchone()
                dictionary['activities'].append(
                    {"id": obj[0], 'date': obj[1], 'type_of_classes': obj[2], 'instructor_id': obj[3],
                     'facility_id': obj[4], 'city': foreign[0], 'street': foreign[1],
                     'house_number': foreign[2], 'price': foreign[3]})

            dictionary['activities'] = sorted(dictionary['activities'], key=lambda i: i['date'], reverse=False)
            dictionary = json.dumps(dictionary, indent=4, sort_keys=True)
            return dictionary, 200


        err_resp = {"errors": [{"description": "Provided bad format of date",
                                "method": "GET", "name": "Failed obtaining classes", "status": 400, "timestamp": datetime.now()}]}
        err_resp = json.dumps(err_resp, indent=4, sort_keys=True)

        date = date.replace("_", "-")
        if not check_date_format(date) or not check_month_format(date) or not check_year_format(date):
            return err_resp, 400

        cmd = "SELECT * FROM fit.classes WHERE classes.date~*'^%s.*'" % date
        activity = db.session.execute(cmd).cursor.fetchall()
        print(activity)
        print(len(activity))
        # It means there is no activities that day
        if len(activity) == 0:
            # resp = {"message": "There are no activities on this day", "status": 204, "method": "GET"}
            # resp = json.dumps(resp, indent=4, sort_keys=True)
            # print(resp)
            return ("", 204)

        dictionary = {"activities": []}

        for obj in activity:
            cmd = "SELECT f.city, f.street, f.house_number, (SELECT p.price FROM fit.price_list p WHERE p.id='%s') \
                            FROM fit.facilities f WHERE f.id='%s'" % (obj[5], obj[4])
            foreign = db.session.execute(cmd).cursor.fetchone()
            dictionary['activities'].append({"id": obj[0], 'date': obj[1], 'type_of_classes': obj[2], 'instructor_id': obj[3],
                                             'facility_id': obj[4], 'city': foreign[0], 'street': foreign[1],
                                             'house_number': foreign[2], 'price': foreign[3]})

        dictionary['activities'] = sorted(dictionary['activities'], key = lambda i: i['date'], reverse=False)
        dictionary = json.dumps(dictionary, indent=4, sort_keys=True)
        return dictionary, 200


class UserActivityApi(Resource):
    @token_required
    def get(self):
        try:
            token = request.headers.get('x-access-tokens')
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except Exception as e:
            err_resp = {"message": {"description": "token is invalid", "status": 401, "name": e,
                                    "method": "PUT", "timestamp": datetime.utcnow()}}
            err_resp = json.dumps(err_resp, indent=4, sort_keys=True)
            return err_resp, 401

        email = data['email']
        # TODO: Get every classes in which particular user took part
        pass







