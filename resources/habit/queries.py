import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import re_structure_habit_output, UserHabits, HabitResponse, ProtectedUserHabits, ProtectedHabit

class GetUserHabits(graphene.AbstractType):
    get_user_habits= graphene.Field(ProtectedUserHabits)
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
