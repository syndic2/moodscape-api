import graphene

class ActivityAbstract(graphene.AbstractType):
    name= graphene.String()
    icon= graphene.String()

class ActivityInput(ActivityAbstract, graphene.InputObjectType):
    pass

class Activity(ActivityAbstract, graphene.ObjectType):
    _id= graphene.Int()

class ActivityCategoryAbstract(graphene.AbstractType):
    category= graphene.String()

class ActivityCategoryInput(ActivityCategoryAbstract, graphene.InputObjectType):
    pass

class ActivityCategoryIds(graphene.AbstractType, graphene.ObjectType):
    _id= graphene.Int()
    activities= graphene.List(graphene.Int)

class ActivityCategory(ActivityCategoryAbstract, graphene.ObjectType):
    _id= graphene.Int()
    activities= graphene.List(Activity)

