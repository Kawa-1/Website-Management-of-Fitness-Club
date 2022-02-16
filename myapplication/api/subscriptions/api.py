from flask import request, g
from flask_restful import Resource
from myapplication import db
from myapplication.api.auth.auth import token_required
from datetime import datetime, timedelta
from myapplication.api.activities.check import check_date_format
from myapplication.models import Subscriptions

timestamp = str(datetime.utcnow())

class StartSubscription(Resource):
    @token_required
    def post(self):
        """This endpoints expect body with every id listed in table subscriptions as well as start_date
            date should be passed in format %Y-%m-%d
            PARAMETERS IN BODY:
                service_id: int
                facility_id: int
                price_id: int
                start_date: str
        """
        def datetime_to_string(date_obj: datetime) -> str:
            """Desired format is "%Y-%m-%d" as string"""
            str_obj = date_obj.strftime("%Y-%m-%d")
            return str_obj

        def string_to_datetime(str_obj: str) -> datetime:
            """Desired format is "%Y-%m-%d" as datetime.datetime"""
            date_obj = datetime.strptime(str_obj, '%Y-%m-%d')
            return date_obj

        post_data = request.get_json()

        service_id = post_data.get('service_id')
        user_id = g.user.id
        facility_id = post_data.get('facility_id')
        price_id = post_data.get('price_id')
        start_date = post_data.get('start_date')

        if service_id is None or not isinstance(service_id, int) or facility_id is None or not isinstance(facility_id, int) or \
                price_id is None or not isinstance(price_id, int) or start_date is None or not isinstance(start_date, str) or \
                not check_date_format(start_date):
            err_resp = {"message": {
                "description": "Not all parameters properly provided",
                "status": 400, "name": "lack of proper parameters", "method": "POST",
                "timestamp": timestamp},
            "provided": post_data}
            return err_resp, 400

        today = datetime_to_string(datetime.utcnow())
        if start_date < today:
            err_resp = {"message": {
                "description": "Cannot make a subscription of pass with older date than today {}".format(today),
                "status": 400, "name": "Invalid date; subscription", "method": "POST",
                "timestamp": timestamp}}
            return err_resp, 400

        cmd = """SELECT * FROM fit.types_of_services WHERE service_id=%d and is_subscription=1""" % service_id
        type_of_pass = db.session.execute('cmd').cursor.fetchone()
        # TODO: check if this values exist in db

        cmd = """SELECT id, (SELECT id FROM fit.facilities WHERE id=%d), (SELECT id FROM fit.price_list WHERE id=%d), 
        (SELECT id FROM fit.users WHERE id=%id) FROM fit.types_of_services WHERE id=%d""" % (facility_id, price_id,
                                                                                             user_id, service_id)
        res = db.session.excute(cmd).cursor.fetchall()

        if res[0] is None or res[1] is None or res[2] is None or res[3] is None:
            err_resp = {"message": {
                "description": "One of the elements of subscription doesn't exist in db",
                "status": 404, "name": "Subscription couldn't be done", "method": "POST",
                "timestamp": timestamp}}
            return err_resp, 404


        # datetime.datetime object
        start_date = string_to_datetime(start_date)
        type_of_pass = type_of_pass[0]
        if type_of_pass == "pass_1d":
            start_date = datetime_to_string(start_date)
            end_date = start_date
            sub = Subscriptions(start_date=start_date, end_date=end_date, service_id=service_id, user_id=user_id,
                                facility_id=facility_id, price_id=price_id)
            db.session.add(sub)
            db.session.commit()
            resp = {"message": {
                "description": "User mad subscription from {} to {}".format(start_date, end_date),
                "status": 201, "name": "Subscription made for 1day", "method": "POST",
                "timestamp": timestamp}}
            return resp, 201

        elif type_of_pass == 'pass_30d':
            end_date = datetime_to_string((start_date + timedelta(days=30)))
            start_date = datetime_to_string(start_date)
            sub = Subscriptions(start_date=start_date, end_date=end_date, service_id=service_id, user_id=user_id,
                                facility_id=facility_id, price_id=price_id)
            db.session.add(sub)
            db.session.commit()
            resp = {"message": {
                "description": "User mad subscription from {} to {}".format(start_date, end_date),
                "status": 201, "name": "Subscription made for 30days", "method": "POST",
                "timestamp": timestamp}}
            return resp, 201

        elif type_of_pass == 'pass_1yr':
            end_date = datetime_to_string((start_date + timedelta(days=365)))
            start_date = datetime_to_string(start_date)
            sub = Subscriptions(start_date=start_date, end_date=end_date, service_id=service_id, user_id=user_id,
                                facility_id=facility_id, price_id=price_id)
            db.session.add(sub)
            db.session.commit()
            resp = {"message": {
                "description": "User mad subscription from {} to {}".format(start_date, end_date),
                "status": 201, "name": "Subscription made for 365 days", "method": "POST",
                "timestamp": timestamp}}
            return resp, 201

        else:
            err_resp = {"message": {
                "description": "Such pass doesn't exist",
                "status": 404, "name": "Subscription couldn't be done", "method": "POST",
                "timestamp": timestamp}}
            return err_resp, 404


