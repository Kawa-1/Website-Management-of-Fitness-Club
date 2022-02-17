import jwt
from flask_restful import Resource, request, current_app, marshal_with, fields
from datetime import datetime, timedelta
from flask import json, url_for, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from bleach import clean
from myapplication.api.auth.auth import check_email, check_postcode, check_number, send_email_confirm, token_required
from myapplication import db
from myapplication.models import Users, BlackListToken
from myapplication.error_handler.err_handler import error_handler
from myapplication.global_helpers import valid_date_day

timestamp = str(datetime.utcnow())


class Test(Resource):
    @token_required
    def get(self):
        #send_email_confirm("Papercut@user.com")
        return "git"

    def post(self):
        return "HEJ"


class UserApi(Resource):
    #user_fields = {"message": {"description": "Current user returned", "name": "user info", "status": 200, "method": "GET",
    #                        "timestamp": timestamp},
    #            "user": {"first_name": fields.String, "last_name": fields.String, "city": fields.String,
    #                     "street": fields.String, "house_number": fields.Integer, "postcode": fields.String,
    #                     "email": fields.String, "is_instructor": fields.Integer,
    #                     "created_at": fields.DateTime(dt_format='rfc822'), "confirmed": fields.Integer}}

    #@marshal_with(user_fields)
    @token_required
    def get(self):
        resp = {"message": {"description": "Current user returned", "name": "user info", "status": 200, "method": "GET",
                            "timestamp": timestamp},
                "user": {"id":g.user.id, "first_name": g.user.first_name, "last_name": g.user.last_name, "city": g.user.city,
                         "street": g.user.street, "house_number": g.user.house_number, "postcode": g.user.postcode,
                         "email": g.user.email, "is_instructor": g.user.is_instructor,
                         "created_at": str(g.user.created_at), "confirmed": g.user.confirmed}}
        resp = jsonify(resp)
        resp.status_code = 200
        return resp
        # return g.user


class ValidateUserSubscription(Resource):
    @token_required
    def post(self):
        """Validating date based on date posted in body .e.g.
        {"date": %Y-%m-%d}
        """
        post_data = request.get_json()
        date_then = post_data.get('date')

        check = valid_date_day(date_then)
        date_then = clean(date_then)
        if check is False:
            err_resp = {"message": {"description": "Improper format of date",
                                "method": "POST", "name": "bad format of date", "status": 422,
                                "timestamp": timestamp}}
            return err_resp, 422

        cmd = """SELECT s.id, s.start_date, s.end_date, t.name_of_service, f.city, f.street, f.house_number, pr.price
                FROM fit.subscriptions s
                INNER JOIN fit.types_of_services t ON s.service_id=t.id
                INNER JOIN fit.facilities f ON s.facility_id=f.id
                INNER JOIN fit.price_list pr ON s.price_id=pr.id
                WHERE \'%s\' BETWEEN s.start_date AND s.end_date AND s.user_id=%d
                ORDER BY s.start_date DESC""" % (date_then, g.user.id)

        user_valid_subs = db.session.execute(cmd).cursor.fetchall()

        if len(user_valid_subs) == 0:
            resp = {"message": {"description": "User has no valid subscriptions right now",
                                   "method": "POST", "name": "Lack of subscriptions", "status": 204,
                                   "timestamp": timestamp}}
            return resp, 204

        resp = {"message": {"description": "Valid subscriptions returned",
                                   "method": "POST", "name": "valid subscriptions by user", "status": 200,
                                   "timestamp": timestamp},
                "subscriptions": []}

        for sub in user_valid_subs:
            resp["subscriptions"].append({"id": resp[0], "start_date": resp[1], "end_date": resp[2], "name_of_service": resp[3],
                                          "city": resp[4], "street": resp[5], "house_number": resp[6], "price": resp[7]})

        return resp, 200




