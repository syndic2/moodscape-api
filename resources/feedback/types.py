import graphene

from ..utility_types import Timestamps
from ..user.types import User

#Chatbot feedback
class ChatbotMessageAbstract(graphene.AbstractType):
    _id= graphene.String()
    sender= graphene.String()
    recipient_id= graphene.String()
    text= graphene.String()
    video_url= graphene.String()

class ChatbotMessageInput(graphene.InputObjectType, ChatbotMessageAbstract):
    pass

class ChatbotMessage(graphene.ObjectType, ChatbotMessageAbstract):
    pass

class ChatbotFeedbackAbstract(graphene.AbstractType):
    review= graphene.String()

class ChatbotFeedbackInput(graphene.InputObjectType, ChatbotFeedbackAbstract):
    bot_message= ChatbotMessageInput()
    messages= graphene.List(ChatbotMessageInput)

class ChatbotFeedback(graphene.ObjectType, ChatbotFeedbackAbstract):
    _id= graphene.String()
    user= graphene.Field(User)
    bot_message= graphene.Field(ChatbotMessage)
    messages= graphene.List(ChatbotMessage)
    handle_status= graphene.String()
    handle_note= graphene.String()
    created_at= graphene.Field(Timestamps)

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
    handle_status= graphene.String()
    handle_note= graphene.String()
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
    month_name= graphene.String()
    month_number= graphene.Int()
    year= graphene.Int()
    feedbacks= graphene.List(AppFeedback)
    average_rating= graphene.Int()