from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('login', description='User login operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid email or password')
    def post(self):
        """Authenticate user and return a JWT token"""
        login_data = api.payload
        email = login_data['email']
        password = login_data['password']

        user = facade.get_user_by_email(email)
        if not user or not facade.check_password(user, password):
            return {'error': 'Invalid email or password'}, 401

        # Generate JWT token with user id and is_admin claim
        access_token = facade.create_access_token(identity=user.id, additional_claims={'is_admin': user.is_admin})
        return {'access_token': access_token}, 200