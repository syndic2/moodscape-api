import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId
import time

from .types import UserInput, User, ProtectedUser
from ..utility_types import ResponseMessage
from extensions import mongo

class UserQuery(graphene.AbstractType):
    all_user= graphene.List(ProtectedUser, fields= graphene.Argument(UserInput))
    user_profile= graphene.Field(ProtectedUser) 

    @query_header_jwt_required
    def resolve_user_profile(self, info):
        result= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })
        
        #if result is None:
        #    return ResponseMessage(text= 'Profil pengguna tidak ditemukan.', status= False)

        time.sleep(2)

        if 'img_url' not in result:
            result['img_url']= 'https://via.placeholder.com/100'

        return User(result)

    def resolve_all_user(self, info, fields):
        documents= list(mongo.db.users.find(fields))

        def to_user_type(document):
            user= User(document)

            return user

        return list(map(to_user_type, documents))
