import graphene

from .types import Article, ArticleInput
from extensions import mongo

class ArticleQuery(graphene.AbstractType):
    article= graphene.Field(Article, title= graphene.String())

    def resolve_article(self, info, title):
        article= mongo.db.articles.find_one({ 'title': title })
        
        return article