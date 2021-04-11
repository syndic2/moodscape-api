import graphene

from resources.auth.queries import AuthQuery
from resources.auth.mutations import AuthMutation

from resources.user.queries import UserQuery
from resources.user.mutations import UserMutation

from resources.article.queries import ArticleQuery
from resources.article.mutations import ArticleMutation

from extensions import mongo

class QueryRoot(
        AuthQuery, 
        UserQuery, 
        ArticleQuery, 
        graphene.ObjectType
    ):
    pass

class MutationRoot(
        AuthMutation, 
        UserMutation, 
        ArticleMutation, 
        graphene.ObjectType
    ):
    pass

class AuthQueryRoot(AuthQuery, graphene.ObjectType):
    pass

class AuthMutationRoot(AuthMutation, graphene.ObjectType):
    pass

main_schema= graphene.Schema(query= QueryRoot, mutation= MutationRoot)
auth_schema= graphene.Schema(query= AuthQueryRoot, mutation= AuthMutationRoot)