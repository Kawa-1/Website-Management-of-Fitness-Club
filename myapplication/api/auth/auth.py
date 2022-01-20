import re

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