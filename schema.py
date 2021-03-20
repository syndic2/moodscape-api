import graphene

from resources.auth.mutations import AuthMutation

from resources.user.queries import UserQuery
from resources.user.mutations import UserMutation

from resources.article.queries import ArticleQuery
from resources.article.mutations import ArticleMutation

from extensions import mongo

class QueryRoot(UserQuery, ArticleQuery, graphene.ObjectType):
    pass

class MutationRoot(AuthMutation, UserMutation, ArticleMutation, graphene.ObjectType):
    pass

schema= graphene.Schema(query= QueryRoot, mutation= MutationRoot)