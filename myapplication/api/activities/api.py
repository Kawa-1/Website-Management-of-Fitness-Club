import jwt
from flask_restful import Resource
from flask import request, json, current_app, g
from datetime import datetime
from myapplication.api.activities.check import check_month_format, check_year_format
from myapplication.api.auth.auth import token_required
from myapplication import db
from myapplication.models import Participation
from myapplication.logger import get_logger
from myapplication.global_helpers import limit_offset, valid_date_day, valid_date_Y, valid_date_Y_m

timestamp = str(datetime.utcnow())
log = get_logger(__name__)

# class involved with activities (classes ~ activity involved with fitness) table
class ActivityApi(Resource):
    #@token_required

    @limit_offset
    def get(self, date=None):
        """
        Date parameter should be passed like: Year-Month-Day e.g. 2021-02-09 (YYYY-MM-DD) then we will receive all acitivites during this day
        OR
        We are able to pass arg url parameter 'since_today' with value 1 (only 1 is processable) then we will get all activities since today
        Both parameters will result in bad request...
        if we are not passing any date parameter:
            then we will receive all activities from db
        if we are passing date like: 2020-12:
            then we will receive all activities from 2020's December
        if we are passing date like: 2020:
            then we will receive all activities from the year of 2020

        NOTE: Return is sorted; from the oldest to the newest in case of date parameter,
                                from the newest to the oldest in case of since_today arg url parameter
        """
        date: str
        since_today: int

        # arg is passed as a string from angular
        since_today = request.args.get('since_today')

        if since_today is not None:
            try:
                since_today = int(since_today)
            except Exception:
                err_resp = {"message": {
                    "description": "since_today was passed in improper format",
                    "method": "GET", "name": "Failed obtaining activities",
                    "status": 422, "timestamp": timestamp}}
                return err_resp, 422

            if date is not None:
                err_resp = {"message": {
                    "description": "It is not allowed to pass simultaneously parameter date and since_today",
                    "method": "GET", "name": "Failed obtaining activities",
                    "status": 400, "timestamp": timestamp}}
                return err_resp, 400

            if since_today == 1:
                today = "{} {}".format(datetime.utcnow().strftime("%Y-%m-%d"), "00-00")
                cmd = """SELECT a.date, t.name_of_service, f.city, f.street, f.house_number, p.price, u.first_name, u.last_name, u.email, 
                                    (SELECT COUNT(p.id) FROM fit.participation p WHERE p.activity_id=a.id), a.id
                                    FROM fit.activities a
                                    INNER JOIN fit.facilities f ON a.facility_id=f.id
                                    INNER JOIN fit.price_list p ON a.price_id=p.id
                                    INNER JOIN fit.users u ON u.is_instructor=1 AND u.id=a.instructor_id
                                    INNER JOIN fit.types_of_services t ON t.id=a.type_of_service_id AND t.is_subscription=0
                                    WHERE \'%s\'<=a.date
                                    ORDER BY a.date 
                                    LIMIT %d""" % (today ,g.limit)

                activity = db.session.execute(cmd).cursor.fetchall()
                if len(activity) == 0:
                    resp = {"message": {
                        "description": "There are no activities at all",
                        "status": 200, "name": "lack of activities", "method": "GET", "timestamp": timestamp}}
                    # 204 should be
                    return resp, 200

                dictionary = {
                    "message": {"description": "Activities returned", "name": "Activities returned", "status": 200,
                                "method": "GET", "timestamp": timestamp}, "activities": []}
                for obj in activity:
                    dictionary['activities'].append(
                        {"date": obj[0], 'type_of_service': obj[1], 'city': obj[2], 'street': obj[3],
                         'house_number': obj[4], 'price': obj[5], 'first_name': obj[6],
                         'last_name': obj[7], 'email': obj[8], "total_number_of_users": obj[9], "id": obj[10]})

                return dictionary, 200

            else:
                err_resp = {"message": {"description": "improper type/format of parameter since_today only int(1) is processable",
                                        "method": "GET", "name": "Failed obtaining activities which are taking place since today",
                                        "status": 422, "timestamp": timestamp}}
                return err_resp, 422


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


        #date = date.replace("_", "-")
        err_resp = {"message": {"description": "Provided bad format of date",
                                "method": "GET", "name": "Failed obtaining activities", "status": 422,
                                "timestamp": timestamp}}
        checked = False
        if (valid_date_day(date) and len(date) == 10):
            checked = True

        if (valid_date_Y_m(date) and len(date) == 7):
            checked = True

        if (valid_date_Y(date) and len(date) == 4):
            checked = True

        if checked is False:
            return err_resp, 422

        cmd = """SELECT a.date, t.name_of_service, f.city, f.street, f.house_number, p.price, u.first_name, u.last_name, u.email,
              (SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.activity_id=a.id GROUP BY p.activity_id), a.id
              FROM fit.activities a 
              INNER JOIN fit.facilities f ON a.facility_id=f.id
              INNER JOIN fit.price_list p ON a.price_id=p.id
              INNER JOIN fit.users u ON u.is_instructor=1 AND u.id=a.instructor_id
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