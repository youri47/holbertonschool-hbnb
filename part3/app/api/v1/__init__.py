from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.auth import api as auth_ns

api = Api(
    title='HBnB API',
    version='1.0',
    description='HBnB Application REST API',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT token. Format: "Bearer {token}"'
        }
    },
    security='Bearer'
)

api.add_namespace(auth_ns, path='/api/v1/auth')
api.add_namespace(users_ns, path='/api/v1/users')
api.add_namespace(places_ns, path='/api/v1/places')
api.add_namespace(reviews_ns, path='/api/v1/reviews')
api.add_namespace(amenities_ns, path='/api/v1/amenities')