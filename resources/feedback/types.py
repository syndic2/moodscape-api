import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

class AppFeedbackAbstract(graphene.AbstractType):
    rating= graphene.Int()
    review= graphene.String()
    feature_category= graphene.String()
    created_at= graphene.DateTime()
 
class AppFeedbackInput(AppFeedbackAbstract, graphene.InputObjectType):
    pass

class AppFeedback(AppFeedbackAbstract, graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()

    def __init__(self, data):
        for key in data:
            if key == 'user_id':
                data[key]= str(data[key])

            setattr(self, key, data[key])

class ProtectedAppFeedback(graphene.Union):
    class Meta:
        types= (AppFeedback, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)