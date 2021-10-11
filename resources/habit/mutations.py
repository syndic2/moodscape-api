import datetime, graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import datetime_format, validate_datetime, lesser_comparison_datetime, get_sequence
from ..utility_types import ResponseMessage
from .types import re_structure_habit_input, re_structure_habit_output, HabitInput, Habit

class CreateHabit(graphene.Mutation):
    class Arguments:
        fields= HabitInput()
    
    created_habit= graphene.Field(Habit)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, fields):
        #start validation check        
        if validate_datetime(fields.goal_dates.start, 'date') is False:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Format tanggal dimulai tidak sesuai, habit gagal diperbarui', status= False)
            )

        if validate_datetime(fields.goal_dates.end, 'date') is False:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Format tanggal selesai tidak sesuai, habit gagal diperbarui', status= False)
            )

        if lesser_comparison_datetime(fields.goal_dates.start, fields.goal_dates.end, 'date') is False:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Tanggal dimulai dan tanggal selesai tidak sesuai, habit gagal diperbarui', status= False)
            )

        if fields.reminder_time != '' and validate_datetime(fields.reminder_time, 'time') is False:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Format waktu pengingat tidak sesuai, habit gagal diperbarui', status= False)
            )
        #end validation check

        #start create habit and user habits
        insert_on_habits= mongo.db.habits.insert_one(dict(re_structure_habit_input(fields)))

        if insert_on_habits.inserted_id is None:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Tidak dapat menyimpan pada habits collection, habit gagal ditambahkan', status= False)
            )

        is_user_habits_exist= mongo.db.user_habits.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        #check if user habits exist or not
        if is_user_habits_exist is None:
            create_user_habits= mongo.db.user_habits.insert_one({
                '_id': get_sequence('user_habits'),
                'user_id': ObjectId(get_jwt_identity()),
                'habits': [insert_on_habits.inserted_id]
            })

            if create_user_habits.inserted_id is None:
                return CreateHabit(
                    created_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat membuat user_habits baru, habit gagal ditambahkan', status= False)
                )
        else:
            insert_on_user_habits= mongo.db.user_habits.update_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                { 
                    '$push': {
                        'habits': insert_on_habits.inserted_id
                    }
                }
            )

            if insert_on_user_habits.modified_count == 0:
                return CreateHabit(
                    created_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat menyimpan pada user_habits collection, habit gagal ditambahkan', status= False)
                )
        
        created_habit= mongo.db.habits.find_one({ '_id': insert_on_habits.inserted_id })
        #end create habit and user habits

        #start create habit track
        result= mongo.db.habit_tracks.insert_one({
            'habit_id': insert_on_habits.inserted_id,
            'total_completed': 0,
            'total_streaks': 0,
            'streak_logs': [
                {
                    'start_date': datetime.datetime.strptime(fields.goal_dates.start, datetime_format('date')),
                    'end_date': datetime.datetime.strptime(fields.goal_dates.end, datetime_format('date')),
                    'current_goal': 0,
                    'target_goal': created_habit['goal'],
                    'last_marked_at': None,
                    'is_complete': False,
                    'marked_at': []
                }
            ]
        })

        if result.inserted_id is None:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Tidak dapat membuat habit track baru, habit gagal ditambahkan', status= False)
            )
        
        created_habit_track= mongo.db.habit_tracks.find_one({ 'habit_id': insert_on_habits.inserted_id })
        #end create habit streak logs

        return CreateHabit(
            created_habit= re_structure_habit_output(created_habit, created_habit_track),
            response= ResponseMessage(text= 'Berhasil menambahkan habit baru', status= True)
        )

