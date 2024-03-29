from flask import request, g
from flask_restful import Resource
from myapplication import db
from datetime import datetime
from myapplication.logger import get_logger

timestamp = str(datetime.utcnow())
log = get_logger(__name__)

class ServiceSubscription(Resource):
    def get(self):
        cmd = """SELECT * FROM fit.types_of_services WHERE is_subscription=1"""
        subs = db.session.execute(cmd).cursor.fetchall()

        if len(subs) == 0:
            resp = {
                "message": {"description": "Subscriptions don't exist!",
                            "name": "lack of subscriptions",
                            "status": 200, "method": "GET", "timestamp": timestamp},
            "subscriptions": []}
            # 204 should be
            return resp, 200

        resp = {
            "message": {"description": "Subscriptions returned!",
                        "name": "Available subscriptions",
                        "status": 200, "method": "GET", "timestamp": timestamp},
            "subscriptions": []}

        for sub in subs:
            resp["subscriptions"].append({"id": sub[0], "name_of_service": sub[1]})

        return resp, 200


class ServiceActivity(Resource):
    def get(self):
        cmd = """SELECT * FROM fit.types_of_services WHERE is_subscription=0"""
        activities = db.session.execute(cmd).cursor.fetchall()

        if len(activities) == 0:
            resp = {
                "message": {"description": "Activities don't exist!",
                            "name": "lack of activities",
                            "status": 200, "method": "GET", "timestamp": timestamp},
                "activities": []}
            # 204 should be
            return resp, 200

        resp = {
            "message": {"description": "Activities returned!",
                        "name": "Available activities",
                        "status": 200, "method": "GET", "timestamp": timestamp},
            "activities": []}

        for activitiy in activities:
            resp["activities"].append({"id": activitiy[0], "name_of_service": activitiy[1]})

        return resp, 200