import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import TimestampsInput, Timestamps, ResponseMessage
from ..activity.types import Activity

#Mood
class MoodEmoticonAbstract(graphene.AbstractType):
    name= graphene.String()
    value= graphene.Int()
    iconPath= graphene.String()
    color= graphene.String()

class MoodEmoticonInput(MoodEmoticonAbstract, graphene.InputObjectType):
    pass

class MoodEmoticon(MoodEmoticonAbstract, graphene.ObjectType):
    pass

class MoodParametersAbstract(graphene.AbstractType):
    internal= graphene.String()
    external= graphene.String()

class MoodParametersInput(MoodParametersAbstract, graphene.InputObjectType):
    pass

class MoodParameters(MoodParametersAbstract, graphene.ObjectType):
    pass

class MoodParametersFilterInput(graphene.InputObjectType):
    internal= graphene.Boolean()
    external= graphene.Boolean()

class MoodCreatedDateFilterInput(graphene.InputObjectType):
    start= graphene.String()
    end= graphene.String()

class MoodAbstract(graphene.AbstractType):
    activities= graphene.List(Activity)
    note= graphene.String()
    #img_paths= graphene.List(graphene.String)

class MoodInput(MoodAbstract, graphene.InputObjectType):
    emoticon= MoodEmoticonInput()
    created_at= TimestampsInput()
    parameters= MoodParametersInput()
    activities= graphene.List(graphene.Int)

class MoodFilterInput(graphene.InputObjectType):
    search_text= graphene.String()
    emoticon_name= graphene.String()
    parameters= MoodParametersFilterInput()
    activity_ids= graphene.List(graphene.Int)
    note= graphene.Boolean()
    created_date= MoodCreatedDateFilterInput()

class Mood(MoodAbstract, graphene.ObjectType): 
    _id= graphene.Int()
    emoticon= graphene.Field(MoodEmoticon)
    created_at= graphene.Field(Timestamps)
    parameters= graphene.Field(MoodParameters)

class UserMoods(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    moods= graphene.List(Mood)
    response= graphene.Field(ResponseMessage)

class MoodResponse(graphene.ObjectType):
    mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

#User moods charts
class MoodAverageByRangeDate(graphene.ObjectType):
    start_date= graphene.Int()
    end_date= graphene.Int()
    moods= graphene.List(Mood)
    average= graphene.Float()

class MoodAverageGroupByYear(graphene.ObjectType):
    year= graphene.Int()
    mood_average_by_range_date= graphene.List(MoodAverageByRangeDate)

class MoodsAverageGroupByMonth(graphene.ObjectType):
    group= graphene.String()
    mood_average_group_by_year= graphene.List(MoodAverageGroupByYear)

class UserMoodsChart(graphene.ObjectType):
    user_id= graphene.String()
    moods_chart= graphene.List(MoodsAverageGroupByMonth)

#Mood charts
class TotalMoodGroupByType(graphene.ObjectType):
    very_happy= graphene.Int()
    happy= graphene.Int()
    netral= graphene.Int()
    sad= graphene.Int()
    very_sad= graphene.Int()

class MoodsGrowthByYear(graphene.ObjectType):
    month_name= graphene.String()
    month_number= graphene.Int() 
    year= graphene.Int()
    mood_count= graphene.Int()
    mood_average= graphene.Int()

#Mood/Auth
class ProtectedUserMoods(graphene.Union):
    class Meta:
        types= (UserMoods, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedUserMoodsChart(graphene.Union):
    class Meta:
        types= (UserMoodsChart, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedMood(graphene.Union):
    class Meta:
        types= (MoodResponse, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

