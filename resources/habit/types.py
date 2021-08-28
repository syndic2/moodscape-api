import datetime, graphene
from flask_graphql_auth import AuthInfoField

from utilities.helpers import datetime_format, get_sequence
from ..utility_types import Timestamps, ResponseMessage

def re_structure_habit_input(fields, operation= 'create'):
    if fields.reminder_time != '':
        fields['reminder_time']= datetime.datetime.strptime(fields.reminder_time, datetime_format('time'))
    
    structured= {
        '_id': get_sequence('habits'),
        'name': fields['name'],
        'description': fields['description'],
        'created_at': '',
        'type': fields['type'],
        'day': fields['day'],
        'goal': fields['goal'],
        'goal_dates': {
            'start': datetime.datetime.strptime(fields.goal_dates.start, datetime_format('date')),
            'end': datetime.datetime.strptime(fields.goal_dates.end, datetime_format('date'))
        },
        'reminder_time': fields['reminder_time'],
        'label_color': fields['label_color']
    }

    if operation == 'create':
        current_datetime= datetime.datetime.now()
        current_date= current_datetime.strftime(datetime_format('date'))
        current_time= current_datetime.strftime(datetime_format('time'))
        structured['created_at']= datetime.datetime.strptime(f"{current_date} {current_time}", datetime_format('datetime'))
    elif operation == 'update':
        del structured['_id']
        del structured['created_at']
    
    return structured

def re_structure_habit_output(fields, track_fields= None):
    fields['created_at']= {
        'date': fields['created_at'].date(),
        'time': str(fields['created_at'].time())[:-3]
    }
    fields['goal_dates']= {
        'start': fields['goal_dates']['start'].date(),
        'end': fields['goal_dates']['end'].date()
    }

    if fields['reminder_time'] != '':
        fields['reminder_time']= str(fields['reminder_time'].time())[:-3]
    
    if track_fields is not None:
        fields['track_details']= {
            'current_goal': track_fields['current_goal'],
            #'days_left': track_fields['days_left'],
            'streaks': track_fields['streaks'],
            'last_marked_at': track_fields['last_marked_at'].date()
        }

    return fields

#Habit
class HabitGoalDatesAbstract(graphene.AbstractType):
    start= graphene.String()
    end= graphene.String()

class HabitGoalDates(HabitGoalDatesAbstract, graphene.ObjectType):
    pass

class HabitGoalDatesInput(HabitGoalDatesAbstract, graphene.InputObjectType):
    pass

class HabitTrackDetail(graphene.ObjectType):
    current_goal= graphene.Int()
    #days_left= graphene.Int()
    streaks= graphene.Int()
    last_marked_at= graphene.String()

class HabitAbstract(graphene.AbstractType):
    name= graphene.String()
    description= graphene.String()
    type= graphene.String()
    day= graphene.String()
    goal= graphene.Int()
    reminder_time= graphene.String()
    label_color= graphene.String()

class HabitInput(HabitAbstract, graphene.InputObjectType):
    goal_dates= HabitGoalDatesInput()

class Habit(HabitAbstract, graphene.ObjectType):
    _id= graphene.Int()
    created_at= graphene.Field(Timestamps)
    goal_dates= graphene.Field(HabitGoalDates)
    track_details= graphene.Field(HabitTrackDetail)

class UserHabits(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    habits= graphene.List(Habit)
    response= graphene.Field(ResponseMessage)

class HabitResponse(graphene.ObjectType):
    habit= graphene.Field(Habit)
    response= graphene.Field(ResponseMessage)

#Habit/Auth
class ProtectedUserHabits(graphene.Union):
    class Meta:
        types= (UserHabits, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedHabit(graphene.Union):
    class Meta:
        types= (HabitResponse, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)



