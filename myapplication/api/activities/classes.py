from flask_restful import Resource
from flask import request, json, jsonify
from datetime import datetime
from myapplication.api.activities.check import check_date_format
from myapplication import db

# class involved with classes table
class ActivityApi(Resource):
    def get(self, date: str):
        err_resp = {"errors": [{"description": "Provided bad format of date",
                                "method": "GET", "name": "Failed obtaining classes", "status": 400, "timestamp": datetime.now()}]}
        err_resp = json.dumps(err_resp, indent=4, sort_keys=True)

        date = date.replace("_", "-")
        if not check_date_format(date):
            return err_resp, 400

        cmd = "SELECT * FROM fit.classes WHERE classes.date~*'^%s.*'" % date
        activity = db.session.execute(cmd).cursor.fetchall()
        print(activity)
        print(len(activity))
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









