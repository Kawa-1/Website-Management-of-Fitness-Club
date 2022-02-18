import jwt
from flask_restful import Resource
from flask import request, json, current_app, g
from datetime import datetime
from myapplication.api.activities.check import check_date_format, check_month_format, check_year_format
from myapplication.api.auth.auth import token_required
from myapplication import db
from myapplication.models import Participation
from myapplication.logger import get_logger
from myapplication.global_helpers import limit_offset

timestamp = str(datetime.utcnow())
log = get_logger(__name__)

# class involved with activities (classes ~ activity involved with fitness) table
class ActivityApi(Resource):
    #@token_required
    #g.user = None
    @limit_offset
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
            cmd = """SELECT a.date, t.name_of_service, f.city, f.street, f.house_number, p.price, u.first_name, u.last_name, u.email, 
                    (SELECT COUNT(p.id) FROM fit.participation p WHERE p.activity_id=a.id), a.id
                    FROM fit.activities a
                    INNER JOIN fit.facilities f ON a.facility_id=f.id
                    INNER JOIN fit.price_list p ON a.price_id=p.id
                    INNER JOIN fit.users u ON u.is_instructor=1 AND u.id=a.instructor_id
                    INNER JOIN fit.types_of_services t ON t.id=a.type_of_service_id AND t.is_subscription=0
                    ORDER BY a.date DESC 
                    LIMIT %d""" % g.limit
            activity = db.session.execute(cmd).cursor.fetchall()
            if len(activity) == 0:
                resp = {"message": {
                    "description": "There are no activities at all",
                    "status": 200, "name": "lack of activities", "method": "GET", "timestamp": timestamp}}
                # 204 should be
                return resp, 200

            dictionary = {"message": {"description": "Activities returned", "name": "Activities returned", "status": 200,
                                      "method": "GET", "timestamp": timestamp}, "activities": []}
            for obj in activity:
                dictionary['activities'].append(
                    {"date": obj[0], 'type_of_service': obj[1], 'city': obj[2], 'street': obj[3],
                     'house_number': obj[4], 'price': obj[5], 'first_name': obj[6],
                     'last_name': obj[7], 'email': obj[8], "total_number_of_users": obj[9], "id": obj[10]})

            #dictionary['activities'] = sorted(dictionary['activities'], key=lambda i: i['date'], reverse=False)
            #dictionary = json.dumps(dictionary, indent=4, sort_keys=True)
            return dictionary, 200

        err_resp = {"errors": [{"description": "Provided bad format of date",
                                "method": "GET", "name": "Failed obtaining activities", "status": 422, "timestamp": timestamp}]}

        date = date.replace("_", "-")
        if not check_date_format(date) or not check_month_format(date) or not check_year_format(date):
            return err_resp, 422

        cmd = """SELECT a.date, t.name_of_service, f.city, f.street, f.house_number, p.price, u.first_name, u.last_name, u.email,
              (SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.activity_id=a.id GROUP BY p.activity_id), a.id
              FROM fit.activities a 
              INNER JOIN fit.facilities f ON a.facility_id=f.id
              INNER JOIN fit.price_list p ON a.price_id=p.id
              INNER JOIN fit.users u ON u.instructor.id=1 AND u.id=a.instructor_id
              INNER JOIN fit.types_of_services t ON t.id=a.type_of_service_id AND t.is_subscription=0
              WHERE a.date~*\'^%s.*\'
              ORDER BY a.date DESC
              LIMIT %d """  % (date, g.limit)
        activity = db.session.execute(cmd).cursor.fetchall()
        print(activity)
        print(len(activity))
        # It means there is no activities that day
        if len(activity) == 0:
            resp = {"message": {"description": "There are no activities", "status": 200, "method": "GET",
                                "timestamp": timestamp}}
            # 204 should be
            return resp, 200

        dictionary = {"message": {"description": "Activities returned", "name": "Activities returned", "status": 200,
                                  "method": "GET", "timestamp": timestamp}, "activities": []}
        for obj in activity:
            dictionary['activities'].append(
                {"date": obj[0], 'type_of_service': obj[1], 'city': obj[2], 'street': obj[3],
                 'house_number': obj[4], 'price': obj[5], 'first_name': obj[6],
                 'last_name': obj[7], 'email': obj[8], "total_number_of_users": obj[9], "id": obj[10]})

        #dictionary['activities'] = sorted(dictionary['activities'], key = lambda i: i['date'], reverse=False)
        #dictionary = json.dumps(dictionary, indent=4, sort_keys=True)
        return dictionary, 200