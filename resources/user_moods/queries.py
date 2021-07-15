from typing import Text
import graphene
from flask_graphql_auth import fields, get_jwt_identity, query_header_jwt_required

from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from ..mood.types import MoodInput
from ..user_moods.types import UserMoods, ProtectedUserMoods

class UserMoodsQuery(graphene.AbstractType):
    user_moods= graphene.Field(UserMoods, fields= graphene.Argument(MoodInput))

    def resolve_user_moods(self, info, fields):
        user_moods= mongo.db.user_moods.find_one({ 'user_id': ObjectId('60acfde1ea67a0786c51fc0c') })

        if user_moods is None:
            return UserMoods(moods= [], response= ResponseMessage(text= 'Belum memiliki mood yang tersimpan', status= False))

        return UserMoods(
            _id= 0,
            user_id=  ObjectId('60acfde1ea67a0786c51fc0c'),
            moods= [],
            response= ResponseMessage(text= 'Berhasil mengembalikan mood pengguna', status= True)
        )
