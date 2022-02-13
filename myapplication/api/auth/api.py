import jwt
from flask_restful import Resource, request, current_app
from datetime import datetime, timedelta
from flask import json, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bleach import clean
from myapplication.api.auth.auth import check_email, check_postcode, check_number, send_email_confirm, token_required
from myapplication import db
from myapplication.models import Users, BlackListToken
from myapplication.error_handler.err_handler import error_handler


class Test(Resource):
    def get(self):
        send_email_confirm("Papercut@user.com")

    def post(self):
        return "HEJ"

class RegisterUserApi(Resource):
    def post(self):
        err_resp = {"errors": {"description": "Provided empty field, bad semantics, something exists so far etc.",
                                "method": "POST", "name": "Failed registration", "status": 400, "timestamp": str(datetime.utcnow())}}

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
        if check_email(email) is False:
            err_resp = {"errors": {"description": "Format of email is incorrect",
                                    "method": "POST", "name": "Failed registration", "status": 400,
                                    "timestamp": str(datetime.utcnow())}}
            return err_resp, 400

        if user:
            err_resp = {"message": {"description": "Such user already exists",
                                    "method": "POST", "name": "Failed registration", "status": 400,
                                    "timestamp": str(datetime.utcnow())}}
            return err_resp, 400

        if len(first_name) > 30 or len(first_name) < 2 or len(last_name) > 30 or len(last_name) < 2 or len(city) > 30 or len(city) < 2 or\
            len(street) > 30 or len(street) < 2 or len(password) > 30 or len(password) < 8:
            return err_resp, 400

        if check_postcode(postcode) is False:
            return err_resp, 400

        if password != repeat_password:
            return err_resp, 400

        if check_number(house_number) is False:
            return err_resp, 400

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
                         "timestamp": str(datetime.utcnow())}}
            return err_resp, 500

        db.session.add(new_user)
        db.session.commit()

        created_resp = {"message": {"description": "new user created", "confirmation_email": send[1], "status": 201,
                                     "name": "registration", "method": "POST", "timestamp": str(datetime.utcnow())()}, "user":
            {"first_name": first_name, "last_name": last_name, "confirmed": False}}
        created_resp = json.dumps(created_resp, indent=4, sort_keys=True)
        return created_resp, 201


class SendEmailConfirmationApi(Resource):
    def post(self):
        email = request.headers.get('email')
        email = clean(email)
        print(email)
        if email is None or not check_email(email):
            err_resp = {"message": {"description": "Bad format of email", "confirmation_email": "Has not been sent", "status": 400,
                                        "name": "email confirmation; error", "method": "POST", "timestamp": str(datetime.utcnow())}}
            return err_resp, 400

        send = send_email_confirm(email)
        if send[0] is False:
            err_resp = {"message": {"description": "Mail has not been sent", "confirmation_email": "Has not been sent",
                                    "status": 400, "name": send[1], "method": "POST", "timestamp": str(datetime.utcnow())}}
            return err_resp, 400

        resp = {"message": {"description": "Confirmation mail has been sent", "confirmation_email": send[1], "status": 200,
                                     "name": "confirmation of account", "method": "POST", "timestamp": str(datetime.utcnow())}}
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
                err_resp = {"message": [{"description": "Account couldn't be confirmed", "status": 400,
                                         "name": "This account doesn't exist", "method": "GET", "timestamp": str(datetime.utcnow())}]}
                return err_resp, 400

            cmd = "UPDATE fit.users SET confirmed=1 WHERE email=\'%s\'" % email
            db.session.execute(cmd)
            db.session.commit()
            resp = {"message": {"description": "Account has been confirmed", "status": 200, "email": str(email),
                                     "name": "confirm_email", "method": "GET", "timestamp": str(datetime.utcnow())}}
            resp = json.dumps(resp, indent=4, sort_keys=True)
            return resp, 200

        except Exception as e:
            # In prod we should change printing straight error...
            err_resp = {"message": [{"description": "Account couldn't be confirmed", "status": 400,
                                     "name": str(e), "method": "GET", "timestamp": str(datetime.utcnow())}]}
            err_resp = json.dumps(err_resp, indent=4, sort_keys=True)
            return err_resp, 400


