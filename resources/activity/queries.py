import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import ActivityIcon, UserActivities, ProtectedUserActivities

class GetActivityIcon(graphene.ObjectType):    
    activity_icon= graphene.Field(ActivityIcon, _id= graphene.Int())
    activity_icon_by_name= graphene.Field(ActivityIcon, name= graphene.String())
    activity_icons= graphene.List(ActivityIcon, name= graphene.Argument(graphene.String))
        
    def resolve_activity_icon(self, info, _id):
        activity_icon= mongo.db.activity_icons.find_one({ '_id': _id })

        return activity_icon

    def resolve_activity_icon_by_name(self, info, name):
        activity_icon= mongo.db.activity_icons.find_one({ 'name': name })

        return activity_icon

    def resolve_activity_icons(self, info, name):
        activity_icons= mongo.db.activity_icons.find({
            'name': {
                '$regex': name, 
                '$options': 'i' 
            }
        }).sort('_id', -1)

        return activity_icons

class GetUserActivities(graphene.ObjectType):
    user_activities= graphene.Field(ProtectedUserActivities)

    @query_header_jwt_required
    def resolve_user_activities(self, info):
        user_activities= mongo.db.user_activities.find_one({ 'user_id': ObjectId(get_jwt_identity()) })
        
        if user_activities is None or not user_activities['activity_categories']:
            return GetUserActivities(activity_categories= user_activities['activity_categories'], response= ResponseMessage(text= 'Belum memiliki aktivitas yang tersimpan', status= False))

        #JOIN
        #results= mongo.db.activity_categories.aggregate([
        #    {
        #        '$lookup': {
        #            'from': 'activities',
        #            'localField': 'activities',
        #            'foreignField': '_id',
        #            'as': 'activities'
        #        }
        #    }
        #])
            
        return UserActivities(
            _id= user_activities['_id'],
            user_id= ObjectId(get_jwt_identity()), 
            activity_categories= user_activities['activity_categories'],
            response= ResponseMessage(text= 'Berhasil mengembalikan aktivitas pengguna', status= True) 
        )

class ActivityQuery(GetActivityIcon, GetUserActivities, graphene.AbstractType):
    pass