import graphene

from .auth.queries import AuthQuery
from .auth.mutations import AuthMutation

from .user.queries import UserQuery
from .user.mutations import UserMutation

from .article.queries import ArticleQuery
from .article.mutations import ArticleMutation

class QueryRoot(
        UserQuery, 
        ArticleQuery, 
        graphene.ObjectType
    ):
    pass

class MutationRoot(
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