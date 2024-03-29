from flask import g, request
from flask_restful import Resource
from myapplication.api.auth.auth import token_required
from myapplication import db
from datetime import datetime
from myapplication.api.instructors.api import check_int
from myapplication.models import Participation
from myapplication.logger import get_logger

timestamp = str(datetime.utcnow())
log = get_logger(__name__)

class UserActivityApi(Resource):
    @token_required
    def get(self):
        user_id = g.user.id
        # TODO: Get each activity in which particular user took part; DESC - 1st row will be the newest
        # cmd =  """SELECT t.name_of_service, a.date, u.first_name, u.last_name, u.email, f.city, f.street, f.house_number,
        # (SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.activity_id=c.id GROUP BY c.id), c.id, pr.price, pr.service
        #             FROM fit.activities a
        #             INNER JOIN fit.users u ON a.instructor_id=u.id AND u.instructor_id=1
        #             INNER JOIN fit.facilities f ON a.facility_id=f.id
        #             INNER JOIN fit.participation p ON p.activity_id=a.id
        #             INNER JOIN fit.price_list pr ON pr.id=a.price_id
        #             INNER JOIN fit.types_of_services t ON t.id=a.type_of_service_id AND t.is_subscription=0
        #             WHERE %d IN (SELECT p1.user_id FROM fit.participation p1 WHERE p1.activity_id=a.id)
        #             GROUP BY a.id
        #             ORDER BY a.date DESC;""" % user_id
        cmd = """SELECT t.name_of_service, a.date, u.first_name, u.last_name, u.email, f.city, f.street, f.house_number, 
                    (SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.activity_id=a.id GROUP BY p.activity_id) as sum_of_users, a.id, pr.price
                    FROM fit.activities a 
                    INNER JOIN fit.users u ON a.instructor_id=u.id AND a.instructor_id=1 
                    INNER JOIN fit.facilities f ON a.facility_id=f.id 
                    INNER JOIN fit.participation p ON p.activity_id=a.id
                    INNER JOIN fit.price_list pr ON pr.id=a.price_id
                    INNER JOIN fit.types_of_services t ON t.id=a.type_of_service_id AND t.is_subscription=0
                    WHERE %d IN (SELECT p1.user_id FROM fit.participation p1 WHERE p1.activity_id=a.id);""" % user_id

        classes_user_took = db.session.execute(cmd).cursor.fetchall()
        dictionary = {"message": {"description": "Activities returned", "name": "Activities returned",
                                  "method": "GET", "timestamp": timestamp}, "activities": []}

        for activity in classes_user_took:
            dictionary['activities'].append({"name_of_service": activity[0], "date": activity[1],
                                             "instructor_name": activity[2], "instructor_surname": activity[3],
                                             "instructor_email": activity[4], "fitness_city": activity[5],
                                             "fitness_street": activity[6], "fitness_house_number": activity[7],
                                             "number_users_enrolled_total": activity[8], "id": activity[9],
                                             "price": activity[10]})

        return dictionary, 200

    @token_required
    def post(self):
        """
        Signing up for activities. ID indicates id of activity
        DESIRED BODY: e.g. {"id": 1}
        """
        body = request.get_json(silent=True)
        activity_id = body.get('id')

        if not body or activity_id is None or not isinstance(activity_id, int):
            err_resp = {"message": {"description": "lack of information to which activity user want to be signed",
                                    "status": 404, "name": "lack of body; json", "method": "POST", "timestamp":
                                    timestamp}}
            return err_resp, 404

        # isinstance or check_int... However i will leave it how it is; project is made majorly for research purposes; university project
        check = check_int(activity_id=activity_id)

        if check[0] is False:
            err_resp = {
                "message": {"description": "activity_id is not an int", "name": "Bad type in form",
                            "status": 400, "method": "PUT", "timestamp": timestamp}}
            return err_resp, 400

        cmd = "SELECT COUNT(p.user_id) FROM fit.participation p WHERE p.activity_id=%d" % activity_id
        number_of_users = db.session.execute(cmd).cursor.fetchone()

        if number_of_users is None:
            err_resp = {"message": {
                "description": "Such activity doesn't exist",
                "status": 404, "name": "cannot sign up", "method": "POST", "timestamp": timestamp}}
            return err_resp, 404

        number_of_users = number_of_users[0]
        if number_of_users >= 15:
            err_resp = {"message": {"description": "User is not allowed to join this activity bcs number of users is max, it means 15",
                                    "status": 400, "name": "cannot sign up", "method": "POST", "timestamp": timestamp}}
            return err_resp, 400

        cmd = "SELECT user_id FROM fit.participation WHERE user_id=%d AND activity_id=%d" %  (g.user.id, activity_id)
        res = db.session.execute(cmd).cursor.fetchone()
        if res is not None:
            err_resp = {"message": {
                "description": "User is already signed for this activity",
                "status": 400, "name": "Already signed up", "method": "POST", "timestamp": timestamp}}
            return err_resp, 400


        db.session.add(Participation(user_id=g.user.id, activity_id=activity_id))
        db.session.commit()

        resp = {"message": {"description": "User properly signed up for activity with email: {} and activity_id: {}".format(g.user.email, activity_id),
                                    "status": 201, "name": "signed up for activity", "method": "POST", "timestamp": timestamp}}
        return resp, 201

    @token_required
    def delete(self, activity_id=None):
        if not isinstance(activity_id, int):
            try:
                activity_id = int(activity_id)
            except Exception as e:
                err_resp = {"message": {
                    "description": "activity_id bad type",
                    "status": 422, "name": "cannot delete", "method": "DELETE", "timestamp": timestamp}}
                return err_resp, 422

        cmd = "SELECT id FROM fit.activities WHERE id=%d" % activity_id
        res = db.session.execute(cmd).cursor.fetchone()

        if activity_id is None or res is None:
            err_resp = {"message": {
                "description": "Such activity doesn't exist, user cannot be signed off",
                "status": 400, "name": "cannot delete", "method": "DELETE", "timestamp": timestamp}}
            return err_resp, 400

        cmd = "DELETE FROM fit.participation WHERE user_id=%d AND activity_id=%d" % (g.user.id, activity_id)
        db.session.execute(cmd)
        db.session.commit()

        resp = {"message": {
            "description": "User properly signed off the activity user's email: {} and activity_id: {}".format(g.user.email, activity_id),
            "status": 202, "name": "User deleted from activity", "method": "DELETE", "timestamp": timestamp}}
        return resp, 202


# TODO: it is already here higher, we are getting every single activity involved with user
class UsersOnParticipation(Resource):
    @token_required
    def get(self):
            pass