class LoginUserApi(Resource):
    def post(self):
        post_data = request.get_json()
        key = current_app.config['SECRET_KEY']

        email = post_data.get('email')
        password = post_data.get('password')

        user = Users.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            err_resp = {"message": {"description": "Such user doesn't exist or password is incorrect",
                                    "name": "Could not log into", "method": "POST", "status": 400, "timestamp": str(datetime.utcnow())}}
            err_resp = json.dumps(err_resp, indent=4, sort_keys=True)
            return err_resp, 400

        if user.confirmed == 0:
            err_resp = {"message": {"description": "This account has not been confirmed yet",
                                    "name": "Could not log into", "method": "POST", "status": 400}, "timestamp": str(datetime.utcnow())}
            err_resp = json.dumps(err_resp, indent=4, sort_keys=True)
            return err_resp, 400


        token = jwt.encode({"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                            "exp": datetime.utcnow() + timedelta(days=1)}, key, algorithm="HS256")

        resp = {"message": {"description": "Token prepared properly", "status": 201, "name": "login", "token": token, "method": "POST",
                            "timestamp": str(datetime.utcnow())()},
                "user": {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "is_instructor": user.is_instructor
                         }}
        return resp, 201


class LogoutUserApi(Resource):
    @token_required
    def post(self, current_user=None):
        auth_token = request.headers['x-access-tokens']

        if current_user is None:
            err_resp = {"message": {"description": "This token is invalid", "status": 403, "name": "Failed blacklisting of token",
                                    "method": "POST", "timestamp": str(datetime.utcnow())}}
            return err_resp, 403

        email_current_user = current_user.email

        if auth_token:
            if BlackListToken.check_blacklist(auth_token):
                if isinstance(auth_token, str):
                    blacklist_token = BlackListToken(token=auth_token)

                    db.session.add(blacklist_token)
                    db.session.commit()
                    resp = {"message": {"description": "User has been logged out", "status": 200, "name": "Token is blacklisted",
                                        "method": "POST", "timestamp": str(datetime.utcnow())}}
                    return resp, 200

                else:
                    err_resp = {"message": {"description": "User could not log out; token can't be blacklisted", "status": 200,
                                        "name": "Token is invalid",
                                        "method": "POST", "timestamp": str(datetime.utcnow())}}
                    return err_resp, 400

            else:
                err_resp = {"message": {"description": "User could not log out; token can't be blacklisted", "status": 200,
                                        "name": "Token is already in blacklist",
                                        "method": "POST", "timestamp": str(datetime.utcnow())}}
                return err_resp, 400

        else:
            err_resp = {"message": {"description": "User could not log out; token can't be blacklisted", "status": 200,
                                    "name": "Lack of token",
                                    "method": "POST", "timestamp": str(datetime.utcnow())}}
            return err_resp, 400


class PasswordUserApi(Resource):
    @token_required
    def put(self, current_user=None):
        token = request.headers.get('x-access-tokens')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        if token is None:
            err_resp = {"message": {"description": "Lack of token", "status": 401,
                                    "name": "Can't change password",
                                    "method": "PUT", "timestamp": str(datetime.utcnow())}}
            return err_resp, 401

        if password != repeat_password:
            err_resp = {"message": {"description": "Password is not the same as 'repeat_password'", "status": 400,
                                    "name": "Can't change password ",
                                    "method": "PUT", "timestamp": str(datetime.utcnow())}}
            return err_resp, 400

        password = generate_password_hash(password)

        cmd = "UPDATE fit.users SET users.password=\'%s\' WHERE users.email=\'%s\'" % password, current_user.email
        db.session.execute(cmd)
        db.session.commit()

        resp = {"message": {"description": "Password has been changed'", "status": 201,
                                    "name": "Password has been changed",
                                    "method": "PUT", "timestamp": str(datetime.utcnow())}}
        return resp, 201









