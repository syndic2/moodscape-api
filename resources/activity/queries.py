import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import (
    ActivityCategoryInput, 
    ActivityIcon, 
    UserActivities,
    ActivityResponse, 
    ActivityCategoryResponse, 
    ProtectedUserActivities,
    ProtectedActivity, 
    ProtectedActivityCategory
)

class GetActivityIcon(graphene.ObjectType):    
    get_activity_icons= graphene.List(ActivityIcon, name= graphene.Argument(graphene.String))
    get_activity_icon= graphene.Field(ActivityIcon, _id= graphene.Int())
    get_activity_icon_by_name= graphene.Field(ActivityIcon, name= graphene.String())

    def resolve_get_activity_icon(self, info, _id):
        activity_icon= mongo.db.activity_icons.find_one({ '_id': _id })

        return activity_icon

    def resolve_get_activity_icon_by_name(self, info, name):
        activity_icon= mongo.db.activity_icons.find_one({ 'name': name })

        return activity_icon

    def resolve_get_activity_icons(self, info, name):
        activity_icons= mongo.db.activity_icons.find({
            'name': {
                '$regex': name, 
                '$options': 'i' 
            }
        }).sort('_id', -1)

        return activity_icons

class GetUserActivities(graphene.ObjectType):
    get_activity_categories= graphene.Field(ProtectedUserActivities, fields= graphene.Argument(ActivityCategoryInput))
    get_activity_category= graphene.Field(ProtectedActivityCategory, _id= graphene.Int())
    get_activity= graphene.Field(ProtectedActivity, _id= graphene.Int(), activity_category_id= graphene.Int())
    
    @query_header_jwt_required  
    def resolve_get_activity_categories(self, info, fields):
        filter_conditions= {}

        if 'category' in fields:
            filter_conditions['$eq']= ['$$item.category', None]
        else:
            filter_conditions['$ne']= ['$$item.category', None]

        result= mongo.db.user_activities.aggregate([
            { 
                '$match': {  'user_id': ObjectId(get_jwt_identity()) } 
            },
            {
                '$project': {
                    '_id': 1,
                    'user_id': 1,
                    'activity_categories': {
                        '$filter': {
                            'input': '$activity_categories',
                            'as': 'item',
                            'cond': filter_conditions
                        }
                    }
                }
            }
        ])
        result= list(result)

        if not result:
            return UserActivities(
                activity_categories= [], 
                response= ResponseMessage(text= 'Belum memiliki aktivitas yang tersimpan', status= True)
            )

        return UserActivities(
            _id= result[0]['_id'],
            user_id= ObjectId(get_jwt_identity()), 
            activity_categories= result[0]['activity_categories'],
            response= ResponseMessage(text= 'Berhasil mengembalikan aktivitas pengguna', status= True) 
        )
    
    @query_header_jwt_required
    def resolve_get_activity_category(self, info, _id):
        result= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                'activity_categories': {
                    '$elemMatch': {
                        '_id': _id
                    }
                }
            }
        )

        if 'activity_categories' not in result:
            return ActivityCategoryResponse(
                activity_category= None,
                response= ResponseMessage(text= 'Kategori aktivitas tidak ditemukan', status= False)
            )

        return ActivityCategoryResponse(
            activity_category= result['activity_categories'][0],
            response= ResponseMessage(text= 'Berhasil mengembalikan kategori aktivitas', status= True)
        )
    
    @query_header_jwt_required
    def resolve_get_activity(self, info, **kwargs):
        _id= kwargs.get('_id')
        activity_category_id= kwargs.get('activity_category_id')
        filter_conditions= {
            '$elemMatch': {
                'activities': {
                    '$elemMatch': {
                        '_id': _id
                    }
                }
            },
            'in': {
                'activities': { 
                    '$filter': {
                        'input': '$$item1.activities',
                        'as': 'item2',
                        'cond': {
                            '$eq': ['$$item2._id', _id]
                        }
                    }
                }
            },
            'cond': {}
        }

        if activity_category_id == 0:
            filter_conditions['$elemMatch']['category']= None
            filter_conditions['in']['category']= '$$item1.category'
            filter_conditions['cond']['$eq']= ['$$item1.category', None]
        else:
            filter_conditions['$elemMatch']['_id']= activity_category_id
            filter_conditions['in']['_id']= '$$item1._id'
            filter_conditions['cond']['$eq']= ['$$item1._id', activity_category_id]

            is_category_id_exist= mongo.db.user_activities.find_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                { 
                    'activity_categories': {
                        '$elemMatch': {
                            '_id': activity_category_id
                        }
                    }
                }
            )

            if 'activity_categories' not in is_category_id_exist:
                return ActivityResponse(
                    activity= None,
                    response= ResponseMessage(text= 'Id kategori aktivitas tidak ditemukan', status= False)                
            )

        result= mongo.db.user_activities.aggregate([
            {
                '$match': {
                    'user_id': ObjectId(get_jwt_identity()),
                    'activity_categories': {
                        '$elemMatch': filter_conditions['$elemMatch']
                    }
                }
            },
            {
                '$addFields': {
                    'activity_categories': {
                        '$filter': {
                            'input': {
                                '$map': {
                                    'input': '$activity_categories',
                                    'as': 'item1',
                                    'in': filter_conditions['in']
                                }
                            },
                            'as': 'item1', 
                            'cond': filter_conditions['cond']
                        }
                    }
                }
            },
            {
                '$project': {
                    'activity_categories.activities': 1
                }
            }
        ])

        result= list(result)

        if not result:
            return ActivityResponse(
                activity= None,
                response= ResponseMessage(text= 'Aktivitas tidak ditemukan', status= False)                
            )
        
        result= result[0]['activity_categories'][0]['activities'][0]

        return ActivityResponse(
            activity= result,
            response= ResponseMessage(text= 'Berhasil mengembalikan aktivitas', status= True)
        )
    
class ActivityQuery(GetActivityIcon, GetUserActivities, graphene.AbstractType):
    pass