class RegisterUserApi(Resource):
    def post(self):
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        city = request.form.get('city')
        street = request.form.get('street')
        house_number = request.form.get('house_number')
        postcode = request.form.get('postcode')
        email = request.form.get("email")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")

        # [(1, 'Kamil', 'Kamilowy', 'BC', 'naulicy', 9, '40', 'tarantino@o2.com', 'plain_text_pass', None, None)]
        user = Users.query.filter_by(email=email).first()
        print(user)
        cmd = 'SELECT * FROM fit.users WHERE email=\'%s\'' % email
        user = db.session.execute(cmd).cursor.fetchone()
        print(user)

        if not first_name or not last_name or not city or not street or not house_number or not postcode or not email or\
            not password or not repeat_password:
            err_resp = {"message": {"description": "One of the fields has not been provided",
                                   "method": "POST", "name": "Failed registration", "status": 400,
                                   "timestamp": timestamp}}
            return err_resp, 400

        if check_email(email) is False:
            err_resp = {"message": {"description": "Format of email is incorrect",
                                    "method": "POST", "name": "Failed registration", "status": 400,
                                    "timestamp": timestamp}}
            return err_resp, 422

        if user:
            err_resp = {"message": {"description": "Such user already exists",
                                    "method": "POST", "name": "Failed registration", "status": 400,
                                    "timestamp": timestamp}}
            return err_resp, 409

        if len(first_name) > 30 or len(first_name) < 2 or len(last_name) > 30 or len(last_name) < 2 or len(city) > 30 or len(city) < 2 or\
            len(street) > 30 or len(street) < 2 or len(password) > 30 or len(password) < 8:
            err_resp = {"message": {"description": "Provided empty field, bad semantics, something exists so far etc.",
                                   "method": "POST", "name": "Failed registration", "status": 400,
                                   "timestamp": timestamp}}
            return err_resp, 422

        if check_postcode(postcode) is False:
            err_resp = {"message": {"description": "Check postcode failed",
                        "method": "POST", "name": "Failed registration", "status": 400,
                        "timestamp": timestamp}}
            return err_resp, 422

        if password != repeat_password:
            err_resp = {"message": {"description": "Passwords are not correct",
                                   "method": "POST", "name": "Failed registration", "status": 400,
                                   "timestamp": timestamp}}
            return err_resp, 422

        if check_number(house_number) is False:
            err_resp = {"message": {"description": "Check house number failed",
                                   "method": "POST", "name": "Failed registration", "status": 400,
                                   "timestamp": timestamp}}
            return err_resp, 422

        first_name = clean(first_name)
        last_name = clean(last_name)
        city = clean(city)
        street = clean(street)
        house_number = clean(house_number)
        postcode = clean(postcode)
        email = clean(email)
        password = clean(password)


        password = generate_password_hash(password)
        new_user = Users(first_name=first_name, last_name=last_name, city=city, street=street, house_number=house_number,
                         postcode=postcode, email=email, password=password)
        send = send_email_confirm(email)

        if send[0] is False:
            err_resp = {"message": {"description": "Confrimation email could not be send", "error": "Mail was not sent",
                         "method": "POST", "name": send[1], "status": 500,
                         "timestamp": timestamp}}
            return err_resp, 500

        db.session.add(new_user)
        db.session.commit()

        created_resp = {"message": {"description": "new user created", "confirmation_email": send[1], "status": 201,
                                     "name": "registration", "method": "POST", "timestamp": timestamp}, "user":
            {"first_name": first_name, "last_name": last_name, "confirmed": False}}
        return created_resp, 201


class SendEmailConfirmationApi(Resource):
    def post(self):
        email = request.headers.get('email')
        email = clean(email)
        print(email)
        if email is None or not check_email(email):
            err_resp = {"message": {"description": "Bad format of email", "confirmation_email": "Has not been sent", "status": 400,
                                        "name": "email confirmation; error", "method": "POST", "timestamp": timestamp}}
            return err_resp, 422

        send = send_email_confirm(email)
        if send[0] is False:
            err_resp = {"message": {"description": "Mail has not been sent", "confirmation_email": "Has not been sent",
                                    "status": 500, "name": send[1], "method": "POST", "timestamp": timestamp}}
            return err_resp, 500

        resp = {"message": {"description": "Confirmation mail has been sent", "confirmation_email": send[1], "status": 200,
                                     "name": "confirmation of account", "method": "POST", "timestamp": timestamp}}
        return resp, 200


class ConfirmEmail(Resource):
    def get(self, token=None):
        token: str
        try:
            email = current_app.config['SAFE_EMAIL']
            email = email.loads(token, salt='email-confirm', max_age=3600)
            cmd = "SELECT id FROM fit.users where email=\'%s\'" % email
            user = db.session.execute(cmd).cursor.fetchone()
            if user is None:
                err_resp = {"message": [{"description": "Account couldn't be confirmed", "status": 404,
                                         "name": "This account doesn't exist", "method": "GET", "timestamp": timestamp}]}
                return err_resp, 404

            cmd = "UPDATE fit.users SET confirmed=1 WHERE email=\'%s\'" % email
            db.session.execute(cmd)
            db.session.commit()
            resp = {"message": {"description": "Account has been confirmed", "status": 200, "email": str(email),
                                     "name": "confirm_email", "method": "GET", "timestamp": timestamp}}
            resp = json.dumps(resp, indent=4, sort_keys=True)
            return resp, 200

        except Exception as e:
            # In prod we should change printing straight error...
            err_resp = {"message": [{"description": "Account couldn't be confirmed", "status": 400,
                                     "name": str(e), "method": "GET", "timestamp": timestamp}]}
            err_resp = json.dumps(err_resp, indent=4, sort_keys=True)
            return err_resp, 400


