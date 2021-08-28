import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import MoodFilterInput, MoodResponse, UserMoods, ProtectedUserMoods, ProtectedMood

class GetUserMoods(graphene.AbstractType):
    get_user_moods= graphene.Field(ProtectedUserMoods)
    get_user_mood= graphene.Field(ProtectedMood, _id= graphene.Int())
    get_filtered_user_mood= graphene.Field(ProtectedUserMoods, filters= graphene.Argument(MoodFilterInput))

    @query_header_jwt_required
    def resolve_get_user_moods(self, info):
        user_moods= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_moods is None or not user_moods['moods']:
            return UserMoods(
                moods= [],
                response= ResponseMessage(text= 'Belum memiliki mood yang tersimpan', status= False) 
            )

        moods= list(mongo.db.moods.find({ '_id': { '$in': user_moods['moods'] } }).sort('created_at', -1))

        for mood in moods:
            mood['created_at']= {
                'date': mood['created_at'].date(),
                'time': str(mood['created_at'].time())[:-3]
            }

        return UserMoods(
            _id= user_moods['_id'],
            user_id=  user_moods['user_id'],
            moods= moods,
            response= ResponseMessage(text= 'Berhasil mengembalikan mood pengguna', status= True)
        )

    @query_header_jwt_required
    def resolve_get_user_mood(self, info, _id):
        is_mood_id_exist= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()), 'moods': _id })

        if is_mood_id_exist is None:
            return MoodResponse(
                mood= None,
                response= ResponseMessage(text= 'Mood tidak ditemukan', status= False)
            )

        result= mongo.db.moods.find_one({ '_id': _id })

        if result is None:
            return MoodResponse(
                mood= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, mood tidak ditemukan', status= False)
            )

        result['created_at']= {
            'date': result['created_at'].date(),
            'time': str(result['created_at'].time())[:-3]
        }

        return MoodResponse(
            mood= result,
            response= ResponseMessage(text= 'Berhasil mengembalikan mood', status= True)
        )

    @query_header_jwt_required
    def resolve_get_filtered_user_mood(self, info, filters):
        filter_conditions= []

        if filters.emoticon_name != '':
            filter_conditions.append({ 'emoticon.name': filters.emoticon_name });
        if filters.parameters.internal is True:
            filter_conditions.append({ 'parameters.internal': { '$regex': filters.search_text, '$options': 'i' } })
        if filters.parameters.external is True:
            filter_conditions.append({ 'parameters.external': { '$regex': filters.search_text, '$options': 'i' } })
        if not filters.activity_ids is False:
            filter_conditions.append({ 'activities._id': { '$all': filters.activity_ids } })
        if filters.note is True:
            filter_conditions.append({ 'note': { '$regex': filters.search_text, '$options': 'i' } })

        user_moods= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_moods is None or not user_moods['moods']:
            return UserMoods(
                moods= [],
                response= ResponseMessage(text= 'Belum memiliki mood yang tersimpan', status= False)
            ) 

        moods= list(mongo.db.moods.find({  '_id': { '$in': user_moods['moods'] }, '$or': filter_conditions }).sort('created_at', -1))

        for mood in moods:
            mood['created_at']= {
                'date': mood['created_at'].date(),
                'time': str(mood['created_at'].time())[:-3]
            }

        return UserMoods(
            _id= user_moods['_id'],
            user_id=  ObjectId(get_jwt_identity()),
            moods= list(moods),
            response= ResponseMessage(text= 'Berhasil mengembalikan hasil pencarian mood pengguna', status= True)
        ) 

class MoodQuery(GetUserMoods, graphene.AbstractType):
    pass