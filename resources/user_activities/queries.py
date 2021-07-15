import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required

from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import UserActivities, ProtectedUserActivities

class UserActivitiesQuery(graphene.AbstractType):
    user_activities= graphene.Field(ProtectedUserActivities)

    @query_header_jwt_required
    def resolve_user_activities(self, info):
        user_activities= mongo.db.user_activities.find_one({ 'user_id': ObjectId(get_jwt_identity()) })
        
        if user_activities is None:
            return UserActivities(activities= [], response= ResponseMessage(text= 'Belum memiliki aktivitas yang tersimpan', status= False))
        
        #JOIN
        results= mongo.db.activity_categories.aggregate([
            {
                '$lookup': {
                    'from': 'activities',
                    'localField': 'activities',
                    'foreignField': '_id',
                    'as': 'activities'
                }
            }
        ])
        
        return UserActivities(
            _id= user_activities['_id'], 
            #user_id= ObjectId('60acfde1ea67a0786c51fc0c'),
            user_id= ObjectId(get_jwt_identity()), 
            activity_categories= results,
            response= ResponseMessage(text= 'Berhasil mengembalikan aktivitas pengguna', status= True) 
        )