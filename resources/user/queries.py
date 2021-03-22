import graphene
from flask_graphql_auth import query_jwt_required
from bson.objectid import ObjectId

from .types import UserInput, User, ProtectedUser
from ..utility_types import ResponseMessage
from extensions import mongo

class UserQuery(graphene.AbstractType):
    find_user= graphene.Field(
        ProtectedUser,
        token= graphene.String(), 
        id= graphene.String())
    all_user= graphene.List(ProtectedUser, fields= graphene.Argument(UserInput))

    @query_jwt_required
    def resolve_find_user(self, info, **kwargs):
        result= mongo.db.users.find_one({ '_id': ObjectId(kwargs.get('id')) })
        
        if result is None:
            return ResponseMessage(text= 'User not found', status= False)

        return User(result)

    def resolve_all_user(self, info, fields):
        documents= list(mongo.db.users.find(fields))

        def to_user_type(document):
            user= User(document)

            return user

        return list(map(to_user_type, documents))
