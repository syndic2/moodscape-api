import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

class ProtectedAuth(graphene.Union):
    class Meta:
        types= (ResponseMessage, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)