class LoginUserApi(Resource):
    def post(self):
        post_data = request.get_json()
        key = current_app.config['SECRET_KEY']

        email = post_data.get('email')
        password = post_data.get('password')

        email = clean(email)
        password = clean(password)

        user = Users.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            err_resp = {"message": {"description": "Such user doesn't exist or password is incorrect",
                                    "name": "Could not log into", "method": "POST", "status": 400, "timestamp": timestamp}}
            return err_resp, 400

        if user.confirmed == 0:
            err_resp = {"message": {"description": "This account has not been confirmed yet",
                                    "name": "Could not log into", "method": "POST", "status": 400}, "timestamp": timestamp}
            return err_resp, 400


        token = jwt.encode({"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                            "exp": datetime.utcnow() + timedelta(days=1)}, key, algorithm="HS256")

        resp = {"message": {"description": "Token prepared properly", "status": 201, "name": "login", "token": token, "method": "POST",
                            "timestamp": timestamp},
                "user": {"email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                         "is_instructor": user.is_instructor}}
        resp = jsonify(resp)
        resp.status_code = 201
        return resp


class LogoutUserApi(Resource):
    @token_required
    def post(self):
        auth_token = request.headers.get('Authorization').split(" ")[1]
        auth_token = clean(auth_token)
        print('logout: ', auth_token)

        if auth_token:
            if not BlackListToken.check_blacklist(auth_token):
                if isinstance(auth_token, str):
                    blacklist_token = BlackListToken(token=auth_token)
                    db.session.add(blacklist_token)
                    db.session.commit()
                    resp = {"message": {"description": "User has logged out", "status": 200, "name": "Token is blacklisted",
                                        "method": "POST", "timestamp": timestamp}}
                    return resp, 200

                else:
                    err_resp = {"message": {"description": "User could not log out; token can't be blacklisted", "status": 400,
                                        "name": "Token is invalid",
                                        "method": "POST", "timestamp": timestamp}}
                    return err_resp, 400

            else:
                err_resp = {"message": {"description": "User could not log out; token can't be blacklisted", "status": 200,
                                        "name": "Token is already in blacklist",
                                        "method": "POST", "timestamp": timestamp}}
                return err_resp, 400

        #else:
        #    err_resp = {"message": {"description": "User could not log out; token can't be blacklisted", "status": 400,
        #                            "name": "Lack of token",
        #                            "method": "POST", "timestamp": timestamp}}
        #    return err_resp, 400


class PasswordUserApi(Resource):
    @token_required
    def put(self):
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        if password != repeat_password:
            err_resp = {"message": {"description": "Password is not the same as 'repeat_password'", "status": 400,
                                    "name": "Can't change password ",
                                    "method": "PUT", "timestamp": timestamp}}
            return err_resp, 400

        password = clean(password)
        password = generate_password_hash(password)

        cmd = "UPDATE fit.users SET users.password=\'%s\' WHERE users.email=\'%s\'" % (password, g.user.email)
        db.session.execute(cmd)
        db.session.commit()

        resp = {"message": {"description": "Password has been changed'", "status": 201,
                                    "name": "Password has been changed",
                                    "method": "PUT", "timestamp": timestamp}}
        return resp, 201


class refresh_token(Resource):
    @token_required
    def post(self):
        key = current_app.config['SECRET_KEY']
        token = request.headers.get("Authorization").split(" ")[1]
        token = clean(token)

        ep = datetime(1970, 1, 1, 0, 0, 0)
        now = (datetime.utcnow() - ep).total_seconds()
        expire = jwt.decode(token, key).get("exp")
        time_to_expire = expire - now

        if time_to_expire > 7200:
            err_resp = {"message": {"description": "Only tokens with expire time < 2h can be refreshed", "status": 400,
                                "name": "Token has not been refreshed",
                                "method": "POST", "timestamp": timestamp}}
            return err_resp, 400

        err_resp = {"message": {"description": "Token can't be blacklisted", "status": 400,
                                "name": "Token is invalid",
                                "method": "POST", "timestamp": timestamp}}

        if token:
            if not BlackListToken.check_blacklist(token):
                if isinstance(token, str):
                    blacklist_token = BlackListToken(token=token)
                    db.session.add(blacklist_token)
                    db.session.commit()

                else:
                    return err_resp, 400

            else:
                return err_resp, 400

        else:
            return err_resp, 400

        new_token = jwt.encode({"id": g.user.id, "email": g.user.email, "first_name": g.user.first_name, "last_name": g.user.last_name,
                            "exp": datetime.utcnow() + timedelta(days=1)}, key, algorithm="HS256")

        resp = {"message": {"description": "Old Token has been blacklisted and new one is generated", "status": 200, "name": "Old Token is blacklisted; new one generated",
                            "method": "POST","token": new_token, "timestamp": timestamp}}

        return resp, 201





