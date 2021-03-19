import graphene

class ArticleAbstract(graphene.AbstractType):
    title= graphene.String()
    short_summary= graphene.String()
    author= graphene.String()
    posted_at= graphene.String()
    reviewed_by= graphene.String()
    head_img= graphene.String()
    content= graphene.String()

class Article(ArticleAbstract, graphene.ObjectType):
    pass

class ArticleInput(ArticleAbstract, graphene.InputObjectType):
    pass