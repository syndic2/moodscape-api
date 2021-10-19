import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import get_month_name
from ..utility_types import ResponseMessage
from .types import re_structure_habit_output, UserHabits, UserHabitsChart, HabitResponse, ProtectedUserHabits, ProtectedUserHabitsChart, ProtectedHabit

class GetUserHabits(graphene.AbstractType):
    get_user_habits= graphene.Field(ProtectedUserHabits)
    get_user_habits_chart= graphene.Field(ProtectedUserHabitsChart)
    get_user_habit= graphene.Field(ProtectedHabit, _id= graphene.Int())
    get_filtered_user_habits= graphene.Field(ProtectedUserHabits)

    @query_header_jwt_required
    def resolve_get_user_habits(self, info):
        user_habit= mongo.db.user_habits.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_habit is None or 'habits' not in user_habit:
            return UserHabits(
                habits= [],
                response= ResponseMessage(text= 'Belum memiliki habit yang tersimpan', status= False)
            )

        #filters_query= { '_id': { '$in': user_habit['habits'] } }
#
        #if day != '':
        #    filters_query['day']= day

        habits= list(mongo.db.habits.find({ '_id': { '$in': user_habit['habits'] } }))

        for habit in habits:
            habit_track= mongo.db.habit_tracks.find_one({ 'habit_id': habit['_id'] })
            habit= re_structure_habit_output(habit, habit_track)

        return UserHabits(
            _id= user_habit['_id'],
            user_id= user_habit['user_id'],
            habits= habits,
            response= ResponseMessage(text= 'Berhasil mengembalikan habit pengguna', status= True)
        )

    @query_header_jwt_required
    def resolve_get_user_habits_chart(self, info):
        user_habits= mongo.db.user_habits.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_habits is None or not user_habits['habits']:
            return UserHabitsChart(
                user_id= None,
                habits_chart= []
            )

        habits= list(mongo.db.habits.find({ '_id': { '$in': user_habits['habits'] }}))
        habit_tracks= list(mongo.db.habit_tracks.find({ 'habit_id': { '$in': user_habits['habits'] } }))        
        habits_chart= []

        #merge habit tracks
        for habit in habits:
            for track in habit_tracks:
                if habit['_id'] == track['habit_id']:
                    habit['track']= track

        #create month group
        for month in range(12):
            habits_chart.append({
                'group': get_month_name(month),
                'habit_average_group_by_year': []
            })
        
        #create year group
        for habit in habits:
            started_at= habit['goal_dates']['start'].date()

            #distinct year
            is_year_exist_in_group= [year_group for year_group in habits_chart[started_at.month-1]['habit_average_group_by_year'] if year_group['year'] == started_at.year]

            if len(is_year_exist_in_group) == 0:
                habits_chart[started_at.month-1]['habit_average_group_by_year'].append({
                    'year': started_at.year,
                    'habits': [],
                    'average': 0
                })

        for habit in habits:
            started_at= habit['goal_dates']['start'].date()

            for year_group in habits_chart[started_at.month-1]['habit_average_group_by_year']:
                if year_group['year'] == started_at.year:
                    habit_temp= habit.copy()
                    habit_temp['goal_dates']= {
                        'start': habit['goal_dates']['start'].date(),
                        'end': habit['goal_dates']['end'].date()
                    }
                    year_group['habits'].append(habit)

                    if habit['track']['total_completed'] > 0: year_group['average']+= 1

        #caluclate average percentage
        for month_group in habits_chart:
            for year_group in month_group['habit_average_group_by_year']:
                if year_group['average'] > 0: year_group['average']/= len(year_group['habits'])*100

        return UserHabitsChart(
            user_id= user_habits['user_id'],
            habits_chart= habits_chart
        )

    @query_header_jwt_required
    def resolve_get_user_habit(self, info, _id):
        is_habit_id_exist= mongo.db.user_habits.find_one({ 'user_id': ObjectId(get_jwt_identity()), 'habits': _id })

        if is_habit_id_exist is None:
            return HabitResponse(
                habit= None,
                response= ResponseMessage(text= 'Habit tidak ditemukan', status= False)
            ) 

        result= mongo.db.habits.find_one({ '_id': _id })

        if result is None:
            return HabitResponse(
                habit= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, habit tidak ditemukan', status= False)
            )

        habit_track= mongo.db.habit_tracks.find_one({ 'habit_id': _id })

        return HabitResponse(
            habit= re_structure_habit_output(result, habit_track),
            response= ResponseMessage(text= 'Berhasil mengembalikan habit', status= True)
        )

    def resolve_get_filtered_user_habits(self, info):
        return UserHabits(
            _id= 0,
            user_id= '',
            habits= [],
            response= ResponseMessage(text= 'Berhasil mengembalikan hasil pencarian habit pengguna', status= True)
        )

class HabitQuery(GetUserHabits, graphene.AbstractType):
    pass
