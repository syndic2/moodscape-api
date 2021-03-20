import graphene
from flask_graphql_auth import query_jwt_required
from bson.objectid import ObjectId

from .types import User, ProtectedUser, UserInput
from extensions import mongo

class UserQuery(graphene.AbstractType):
    find_user= graphene.Field(
        ProtectedUser,
        token= graphene.String(), 
        id= graphene.String())

    @query_jwt_required
    def resolve_find_user(self, info, **kwargs):
        user= mongo.db.users.find_one({ '_id': ObjectId(kwargs.get('id')) })

        if user is None:
            raise Exception('User not found')

        return User(user)