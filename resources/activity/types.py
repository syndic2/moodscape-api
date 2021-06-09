import graphene

class ActivityAbstract(graphene.AbstractType):
    name= graphene.String()
    icon= graphene.String()

class ActivityInput(ActivityAbstract, graphene.InputObjectType):
    pass

class Activity(ActivityAbstract, graphene.ObjectType):
    _id= graphene.Int()

class ActivityIcon(graphene.ObjectType):
    _id= graphene.Int()
    name= graphene.String()

class ActivityCategoryAbstract(graphene.AbstractType):
    category= graphene.String()

class ActivityCategoryInput(ActivityCategoryAbstract, graphene.InputObjectType):
    activities= graphene.List(graphene.Int)

class ActivityCategory(ActivityCategoryAbstract, graphene.ObjectType):
    _id= graphene.Int()
    activities= graphene.List(Activity)