class UpdateHabit(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        fields= HabitInput()
    
    updated_habit= graphene.Field(Habit)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, _id, fields):
        #start validation check
        if validate_datetime(fields.goal_dates.start, 'date') is False:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Format tanggal dimulai tidak sesuai, habit gagal diperbarui', status= False)
            )

        if validate_datetime(fields.goal_dates.end, 'date') is False:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Format tanggal selesai tidak sesuai, habit gagal diperbarui', status= False)
            )

        if lesser_comparison_datetime(fields.goal_dates.start, fields.goal_dates.end, 'date') is False:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Tanggal dimulai dan tanggal selesai tidak sesuai, habit gagal diperbarui', status= False)
            )

        if fields.reminder_time != '' and validate_datetime(fields.reminder_time, 'time') is False:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Format waktu pengingat tidak sesuai, habit gagal diperbarui', status= False)
            )

        is_habit_id_exist_in_user_habits= mongo.db.user_habits.find_one({ 
            'user_id': ObjectId(get_jwt_identity()),
            'habits': _id
        })

        if is_habit_id_exist_in_user_habits is None:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Habit tidak ditemukan pada user_habits collection, habit gagal diperbarui', status= False)
            )

        is_habit_id_exist_in_habits= mongo.db.habits.find_one({ '_id': _id })

        if is_habit_id_exist_in_habits is None:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Habit tidak ditemukan pada habits collection, habit gagal diperbarui', status= False)
            )
        #end validation check

        #start update habit
        result= mongo.db.habits.find_one_and_update(
            { '_id': _id },
            { '$set': dict(re_structure_habit_input(fields, 'update')) }    
        )

        if result is None:
            return UpdateHabit(
                updated_habit= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, habit gagal diperbarui', status= False)
            )
        
        updated_habit= mongo.db.habits.find_one({ '_id': _id })
        #end update habit

        #start update on habit streak logs
        is_streak_log_exist= mongo.db.habit_tracks.find_one(
            { 
                'habit_id': _id,
                'streak_logs': {
                    '$elemMatch': {
                        'start_date': datetime.datetime.strptime(fields.goal_dates.start, datetime_format('date')),
                        #'end_date': datetime.datetime.strptime(fields.goal_dates.end, datetime_format('date'))
                    }
                }
            }
        )

        #check if streak log exist in array streak_logs
        if is_streak_log_exist is None:
            result= mongo.db.habit_tracks.update_one(
                { 'habit_id': _id },
                {
                    '$push': {
                        'streak_logs': {
                            'start_date': datetime.datetime.strptime(fields.goal_dates.start, datetime_format('date')),
                            'end_date': datetime.datetime.strptime(fields.goal_dates.end, datetime_format('date')),
                            'current_goal': 0,
                            'target_goal': fields['goal'],
                            'last_marked_at': None,
                            'is_complete': False,
                            'marked_at': []
                        }
                    }
                }
            )

            if result.modified_count == 0:
                return UpdateHabit(
                    updated_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat menambah streak log pada habit_streak_logs, habit gagal diperbarui', status= False)
                )
        else:
            current_log= None
            total_completed= is_streak_log_exist['total_completed']

            for log in is_streak_log_exist['streak_logs']:
                if log['start_date'] == datetime.datetime.strptime(fields.goal_dates.start, datetime_format('date')):
                    current_log= log
            
            if current_log['current_goal'] == updated_habit['goal'] and datetime.datetime.now().date() in current_log['marked_at']:
                total_completed+= 1
                current_log['is_complete']= True
                    
            result= mongo.db.habit_tracks.find_one_and_update(
                { 
                    'habit_id': updated_habit['_id'],
                    'total_completed': total_completed,
                    'streak_logs': {
                        '$elemMatch': {
                            'start_date': datetime.datetime.strptime(fields.goal_dates.start, datetime_format('date'))
                        }
                    } 
                },
                { 
                    '$set': { 
                        'streak_logs.$.end_date': datetime.datetime.strptime(fields.goal_dates.end, datetime_format('date')),
                        'streak_logs.$.target_goal': updated_habit['goal'],
                        'streak_logs.$.is_complete': current_log['is_complete'] 
                    } 
                }
            )

            if result is None:
                return UpdateHabit(
                    updated_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat mengubah streak log pada habit_streak_logs, habit gagal diperbarui', status= False)
                )
        
        habit_track= mongo.db.habit_tracks.find_one({ 'habit_id': _id })
        #end update on habit streak logs

        return UpdateHabit(
            updated_habit= re_structure_habit_output(updated_habit, habit_track),
            response= ResponseMessage(text= 'Berhasil membarui habit', status= True)
        )

class RemoveHabits(graphene.Mutation):
    class Arguments:
        habit_ids= graphene.List(graphene.Int)
    
    removed_habits= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, habit_ids):
        is_habit_ids_exist= mongo.db.user_habits.find_one({ 
            'user_id': ObjectId(get_jwt_identity()),
            'habits': { '$all': habit_ids }
        })

        if is_habit_ids_exist is None:
            return RemoveHabits(
                removed_habits= [],
                response= ResponseMessage(text= 'Habit tidak ditemukan, habit gagal terhapus', status= False)
            )

        #start remove from habits
        remove_from_habits= mongo.db.habits.delete_many({ '_id': { '$in': habit_ids } }) 

        if remove_from_habits.deleted_count == 0:
            return RemoveHabits(
                removed_habits= [],
                response= ResponseMessage(text= 'Gagal menghapus habit dari habits collection, habit gagal terhapus', status= False)
            )
        #end remove from habits

        #start remove from user habits
        remove_from_user_habits= mongo.db.user_habits.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                '$pull': {
                    'habits': {
                        '$in': habit_ids
                    }
                }
            }
        )

        if remove_from_user_habits.modified_count == 0:
            return RemoveHabits(
                removed_habits= [],
                response= ResponseMessage(text= 'Gagal menghapus habit dari user_habits collection, habit gagal terhapus', status= False)
            )
        #end remove from user habits

        #start remove from habit streak logs
        remove_from_habit_tracks= mongo.db.habit_tracks.delete_many({ 'habit_id': { '$in': habit_ids } })

        if remove_from_habit_tracks.deleted_count == 0:
            return RemoveHabits(
                removed_habits= [],
                response= ResponseMessage(text= 'Gagal menghapus habit dari habit_streak_logs collection, habit gagal terhapus', status= False)
            )
        #end remove from habit streak logs

        return RemoveHabits(
            removed_habits= habit_ids,
            response= ResponseMessage(text= 'Berhasil menghapus habit', status= True)
        )

