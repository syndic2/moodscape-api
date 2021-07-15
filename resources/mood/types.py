import graphene

from ..utility_types import TimestampsInput, Timestamps

class MoodParametersAbstract(graphene.AbstractType):
    internal= graphene.String()
    external= graphene.String()

class MoodParametersInput(MoodParametersAbstract, graphene.InputObjectType):
    pass

class MoodParameters(MoodParametersAbstract, graphene.ObjectType):
    pass

class MoodAbstract(graphene.AbstractType):
    mood= graphene.String()
    activity_ids= graphene.List(graphene.Int)
    note= graphene.String()
    img_paths= graphene.List(graphene.String)

class MoodInput(MoodAbstract, graphene.InputObjectType):
    timestamps= TimestampsInput()
    parameters= MoodParametersInput()

class Mood(MoodAbstract, graphene.ObjectType): 
    _id= graphene.Int()
    timestamps= graphene.Field(Timestamps)
    parameters= graphene.Field(MoodParameters)