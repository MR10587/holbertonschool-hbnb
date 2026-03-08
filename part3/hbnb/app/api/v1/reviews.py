from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        # get all information which we need for check out
        current_user = get_jwt_identity()
        review_data = api.payload
        place = facade.get_place(review_data['place_id'])

        #checking process
        if not place:
            return {'error': 'Place not found'}, 404
        if str(place.owner.id) == str(current_user):
            return {'error': 'You cannot review your own place'}, 400
        all_reviews = facade.get_all_reviews()
        for r in all_reviews:
            if str(r.place.id) == str(review_data['place_id']) and str(r.user.id) == str(current_user):
                return {'error': 'You have already reviewed this place'}, 400

        review_data['user_id'] = current_user

        #checking completed successfully, creating review
        try:
            new_review = facade.create_review(review_data)
            if not new_review:
                raise ValueError('ValueError')
            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'user_id': new_review.author.id,
                'place_id': new_review.place.id
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        data = facade.get_all_reviews()
        review_list = [
            {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.author.id,
                'place_id': review.place.id
            } for review in data
        ]
        return review_list


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        # 1. Пытаемся получить данные из фасада
        data = facade.get_review(review_id)

        # 2. Проверяем, существует ли объект (не None ли он?)
        if not data:
            return {"message": f"Review {review_id} not found"}, 404

        # 3. Если объект есть, возвращаем данные с кодом 200
        return {
            'id': data.id,
            'text': data.text,
            'rating': data.rating,
            'user_id': data.author.id,
            'place_id': data.place.id
        }, 200
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, review_id):
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        """Update a review's information"""
        current_user = get_jwt_identity()
        review_update = api.payload
        review = facade.get_review(review_id)

        # Checking guys
        if not review:
            return {'error': 'Review not found'}, 404
        if not is_admin and str(current_user) != str(review.author.id):
            return {'error': 'Unauthorized action.'}, 403

        #creating
        try:
            updated_review = facade.update_review(review_id, review_update)
            if not updated_review:
                return {'error': 'Review not found'}, 404
            return {'message': 'Review updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)

        #checking
        if not review:
            return {'error': 'Review not found'}, 404
        if not is_admin and str(current_user) != str(review.author.id):
            return {'error': 'Unauthorized action.'}, 403

        """Delete a review"""
        review_delete = facade.get_review(review_id)
        if not review_delete:
            return {'message': 'Review not found'}, 404
        facade.delete_review(review_id)
        return {'message': 'Review Deleted Successfully'}, 200