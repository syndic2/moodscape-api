import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage
from ..article.types import Article

class UserArticles(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    articles= graphene.List(Article)
    response= graphene.Field(ResponseMessage)

class ArchivedArticleIds(graphene.ObjectType):
    article_ids= graphene.List(graphene.Int)

class ProtectedUserArticles(graphene.Union):
    class Meta:
        types= (UserArticles, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

class ProtectedArchivedArticleIds(graphene.Union):
    class Meta:
        types= (ArchivedArticleIds, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)





