from datetime import datetime
from myapplication import db


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    house_number = db.Column(db.Integer, nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(600), nullable=False)
    # 1 - is instructor; 0 - not instructor
    is_instructor = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 0 - not, 1 - confirmed
    confirmed = db.Column(db.Integer, nullable=False, default=0)
    #confirmed = db.Column(db.Boolean, default=False)

    user_participations = db.relationship('Participation', backref='user_participations', lazy=True)
    user_subscriptions = db.relationship('Subscriptions', backref='user_subscriptions', lazy=True)
    user_instructor_classes = db.relationship('Classes', backref='user_instructor_classes', lazy=True)


# class Instructors(db.Model):
#     __tablename__ = 'instructors'
#     __table_args__ = {'extend_existing': True, 'schema': 'fit'}
#
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(100), nullable=False)
#     last_name = db.Column(db.String(100), nullable=False)
#     city = db.Column(db.String(100), nullable=False)
#     street = db.Column(db.String(100), nullable=False)
#     house_number = db.Column(db.Integer, nullable=False)
#     postcode = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False, unique=True)
#     password = db.Column(db.String(600), nullable=False)
#
#     instructor_classes = db.relationship('Classes', backref='instructor_classes', lazy=True)


class Facilities(db.Model):
    __tablename__ = 'facilities'
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    house_number = db.Column(db.Integer, nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

    facility_classes = db.relationship('Classes', backref='facility_activity', lazy=True)
    facility_subscription = db.relationship('Subscriptions', backref='facility_subscription', lazy=True)


class PriceList(db.Model):
    __tablename__ = 'price_list'
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)


class Subscriptions(db.Model):
    __tablename__ = "subscriptions"
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('fit.users.id'))
    facility_id = db.Column(db.Integer, db.ForeignKey('fit.facilities.id'))
    price_id = db.Column(db.Integer, db.ForeignKey('fit.price_list.id'))


class Classes(db.Model):
    __tablename__ = "classes"
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime("%Y-%m-%d %H-%M"))
    type_of_classes = db.Column(db.String(100), nullable=False)

    #instructor_id = db.Column(db.Integer, db.ForeignKey('fit.instructors.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('fit.users.id'))
    facility_id = db.Column(db.Integer, db.ForeignKey('fit.facilities.id'))
    price_id = db.Column(db.Integer, db.ForeignKey('fit.price_list.id'))


class Participation(db.Model):
    __tablename__ = 'participation'
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('fit.users.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('fit.classes.id'))


class BlackListToken(db.Model):
    id: int
    token: str

    __tablename__ = 'BlackListToken'
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        """Static method which purpose is to check whether the token is already in the blacklist. False - doesn't exist,
            True - exists.

            PARAMETERS:
                auth_token: str
            RETURNS:
                bool"""
        # check whether auth token has been blacklisted
        res = BlackListToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return False
        else:
            return True

class Test(db.Model):
    __tablename__ = 'participation'
    __table_args__ = {'extend_existing': True, 'schema': 'fit'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
#db.create_all()
