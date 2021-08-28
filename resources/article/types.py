import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

#Article
class ArticleAbstract(graphene.AbstractType):
    title= graphene.String()
    short_summary= graphene.String()
    author= graphene.String()
    posted_at= graphene.String()
    reviewed_by= graphene.String()
    header_img= graphene.String()
    content= graphene.String()
    url_name= graphene.String()
    url= graphene.String()

class ArticleInput(ArticleAbstract, graphene.InputObjectType):
    pass

class Article(ArticleAbstract, graphene.ObjectType):
    _id= graphene.Int()

    def __init__(self, data):
        for key in data:            
            setattr(self, key, data[key])

class ArticlePagination(graphene.ObjectType):
    offset= graphene.Int()
    limit= graphene.Int()
    max_page= graphene.Int()
    articles= graphene.List(Article)

class UserArticles(graphene.ObjectType):
    _id= graphene.Int()
    user_id= graphene.String()
    articles= graphene.List(Article)
    response= graphene.Field(ResponseMessage)

#Article/Auth
class ProtectedUserArticles(graphene.Union):
    class Meta:
        types= (UserArticles, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)    