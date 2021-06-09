import graphene

from extensions import mongo
from .types import ActivityInput, ActivityCategoryInput, Activity, ActivityIcon, ActivityCategory

class ActivityQuery(graphene.AbstractType):
    activity= graphene.Field(Activity, _id= graphene.Int())
    activities= graphene.List(Activity, fields= graphene.Argument(ActivityInput))
    
    activity_icon= graphene.Field(ActivityIcon, _id= graphene.Int())
    activity_icon_by_name= graphene.Field(ActivityIcon, name= graphene.String())
    activity_icons= graphene.List(ActivityIcon, name= graphene.Argument(graphene.String))
    
    activity_categories= graphene.List(ActivityCategory, fields= graphene.Argument(ActivityCategoryInput))

    def resolve_activity(self, info, _id):
        activity= mongo.db.activities.find_one({ '_id': _id })

        return activity

    def resolve_activities(self, info, fields):
        if 'name' not in fields:
            fields['name']= ''

        if 'icon' not in fields:
            fields['icon']= ''

        activities= mongo.db.activities.find({
            'name': { 
                '$regex': fields['name'], 
                '$options': 'i' 
            },
            'icon': {
                '$regex': fields['icon'], 
                '$options': 'i'
            }
        }).sort('_id', -1)
        
        return activities
    
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

    def resolve_activity_categories(self, info, fields):
        if 'category' not in fields:
            fields['category']= ''

        in_array= { '$nin': [] }

        if 'activities' in fields:
            in_array= { '$in': fields['activities'] }

        activity_categories= mongo.db.activity_categories.find({
            'category': { 
                '$regex': fields['category'], 
                '$options': 'i' 
            },
            'activities': in_array
        }).sort('_id', -1)

        return activity_categories