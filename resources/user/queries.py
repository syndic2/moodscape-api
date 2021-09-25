import os, graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import upload_path
from resources.utility_types import ResponseMessage
from .types import User, UserResponse, ProtectedUser

class UserQuery(graphene.AbstractType):
    get_users= graphene.List(User)
    get_user= graphene.Field(User, _id= graphene.String())
    get_user_profile= graphene.Field(ProtectedUser) 

    def resolve_get_users(self, info):
        users= list(mongo.db.users.find({}))

        for user in users:
            user['date_of_birth']= user['date_of_birth'].date()
            user['joined_at']= user['joined_at'].date()
            
            img_name= user['img_url'].split('/')[-1]
            if user['img_url'] != 'https://via.placeholder.com/100' and os.path.isfile(os.path.join(f"{upload_path}/images", img_name)) is False:
                result= mongo.db.users.find_one_and_update(
                    { '_id': ObjectId(user['_id']) },
                    { '$set': { 'img_url': 'https://via.placeholder.com/100' } }
                )

                if result is None:
                    return []

        return users    

    def resolve_get_user(self, info, _id):
      user= mongo.db.users.find_one({ '_id': ObjectId(_id) })

      return user

    @query_header_jwt_required
    def resolve_get_user_profile(self, info):
        result= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })

        if result is None:
            return UserResponse(
                user= None,
                response= ResponseMessage(text= 'Profil pengguna tidak ditemukan', status= False)
            )

        result['date_of_birth']= result['date_of_birth'].date()
        result['joined_at']= result['joined_at'].date()

        return UserResponse(
            user= result,
            response= ResponseMessage(text= 'Berhasil mengembalikan profil pengguna', status= True)
        )
