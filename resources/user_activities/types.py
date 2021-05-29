import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage
from ..activity.types import ActivityCategory

class UserActivities(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    activity_categories= graphene.List(ActivityCategory)
    response= graphene.Field(ResponseMessage)

class ProtectedUserActivities(graphene.Union):
    class Meta:
        types= (UserActivities, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)