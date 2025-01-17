from flask_restful import Resource, reqparse
from hmac import compare_digest
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
from models import UserModel
from models import CounselorModel

class UserRegister(Resource):
    _user_parser = reqparse.RequestParser()
    _user_parser.add_argument('user_name',
                              type=str,
                              required=True,
                              help="This field cannot be blank."
                              )
    _user_parser.add_argument('password',
                              type=str,
                              required=True,
                              help="This field cannot be blank."
                              )
    _user_parser.add_argument('user_subname',
                              type=str,
                              required=True,
                              help="This field cannot be blank."
                              )
    _user_parser.add_argument('user_type',
                            type=str,
                            required=True,
                            help="This field cannot be blank."
                            )

    def post(self):
        data = UserRegister._user_parser.parse_args()

        if UserModel.find_by_username(data['user_name']):
            return {"message": "A user with that email already exists"}, 400

        user = UserModel(data['user_name'],data['user_subname'],data['password'],data['user_type'])
        user.save_to_db()
        return {"message": "User created successfully."}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    def get(self):
        user_id = 1

        user = UserModel.find_by_id(user_id)
        if not user:
            user = CounselorModel.find_by_id(user_id)
            if not user :
                return {'message': 'User Not Found'}, 404
        return user.json(), 200

    def delete(self):
        user_id = 1

        user = UserModel.find_by_user_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200

class UserLogin(Resource):
    _user_parser = reqparse.RequestParser()
    _user_parser.add_argument('user_name',
                              type=str,
                              required=True,
                              help="This field cannot be blank."
                              )
    _user_parser.add_argument('password',
                              type=str,
                              required=True,
                              help="This field cannot be blank."
                              )
    def post(self):
        data = UserLogin._user_parser.parse_args()
        user = UserModel.find_by_username(data['user_name'])

        if not user :
            user = CounselorModel.find_by_username(data['user_name'])

        # this is what the `authenticate()` function did in security.py
        if user and compare_digest(user.password, data['password']):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_id':user.id,
                'user_type':user.user_type
            }, 200

        return {"message": "Invalid Credentials!"}, 401