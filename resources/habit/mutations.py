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

        insert_on_habits= mongo.db.habits.insert_one(dict(re_structure_habit_input(fields)))

        if insert_on_habits.inserted_id is None:
            return CreateHabit(
                created_habit= None,
                response= ResponseMessage(text= 'Tidak dapat menyimpan pada habits collection, habit gagal ditambahkan', status= False)
            )

        is_user_habits_exist= mongo.db.user_habits.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

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

        return CreateHabit(
            created_habit= re_structure_habit_output(created_habit),
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

        #update on habit track
        is_habit_tracks_exist= mongo.db.habit_tracks.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'tracks.habit_id': _id
        })

        if is_habit_tracks_exist:
            update_on_habit_tracks= mongo.db.habit_tracks.find_one_and_update(
                { 'user_id': ObjectId(get_jwt_identity()), 'tracks.habit_id': _id },
                {
                    '$set': {
                        'tracks.$.target_goal': fields['goal']
                    }
                }
            )

            if update_on_habit_tracks is None:
                return UpdateHabit(
                    updated_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat membarui track pada habit_tracks, habit gagal diperbarui', status= False)
                )
        
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
        habit_tracks= mongo.db.habit_tracks.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                'tracks': {
                    '$elemMatch': {
                        'habit_id': _id
                    }
                }
            }
        )

        if 'tracks' in habit_tracks:
            updated_habit= re_structure_habit_output(updated_habit, habit_tracks['tracks'][0])
        else:
            updated_habit= re_structure_habit_output(updated_habit)

        return UpdateHabit(
            updated_habit= updated_habit,
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

        remove_from_habits= mongo.db.habits.delete_many({ '_id': { '$in': habit_ids } }) 

        if remove_from_habits.deleted_count == 0:
            return RemoveHabits(
                removed_habits= [],
                response= ResponseMessage(text= 'Gagal menghapus habit dari habits collection, habit gagal terhapus', status= False)
            )

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

        is_habit_tracks_exist= mongo.db.habit_tracks.find_one({ 
            'user_id': ObjectId(get_jwt_identity()),
            'tracks.habit_id': { '$all': habit_ids } 
        })

        if is_habit_tracks_exist:
            remove_from_habit_tracks= mongo.db.habit_tracks.update_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                {
                    '$pull': {
                        'tracks': {
                            'habit_id': { '$in': habit_ids }
                        }
                    }
                }
            )
        
            if remove_from_habit_tracks.modified_count == 0:
                return RemoveHabits(
                    removed_habits= [],
                    response= ResponseMessage(text= 'Gagal menghapus habit dari habit_tracks collection, habit gagal terhapus', status= False)
                )

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
        is_habit_tracks_exist= mongo.db.habit_tracks.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        days_left= 0

        #check date now still between on goal start and end date
        date_now= datetime.datetime.strptime(marked_at, datetime_format('date')).date()

        if date_now >= habit['goal_dates']['start'].date() and date_now <= habit['goal_dates']['end'].date():
            days_left= (habit['goal_dates']['end'].date() - date_now).days
        else:
            return MarkHabitGoal(
                marked_habit= None,
                response= ResponseMessage(text= 'Tanggal tidak sesuai dengan rentang tanggal yang ditentukan, habit goal gagal ditandai', status= False)
            )

        #check habit_tracks exist or not
        if is_habit_tracks_exist is None:
            create_habit_tracks= mongo.db.habit_tracks.insert_one({
                '_id': get_sequence('habit_tracks'),
                'user_id': ObjectId(get_jwt_identity()),
                'tracks': [
                    {
                        'habit_id': _id,
                        'current_goal': 1,
                        'target_goal': habit['goal'],
                        'streaks': 0,
                        'last_marked_at': datetime.datetime.strptime(marked_at, datetime_format('date')),
                        'logs': [
                            { 'current_goal': 1, 'marked_at': datetime.datetime.strptime(marked_at, datetime_format('date')) }
                        ]
                    }   
                ]
            })

            if create_habit_tracks.inserted_id is None:
                return MarkHabitGoal(
                    marked_habit= None,
                    response= ResponseMessage(text= 'Tidak dapat membuat habit_tracks baru, habit goal gagal ditandai', status= False)
                ) 
        else:
            is_track_exist= mongo.db.habit_tracks.find_one({ 
                'user_id': ObjectId(get_jwt_identity()),
                'tracks.habit_id': _id  
            })

            #check if track exist or not in tracks array
            if is_track_exist is None:
                create_track= mongo.db.habit_tracks.update_one(
                    { 'user_id': ObjectId(get_jwt_identity()) },
                    {
                        '$push': {
                            'tracks': {
                                'habit_id': _id,
                                'current_goal': 1,
                                'target_goal': habit['goal'],
                                'streaks': 0,
                                'last_marked_at': datetime.datetime.strptime(marked_at, datetime_format('date')),
                                'logs': [
                                    { 'current_goal': 1, 'marked_at': datetime.datetime.strptime(marked_at, datetime_format('date')) }
                                ]
                            }
                        }
                    }
                )

                if create_track.modified_count == 0:
                    return MarkHabitGoal(
                        marked_habit= None,
                        response= ResponseMessage(text= 'Tidak dapat membuat track baru, habit goal gagal ditandai', status= False)
                    )
            else:
                is_already_marked= mongo.db.habit_tracks.find_one(
                    { 'user_id': ObjectId(get_jwt_identity()) },
                    {
                        'tracks': {
                            '$elemMatch': {
                                'habit_id': _id,
                                'logs': {
                                    '$elemMatch': {
                                        'marked_at': datetime.datetime.strptime(marked_at, datetime_format('date'))
                                    }
                                }
                            }
                        }
                    }
                )

                #check is already marked or not
                if 'tracks' in is_already_marked:
                    return MarkHabitGoal(
                        marked_habit= None,
                        response= ResponseMessage(text= 'Habit ini sudah ditandai pada tanggal tersebut', status= False)
                    )
                
                current_track= mongo.db.habit_tracks.find_one(
                    { 'user_id': ObjectId(get_jwt_identity()) },
                    {
                        'tracks': {
                            '$elemMatch': {
                                'habit_id': _id
                            }
                        }
                    }
                )['tracks'][0]

                #check if tracking complete
                if current_track['current_goal'] == habit['goal']:
                    return MarkHabitGoal(
                        marked_habit= None,
                        response= ResponseMessage(text= 'Tracking habit sudah selesai, habit goal gagal ditandai', status= False)
                    )

                #update current goal & add new log
                update_habit_tracks= mongo.db.habit_tracks.update_one(
                    { 'user_id': ObjectId(get_jwt_identity()), 'tracks.habit_id': _id },
                    {
                        '$set': { 
                            'tracks.$.current_goal': current_track['current_goal']+1,
                            'tracks.$.last_marked_at': datetime.datetime.strptime(marked_at, datetime_format('date'))
                        },
                        '$push': {
                            'tracks.$.logs': { 'current_goal': current_track['current_goal']+1, 'marked_at': datetime.datetime.strptime(marked_at, datetime_format('date')) }
                        }
                    }
                )

                if update_habit_tracks.modified_count == 0:
                    return MarkHabitGoal(
                        marked_habit= None,
                        response= ResponseMessage(text= 'Tidak dapat menambah log baru pada habit_tracks, habit goal gagal ditandai', status= False)
                    ) 
        
        updated_track= mongo.db.habit_tracks.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                'tracks': {
                    '$elemMatch': {
                        'habit_id': _id
                    }
                }
            }
        )['tracks'][0]
        
        return MarkHabitGoal(
            marked_habit= re_structure_habit_output(habit, updated_track),
            response= ResponseMessage(text= f"Berhasil menandai habit hari ini, tanggal {marked_at}", status= True)
        )

class HabitMutation(graphene.AbstractType):
    create_habit= CreateHabit.Field()
    update_habit= UpdateHabit.Field()
    remove_habits= RemoveHabits.Field()
    mark_habit_goal= MarkHabitGoal.Field()