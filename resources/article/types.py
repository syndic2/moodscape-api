import graphene
from ..utility_types import ResponseMessage

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
            #if key == '_id':
            #    data[key]= int(data[key])
            
            setattr(self, key, data[key])

class ArticlePagination(graphene.ObjectType):
    offset= graphene.Int()
    limit= graphene.Int()
    max_page= graphene.Int()
    articles= graphene.List(Article)
    response= graphene.Field(ResponseMessage)
    