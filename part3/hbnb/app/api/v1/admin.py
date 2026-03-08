from flask import request
from app.services import facade
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

api = Namespace('admin', description='Admin operations')

@api.route('/make-me-admin')
class MakeMeAdmin(Resource):
    """
    DEV ONLY!
    Promote the currently logged-in user to admin.
    You MUST Login again to get an admin token.
    """
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        facade.update_user(user_id, {"is_admin": True})
        return {
            "message": "You are now admin. Login again to get an admin token."
        }, 200

@api.route('/users/<user_id>')
class AdminUserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt()

        # If 'is_admin' is part of the identity payload
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        data = request.get_json() or {}


        if 'email' in data:
            email = (data.get('email') or "").lower().strip()
            if not email:
                return {'error': 'Email cannot be empty'}

        email = data.get('email')

        if email:
            # Check if email is already in use
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email is already in use'}, 400

        updated_user = facade.update_user(user_id, data)
        if not updated_user:
            return {'error': 'user not found'}, 404

        return {
            'id': updated_user.id,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'email': updated_user.email,
            'is_admin': updated_user.is_admin
        }, 200