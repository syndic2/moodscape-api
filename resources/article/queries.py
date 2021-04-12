import graphene
from bson.objectid import ObjectId

from .types import ArticleInput, Article
from ..utility_types import ResponseMessage 
from extensions import mongo

class ArticleQuery(graphene.AbstractType):
    article= graphene.Field(Article, _id= graphene.String())
    all_article= graphene.List(Article, fields= graphene.Argument(ArticleInput))

    def resolve_article(self, info, _id): 
        article= mongo.db.articles.find_one({ '_id': ObjectId(_id) })

        return article
    
    def resolve_all_article(self, info, fields):
        if fields.title:
            title= fields.title
            fields['title']= { '$regex': title, '$options': 'i' }
        
        documents= list(mongo.db.articles.find(fields))

        def to_article_type(document):
            article= Article(document)
            
            return article

        return list(map(to_article_type, documents))
    
