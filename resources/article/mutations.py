import graphene

from .types import Article, ArticleInput
from extensions import mongo

class CreateArticle(graphene.Mutation):
    class Arguments:
        article= ArticleInput()

    article= graphene.Field(Article)
    status= graphene.Boolean()

    def mutate(self, root, article):
        result= mongo.db.articles.insert_one(vars(article))

        new_article= Article(
            title= article.title,
            author= article.author,
            posted_at= article.posted_at
        )

        return CreateArticle(article= new_article, status= True)

class ArticleMutation(graphene.AbstractType):
    new_article= CreateArticle.Field()