import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage
from ..mood.types import Mood

class UserMoods(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    moods= graphene.List(Mood)
    response= graphene.Field(ResponseMessage)

class ProtectedUserMoods(graphene.Union):
    class Meta:
        types= (UserMoods, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedUserMood(graphene.Union):
    class Meta:
        types= (Mood, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)






    