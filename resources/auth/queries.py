import graphene
from flask_graphql_auth import get_jwt_identity, query_jwt_required

from .types import ProtectedAuth
from ..utility_types import ResponseMessage
from extensions import mongo

class AuthQuery(graphene.AbstractType):
    check_token= graphene.Field(ProtectedAuth, token= graphene.String())

    @query_jwt_required
    def resolve_check_token(self, info):

        return ResponseMessage(text= 'Authenticated.', status= True)