from resources.utility_types import ResponseMessage
import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from .types import UserInput, User, UserResponse, ProtectedUser

class UserQuery(graphene.AbstractType):
    all_user= graphene.List(ProtectedUser, fields= graphene.Argument(UserInput))
    get_user_profile= graphene.Field(ProtectedUser) 

    def resolve_all_user(self, info, fields):
        users= mongo.db.users.find(fields)

        def to_user_type(document):
            user= User(document)

            return user

        return list(map(to_user_type, users))

    @query_header_jwt_required
    def resolve_get_user_profile(self, info):
        result= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })

        if result is None:
            return UserResponse(
                user= None,
                response= ResponseMessage(text= 'Profil pengguna tidak ditemukan', status= False)
            )

        if 'img_url' not in result:
            result['img_url']= 'https://via.placeholder.com/100'

        return UserResponse(
            user= result,
            response= ResponseMessage(text= 'Berhasil mengembalikan profil pengguna', status= True)
        )
