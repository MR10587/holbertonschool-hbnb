from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

user_model_updated = api.model('UserReg', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

user_update_model = api.model('UserReg', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email of the user'),
    'password': fields.String(description='Password of the user')
})

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
         """A protected endpoint that requires a valid JWT token"""
         print("jwt------")
         print(get_jwt_identity())
         current_user = get_jwt_identity() # Retrieve the user's identity from the token
         #if you need to see if the user is an admin or not, you can access additional claims using get_jwt() :
         # additional claims = get_jwt()
         #additional claims["is_admin"] -> True or False
         return {'message': f'Hello, user {current_user}'}, 200


@api.route('/')
class UserList(Resource):
    @api.expect(user_model_updated, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(403, 'Admin privileges required')
    #@jwt_required()
    def post(self):
    #    current_user = get_jwt()
    #    if not current_user.get("is_admin", False):
    #        return {'error': 'Admin privileges required'}, 403

        """Register a new user"""
        user_data = api.payload
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        return {
            'id': new_user.id,
            'message': 'User successfully created'
        }, 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of all users"""
        users = facade.get_all_users()
        return [{
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email
        } for u in users], 200

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }, 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)


        current_user = get_jwt_identity()
        user_data = api.payload
        email = user_data.get('email')

        if not is_admin:
            user_data.pop('is_admin', None)  # Удаляем ключ is_admin, если он там был

        # Checking
        if not is_admin and str(current_user) != str(user_id):
            return {'error': 'Unauthorized action'}, 403


        if not is_admin and ('email' in user_data or 'password' in user_data):
            return {'error': 'You cannot modify email or password'}, 400

        # Ensure email uniqueness
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        """Update user information"""
        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            return {'error': 'User not found'}, 404
        return {
            'id': updated_user.id,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'email': updated_user.email
        }, 200