class MarkHabitGoal(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        marked_at= graphene.String()
    
    marked_habit= graphene.Field(Habit)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, _id, marked_at):
        #start validation check
        #validate date
        if validate_datetime(marked_at, 'date') is False:
            return MarkHabitGoal(
                marked_habit= None,
                response= ResponseMessage(text= 'Format tanggal tidak sesuai, habit goal gagal ditandai', status= False)
            )

        is_habit_id_exist= mongo.db.user_habits.find_one({ 
            'user_id': ObjectId(get_jwt_identity()),
            'habits': _id 
        })

        #check habit id exist or not
        if is_habit_id_exist is None:
            return MarkHabitGoal(
                marked_habit= None,
                response= ResponseMessage(text= 'Habit tidak ditemukan, habit goal gagal ditandai', status= False)
            )
        
        habit= mongo.db.habits.find_one({ '_id': _id })

        #check date now still between on goal start and end date
        date_now= datetime.datetime.strptime(marked_at, datetime_format('date')).date()

        #if date_now >= habit['goal_dates']['start'].date() and date_now <= habit['goal_dates']['end'].date():
        #    days_left= (habit['goal_dates']['end'].date() - date_now).days
        #else:
        #    return MarkHabitGoal(
        #        marked_habit= None,
        #        response= ResponseMessage(text= 'Tanggal tidak sesuai dengan rentang tanggal yang ditentukan, habit goal gagal ditandai', status= False)
        #    )

        if date_now < habit['goal_dates']['start'].date() or date_now > habit['goal_dates']['end'].date():
            return MarkHabitGoal(
                marked_habit= None,
                response= ResponseMessage(text= 'Tanggal tidak sesuai dengan rentang tanggal yang ditentukan, habit goal gagal ditandai', status= False)
            )
        #end validation check     

        #start mark habit
        is_already_marked= mongo.db.habit_tracks.find_one({ 
            'habit_id': _id,
            'streak_logs': {
                '$elemMatch': {
                    'start_date': habit['goal_dates']['start'],
                    'last_marked_at': datetime.datetime.strptime(marked_at, datetime_format('date'))
                }
            }
        })

        if is_already_marked:
            return MarkHabitGoal(
                marked_habit= None,
                response= ResponseMessage(text= 'Habit sudah ditandai pada tanggal tersebut', status= False)
            )
        else:
            current_track= mongo.db.habit_tracks.find_one({ 'habit_id': _id })
            current_log= None

            for log in current_track['streak_logs']:
                if log['start_date'] == habit['goal_dates']['start']:
                    current_log= log
            
            if current_log['current_goal']+1 == current_log['target_goal']:
                current_track['total_completed']+= 1
                current_log['is_complete']= True
            
            current_track['total_streaks']+= 1
            current_log['current_goal']+= 1

            result= mongo.db.habit_tracks.update_one(
                { 
                    'habit_id': _id,
                    'streak_logs': {
                        '$elemMatch': {
                            'start_date': habit['goal_dates']['start']
                        }
                    }
                },
                {
                    '$set': { 
                        'total_completed': current_track['total_completed'],
                        'total_streaks': current_track['total_streaks'],
                        'streak_logs.$.current_goal': current_log['current_goal'],
                        'streak_logs.$.last_marked_at': datetime.datetime.strptime(marked_at, datetime_format('date')),
                        'streak_logs.$.is_complete': current_log['is_complete']
                    },
                    '$push': {
                        'streak_logs.$.marked_at': datetime.datetime.strptime(marked_at, datetime_format('date'))
                    }
                }
            )

            if result.modified_count == 0:
                return MarkHabitGoal(
                    marked_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat menambah marked_at log baru pada habit_tracks, habit goal gagal ditandai', status= False)
                )

        habit_track= mongo.db.habit_tracks.find_one({ 'habit_id': _id })
        #end mark habit
        
        return MarkHabitGoal(
            marked_habit= re_structure_habit_output(habit, habit_track),
            response= ResponseMessage(text= f"Berhasil menandai habit hari ini, tanggal {marked_at}", status= True)
        )

class HabitMutation(graphene.AbstractType):
    create_habit= CreateHabit.Field()
    update_habit= UpdateHabit.Field()
    remove_habits= RemoveHabits.Field()
    mark_habit_goal= MarkHabitGoal.Field()