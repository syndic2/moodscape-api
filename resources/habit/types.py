import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

class HabitAbstract(graphene.AbstractType):
    name= graphene.String()
    description= graphene.String()
    goal= graphene.Int()
    streaks_goal= graphene.String()
    reminder_at= graphene.String()
    repeat_reminder= graphene.String()

class HabitInput(graphene.InputObjectType, HabitAbstract):
    pass

class Habit(graphene.ObjectType,  HabitAbstract):
    _id= graphene.Int()
    created_at= graphene.String()

class UserHabits(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    habits= graphene.List(Habit)
    response= graphene.Field(ResponseMessage)

class ProtectedUserHabits(graphene.Union):
    class Meta:
        types= (UserHabits, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedUserHabit(graphene.Union):
    class Meta:
        types= (Habit, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)



