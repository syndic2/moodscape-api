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
        'is_reminder': fields['is_reminder'],
        'is_notified': False,
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
        fields['track']= {
            'total_completed': track_fields['total_completed'],
            'total_streaks': track_fields['total_streaks'],
            'streak_logs': track_fields['streak_logs']
        }

        for i in range(len(fields['track']['streak_logs'])):
            fields['track']['streak_logs'][i]['start_date']= fields['track']['streak_logs'][i]['start_date'].date()
            fields['track']['streak_logs'][i]['end_date']= fields['track']['streak_logs'][i]['end_date'].date()
            
            if fields['track']['streak_logs'][i]['last_marked_at'] is not None:
                fields['track']['streak_logs'][i]['last_marked_at']= fields['track']['streak_logs'][i]['last_marked_at'].date()

            for j in range(len(fields['track']['streak_logs'][i]['marked_at'])):
                fields['track']['streak_logs'][i]['marked_at'][j]= fields['track']['streak_logs'][i]['marked_at'][j].date()

    return fields

#Habit
class HabitGoalDatesAbstract(graphene.AbstractType):
    start= graphene.String()
    end= graphene.String()

class HabitGoalDates(HabitGoalDatesAbstract, graphene.ObjectType):
    pass

class HabitGoalDatesInput(HabitGoalDatesAbstract, graphene.InputObjectType):
    pass

class HabitStreakLog(graphene.ObjectType):
    start_date= graphene.String()
    end_date= graphene.String()
    current_goal= graphene.Int()
    target_goal= graphene.Int()
    last_marked_at= graphene.String()
    is_complete= graphene.Boolean()
    marked_at= graphene.List(graphene.String)

class HabitTrack(graphene.ObjectType):
    total_completed= graphene.Int()
    total_streaks= graphene.Int()
    streak_logs= graphene.List(HabitStreakLog)

class HabitAbstract(graphene.AbstractType):
    name= graphene.String()
    description= graphene.String()
    type= graphene.String()
    day= graphene.String()
    goal= graphene.Int()
    reminder_time= graphene.String()
    is_reminder= graphene.Boolean()
    label_color= graphene.String()

class HabitInput(HabitAbstract, graphene.InputObjectType):
    goal_dates= HabitGoalDatesInput()

class Habit(HabitAbstract, graphene.ObjectType):
    _id= graphene.Int()
    created_at= graphene.Field(Timestamps)
    goal_dates= graphene.Field(HabitGoalDates)
    track= graphene.Field(HabitTrack)

class UserHabits(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    habits= graphene.List(Habit)
    response= graphene.Field(ResponseMessage)

class HabitResponse(graphene.ObjectType):
    habit= graphene.Field(Habit)
    response= graphene.Field(ResponseMessage)

#User habits chart
class HabitAverageGroupByYear(graphene.ObjectType):
    year= graphene.Int()
    habits= graphene.List(Habit)
    average= graphene.Int()

class HabitAverageGroupByMonth(graphene.ObjectType):
    group= graphene.String()
    habit_average_group_by_year= graphene.List(HabitAverageGroupByYear)

class UserHabitsChart(graphene.ObjectType):
    user_id= graphene.String()
    habits_chart= graphene.List(HabitAverageGroupByMonth)

#Habit/Auth
class ProtectedUserHabits(graphene.Union):
    class Meta:
        types= (UserHabits, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedUserHabitsChart(graphene.Union):
    class Meta:
        types= (UserHabitsChart, AuthInfoField)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedHabit(graphene.Union):
    class Meta:
        types= (HabitResponse, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)



