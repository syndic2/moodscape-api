import graphene

from ..utility_types import Timestamps
from ..user.types import User

#Chatbot feedback

#App feedback
class AppFeedbackAbstract(graphene.AbstractType):
    rating= graphene.Int()
    review= graphene.String()
    feature_category= graphene.String()

class AppFeedbackInput(AppFeedbackAbstract, graphene.InputObjectType):
    pass

class AppFeedback(AppFeedbackAbstract, graphene.ObjectType):
    _id= graphene.String()
    user= graphene.Field(User)
    created_at= graphene.Field(Timestamps)

class AppFeedbackUsers(graphene.ObjectType):
    group= graphene.String()
    users= graphene.List(User)
    user_average_age= graphene.Int()

class AppFeedbacksGroupByRating(graphene.ObjectType):
    very_useful= graphene.Field(AppFeedbackUsers)
    useful= graphene.Field(AppFeedbackUsers)
    neutral= graphene.Field(AppFeedbackUsers)
    useless= graphene.Field(AppFeedbackUsers)
    very_useless= graphene.Field(AppFeedbackUsers)

class AppFeedbacksGrowthByYear(graphene.ObjectType):
    month= graphene.String()
    feedbacks= graphene.List(AppFeedback)
    average_rating= graphene.Int()