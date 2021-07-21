import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import TimestampsInput, Timestamps, ResponseMessage

#Mood
class MoodEmoticon(graphene.ObjectType):
    name= graphene.String()
    value= graphene.Int()

class MoodParametersAbstract(graphene.AbstractType):
    internal= graphene.String()
    external= graphene.String()

class MoodParametersInput(MoodParametersAbstract, graphene.InputObjectType):
    pass

class MoodParameters(MoodParametersAbstract, graphene.ObjectType):
    pass

class MoodAbstract(graphene.AbstractType):
    activity_ids= graphene.List(graphene.Int)
    note= graphene.String()
    img_paths= graphene.List(graphene.String)

class MoodInput(MoodAbstract, graphene.InputObjectType):
    timestamps= TimestampsInput()
    parameters= MoodParametersInput()

class Mood(MoodAbstract, graphene.ObjectType): 
    _id= graphene.Int()
    emoticon= graphene.Field(MoodEmoticon)
    timestamps= graphene.Field(Timestamps)
    parameters= graphene.Field(MoodParameters)

#User - Moods
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

class ProtectedMood(graphene.Union):
    class Meta:
        types= (Mood, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)