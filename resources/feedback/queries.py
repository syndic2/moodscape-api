import datetime, graphene
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import (
    get_month_name, 
    calculate_age, 
    validate_datetime, 
    datetime_format, 
    lesser_comparison_datetime, 
    get_months_between
)
from .types import AppFeedback, AppFeedbackUsers, AppFeedbacksGroupByRating, AppFeedbacksGrowthByYear, ChatbotFeedback

class FeedbackQuery(graphene.AbstractType):
    get_chatbot_feedbacks= graphene.List(ChatbotFeedback)
    get_app_feedbacks= graphene.List(AppFeedback)
    get_app_feedbacks_group_by_rating= graphene.Field(AppFeedbacksGroupByRating)
    get_app_feedbacks_growth_by_year= graphene.List(AppFeedbacksGrowthByYear, start_date= graphene.String(), end_date= graphene.String())
    get_app_feedback= graphene.Field(AppFeedback, _id= graphene.String())

    def resolve_get_chatbot_feedbacks(self, info):
        feedbacks= list(mongo.db.chatbot_feedbacks.aggregate([
            {
                '$lookup':  {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
            { '$sort': { 'created_at': -1 } }
        ]))
        filtered_feedbacks= []

        for feedback in feedbacks:
            if len(feedback['user']) > 0:
                feedback['user']= feedback['user'][0]
            
            feedback['created_at']= {
                'date': feedback['created_at'].date(),
                'time': str(feedback['created_at'].time())[:-7]
            }

            if 'is_deleted' not in feedback or feedback['is_deleted'] is False:
                filtered_feedbacks.append(feedback)
        
        return filtered_feedbacks

    def resolve_get_app_feedbacks(self, info):
        feedbacks= list(mongo.db.app_feedbacks.aggregate([
            {
                '$lookup':  {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
            { '$sort': { 'created_at': -1 } }
        ]))
        filtered_feedbacks= []

        for feedback in feedbacks:
            feedback['user']= feedback['user'][0]
            feedback['created_at']= {
                'date': feedback['created_at'].date(),
                'time': str(feedback['created_at'].time())[:-7]
            }

            if 'is_deleted' not in feedback or feedback['is_deleted'] == False:
                filtered_feedbacks.append(feedback)

        return filtered_feedbacks
    
    def resolve_get_app_feedbacks_group_by_rating(self, info):
        feedbacks= mongo.db.app_feedbacks.aggregate([
            {
                '$lookup':  {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }
            }
        ])
        very_useful= AppFeedbackUsers(group= 'Sangat membantu', users= [], user_average_age= 0)
        useful= AppFeedbackUsers(group= 'Membantu', users= [], user_average_age= 0)
        neutral= AppFeedbackUsers(group= 'Netral/biasa saja', users= [], user_average_age= 0)
        useless= AppFeedbackUsers(group= 'Tidak membantu', users= [], user_average_age= 0)
        very_useless= AppFeedbackUsers(group= 'Sangat tidak membantu', users= [], user_average_age= 0)  
        
        for feedback in feedbacks:
            if 'date_of_birth' in feedback['user'][0] and feedback['user'][0]['date_of_birth'] is not None:
                age= calculate_age(feedback['user'][0]['date_of_birth'].date())
            
            if feedback['rating'] == 5: 
                very_useful.users.append(feedback['user'][0])
                very_useful.user_average_age+= age
            elif feedback['rating'] == 4: 
                useful.users.append(feedback['user'][0])
                useful.user_average_age+= age
            elif feedback['rating'] == 3: 
                neutral.users.append(feedback['user'][0])
                neutral.user_average_age+= age
            elif feedback['rating'] == 2: 
                useless.users.append(feedback['user'][0])
                useless.user_average_age+= age
            elif feedback['rating'] == 1: 
                very_useless.users.append(feedback['user'][0])
                very_useless.user_average_age+= age

        if len(very_useful.users) > 0: very_useful.user_average_age/= len(very_useful.users) 
        if len(useful.users) > 0: useful.user_average_age/= len(useful.users)
        if len(neutral.users) > 0: neutral.user_average_age/= len(neutral.users)
        if len(useless.users) > 0: useless.user_average_age/= len(useless.users)
        if len(very_useless.users) > 0: very_useless.user_average_age/= len(very_useless.users)

        return AppFeedbacksGroupByRating(
            very_useful= very_useful,
            useful= useful,
            neutral= neutral,
            useless= useless,
            very_useless= very_useless
        )
    
    def resolve_get_app_feedbacks_growth_by_year(self, info, **kwargs):
        start_date= kwargs.get('start_date')
        end_date= kwargs.get('end_date')

        if lesser_comparison_datetime(start_date, end_date, 'date') is False:
            return []

        if validate_datetime(start_date, 'date') is False or validate_datetime(end_date, 'date') is False:
            return []

        start_date= datetime.datetime.strptime(start_date, datetime_format('date'))
        end_date= datetime.datetime.strptime(end_date, datetime_format('date'))

        feedbacks= list(mongo.db.app_feedbacks.find({ 'created_at': { '$gte': start_date, '$lte': end_date } }))
        feedbacks_growth_by_year= []

        for date in list(get_months_between(start_date, end_date)):
            feedbacks_growth_by_year.append(AppFeedbacksGrowthByYear(
                month_name= get_month_name(date.month-1),
                month_number= date.month,
                year= date.year,
                feedbacks= [],
                average_rating= 0
            ))

        for growth in feedbacks_growth_by_year:
            for feedback in feedbacks:
                created_at= feedback['created_at'].date()

                if (created_at.month, created_at.year) == (growth.month_number, growth.year):
                    growth.feedbacks.append(feedback)
                    growth.average_rating+= feedback['rating']

        for growth in feedbacks_growth_by_year:
            if len(growth.feedbacks) > 0: growth.average_rating/= len(growth.feedbacks)

        return feedbacks_growth_by_year

    def resolve_get_app_feedback(self, info, _id):
        feedback= list(mongo.db.app_feedbacks.aggregate([
            {
                '$match': {
                    '_id': ObjectId(_id)
                }
            },
            {
                '$lookup':  {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }
            }
        ]))

        if len(feedback) == 0:
            return None

        feedback[0]['user']= feedback[0]['user'][0]
        feedback[0]['created_at']= {
            'date': feedback[0]['created_at'].date(),
            'time': feedback[0]['created_at'].time()
        }

        return feedback[0]