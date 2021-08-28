import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

#Activity
class ActivityIcon(graphene.ObjectType):
    _id= graphene.Int()
    name= graphene.String()

class ActivityAbstract(graphene.AbstractType):
    name= graphene.String()
    icon= graphene.String()

class ActivityInput(ActivityAbstract, graphene.InputObjectType):
    pass

class Activity(ActivityAbstract, graphene.ObjectType):
    _id= graphene.Int()

class ActivityCategoryAbstract(graphene.AbstractType):
    category= graphene.String()

class ActivityCategoryInput(ActivityCategoryAbstract, graphene.InputObjectType):
    activities= graphene.List(graphene.Int)

class ActivityCategory(ActivityCategoryAbstract, graphene.ObjectType):
    _id= graphene.Int()
    activities= graphene.List(Activity)

class UserActivities(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    activity_categories= graphene.List(ActivityCategory)
    response= graphene.Field(ResponseMessage)

class ActivityResponse(graphene.ObjectType):
    activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage)

class ActivityCategoryResponse(graphene.ObjectType):
    activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)

#Activity/Auth
class ProtectedUserActivities(graphene.Union):
    class Meta:
        types= (UserActivities, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedActivity(graphene.Union):
    class Meta:
        types= (ActivityResponse, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedActivityCategory(graphene.Union):
    class Meta:
        types= (ActivityCategoryResponse, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

