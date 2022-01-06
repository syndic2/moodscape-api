import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

import datetime

from extensions import mongo
from utilities.helpers import validate_datetime, datetime_format, get_month_name
from ..utility_types import ResponseMessage
from .types import (
    MoodFilterInput, 
    MoodResponse, 
    UserMoods, 
    UserMoodsChart, 
    ProtectedUserMoods, 
    ProtectedUserMoodsChart, 
    ProtectedMood
)

class GetUserMoods(graphene.AbstractType):
    get_user_moods= graphene.Field(ProtectedUserMoods)
    get_user_moods_chart= graphene.Field(ProtectedUserMoodsChart)
    get_user_mood= graphene.Field(ProtectedMood, _id= graphene.Int())
    get_filtered_user_mood= graphene.Field(ProtectedUserMoods, filters= graphene.Argument(MoodFilterInput))

    @query_header_jwt_required
    def resolve_get_user_moods(self, info):
        user_moods= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_moods is None or not user_moods['moods']:
            return UserMoods(
                moods= [],
                response= ResponseMessage(text= 'Belum memiliki mood yang tersimpan', status= False) 
            )

        moods= list(mongo.db.moods.find({ '_id': { '$in': user_moods['moods'] } }).sort('created_at', -1))

        for mood in moods:
            mood['created_at']= {
                'date': mood['created_at'].date(),
                'time': str(mood['created_at'].time())[:-3]
            }

        return UserMoods(
            _id= user_moods['_id'],
            user_id=  user_moods['user_id'],
            moods= moods,
            response= ResponseMessage(text= 'Berhasil mengembalikan mood pengguna', status= True)
        )
    
    @query_header_jwt_required
    def resolve_get_user_moods_chart(self, info):
        user_moods= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_moods is None or not user_moods['moods']:
            return UserMoodsChart(
                user_id= None,
                moods_chart= []
            )

        moods= list(mongo.db.moods.find({ '_id': { '$in': user_moods['moods'] } }))
        moods_chart= []

        #create month group
        for month in range(12):
            moods_chart.append({
                'group': get_month_name(month),
                'mood_average_group_by_year': []
            })

        #create year group
        for mood in moods:
            created_at= mood['created_at'].date()

            #distinct year
            is_year_exist_in_group= [year_group for year_group in moods_chart[created_at.month-1]['mood_average_group_by_year'] if year_group['year'] == created_at.year]

            if len(is_year_exist_in_group) == 0:
                moods_chart[created_at.month-1]['mood_average_group_by_year'].append({
                    'year': created_at.year,
                    'mood_average_by_range_date': []
                })

        #create range date group in each year group
        for month_group in moods_chart:
            for year_group in month_group['mood_average_group_by_year']:
                start_date= 1
                end_date= 3 

                for date in range(10):
                    year_group['mood_average_by_range_date'].append({
                        'start_date': start_date,
                        'end_date': end_date,
                        'moods': [],
                        'average': 0
                    })

                    start_date+= 3
                    end_date+= 3

        #grouping mood by range date
        for mood in moods:
            created_at= mood['created_at'].date()

            for year_group in moods_chart[created_at.month-1]['mood_average_group_by_year']:
                if year_group['year'] == created_at.year:
                    for date_group in year_group['mood_average_by_range_date']:
                        if created_at.day >= date_group['start_date'] and created_at.day <= date_group['end_date']:
                            mood_temp= mood.copy()
                            mood_temp['created_at']= {
                                'date': mood_temp['created_at'].date(),
                                'time': str(mood_temp['created_at'].time())[:-3]
                            }
                            date_group['moods'].append(mood_temp)
                            date_group['average']+= mood_temp['emoticon']['value']
        
        #calculate average of moods on each range date group
        for month_group in moods_chart:
            for year_group in month_group['mood_average_group_by_year']:
                for date_group in year_group['mood_average_by_range_date']:
                    if len(date_group['moods']) > 0: date_group['average']/= len(date_group['moods'])

        return UserMoodsChart(
            user_id= user_moods['user_id'],
            moods_chart= moods_chart
        )
    
    @query_header_jwt_required
    def resolve_get_user_mood(self, info, _id):
        is_mood_id_exist= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()), 'moods': _id })

        if is_mood_id_exist is None:
            return MoodResponse(
                mood= None,
                response= ResponseMessage(text= 'Mood tidak ditemukan', status= False)
            )

        result= mongo.db.moods.find_one({ '_id': _id })

        if result is None:
            return MoodResponse(
                mood= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, mood tidak ditemukan', status= False)
            )

        result['created_at']= {
            'date': result['created_at'].date(),
            'time': str(result['created_at'].time())[:-3]
        }

        return MoodResponse(
            mood= result,
            response= ResponseMessage(text= 'Berhasil mengembalikan mood', status= True)
        )

    @query_header_jwt_required
    def resolve_get_filtered_user_mood(self, info, filters):
        filter_conditions= []

        if filters.emoticon_name != '':
            filter_conditions.append({ 'emoticon.name': filters.emoticon_name })
        if filters.parameters.internal is True:
            filter_conditions.append({ 'parameters.internal': { '$regex': filters.search_text, '$options': 'i' } })
        if filters.parameters.external is True:
            filter_conditions.append({ 'parameters.external': { '$regex': filters.search_text, '$options': 'i' } })
        if len(filters.activity_ids) > 0:
            filter_conditions.append({ 'activities._id': { '$all': filters.activity_ids } })
        if filters.note is True:
            filter_conditions.append({ 'note': { '$regex': filters.search_text, '$options': 'i' } })
        if ((filters.created_date.start != '' and filters.created_date.end != '') and
            (validate_datetime(filters.created_date.start, 'date') and validate_datetime(filters.created_date.end, 'date'))):
            filter_conditions.append({
                '$and': [
                    { 'created_at': { '$gte': datetime.datetime.strptime(f'{filters.created_date.start} 23:59', datetime_format('datetime')) } },
                    { 'created_at': { '$lte': datetime.datetime.strptime(f'{filters.created_date.end} 23:59', datetime_format('datetime')) } }
                ]
            })

        user_moods= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if user_moods is None or not user_moods['moods']:
            return UserMoods(
                moods= [],
                response= ResponseMessage(text= 'Belum memiliki mood yang tersimpan', status= False)
            ) 

        moods= []

        if len(filter_conditions) > 0: 
            moods= list(mongo.db.moods.find({ '_id': { '$in': user_moods['moods'] }, '$and': filter_conditions }).sort('created_at', -1))

        for mood in moods:
            mood['created_at']= {
                'date': mood['created_at'].date(),
                'time': str(mood['created_at'].time())[:-3]
            }

        return UserMoods(
            _id= user_moods['_id'],
            user_id=  ObjectId(get_jwt_identity()),
            moods= list(moods),
            response= ResponseMessage(text= 'Berhasil mengembalikan hasil pencarian mood pengguna', status= True)
        ) 

class MoodQuery(GetUserMoods, graphene.AbstractType):
    pass