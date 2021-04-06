import graphene

class ArticleAbstract(graphene.AbstractType):
    title= graphene.String()
    short_summary= graphene.String()
    author= graphene.String()
    posted_at= graphene.String()
    reviewed_by= graphene.String()
    header_img= graphene.String()
    content= graphene.String()
    url= graphene.String()

class ArticleInput(ArticleAbstract, graphene.InputObjectType):
    pass

class Article(ArticleAbstract, graphene.ObjectType):
    _id= graphene.String()

    def __init__(self, data):
        for key in data:
            if key == '_id':
                data[key]= str(data[key])
            
            setattr(self, key, data[key])