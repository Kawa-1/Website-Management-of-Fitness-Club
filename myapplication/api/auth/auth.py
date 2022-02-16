import jwt
import re
from functools import wraps
from flask import request, json, current_app, url_for, g
from flask_mail import Message
from datetime import datetime
from myapplication import mail
from myapplication.models import Users, BlackListToken

timestamp = str(datetime.utcnow())

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = None

		if 'Authorization' in request.headers:
			auth_value = request.headers['Authorization']
			try:
				token = auth_value.split(" ")[1]
				if BlackListToken.check_blacklist(token):
					err_resp = {
						"message": {"description": "Token already blacklisted",
									"name": "Token already blacklisted",
									"status": 401, 'timestamp': timestamp}}
					return err_resp, 401
			except Exception as e:
				err_resp = {
					"message": {"description": "Value of header 'Authorization' is in bad format; Proper format: 'Bearer \
											   `cipher`", "name": "Bad format of 'Authorization' header",
								"status": 401, 'timestamp': timestamp}}
				return err_resp, 401

		if not token:
			err_resp = {"message": {"description": "Valid token is missing", "name": "token required", "status": 401,
									'timestamp': timestamp}}
			return err_resp, 401

		try:
			data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
			print("decoded ", data)
			g.user = Users.query.filter_by(id=data['id']).first()
			if g.user is None:
				err_resp = {
					"message": {"description": "Such user doesn't exist", "status": 401, "name": "Cannot auth; token required",
								'timestamp': timestamp}}
				return err_resp, 404

		except jwt.ExpiredSignatureError:
			err_resp = {"message": {"description": "token expired!", "status": 401, "name": "Not active token",
									'timestamp': timestamp}}
			print('error 53', jwt.ExpiredSignature)
			return err_resp, 401

		return f(*args, **kwargs)
	return decorator


def send_email_confirm(email: str):
	token = current_app.config['SAFE_EMAIL']
	token = token.dumps(email, salt='email-confirm')

	msg = Message('Confirmation mail from FITNESS CLUB!!', sender="fitness_management@Fitness.com", recipients=[email])
	#link = url_for("/api/confirm_email", token=token, _external=True)
	link = "http://127.0.0.1:5000/api/confirm_email/{}".format(token)
	msg.body = """Your activation link for Fitness club is
				{}
				PLease ignore this email if it is not you!
				""".format(link)
	try:
		mail.send(msg)
		return True, "Confirmation mail has been sent"
	except Exception as e:
		print(e)
		return False, str(e)


def check_email(email: str) -> bool:
	regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
	email = str(email)
	if re.search(regex, email):
		return True
	else:
		return False

def check_postcode(postcode: str) -> bool:
	regex = '^[0-9]{2}[-][0-9]{3}$'
	postcode = str(postcode)
	if re.search(regex, postcode):
		return True
	else:
		return False

def check_phone(phone: str) -> bool:
	regex = '^[0-9]{9}$'
	phone = str(phone)
	if re.search(regex, phone):
		return True
	else:
		return False

def sanitize(text: str) -> str:
        return (
            text.replace("&", "&amp;").
                replace('"', "&quot;").
				replace('\'', "&quot;").
				replace('--',"_").
				replace("||", "|").
                replace("<", "&lt;").
                replace(">", "&gt;")
        )

def check_number(number: str) -> bool:
	regex = '^[0-9]+$'
	number = str(number)
	if re.search(regex, number):
		return True
	else:
		return False