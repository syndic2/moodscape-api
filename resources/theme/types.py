import graphene

class ThemeColorAbstract(graphene.AbstractType):
    primary= graphene.String()
    primary_rgb= graphene.String()
    primary_contrast= graphene.String()
    primary_contrast_rgb= graphene.String()
    primary_shade= graphene.String()
    primary_tint= graphene.String()

class ThemeColorInput(ThemeColorAbstract, graphene.InputObjectType):
    pass

class ThemeColor(ThemeColorAbstract, graphene.ObjectType):
    pass

class ThemeAbstract(graphene.AbstractType):
    name= graphene.String()
    #img_url= graphene.String()
    is_active= graphene.Boolean()

class ThemeInput(ThemeAbstract, graphene.InputObjectType):
    colors= ThemeColorInput()

class Theme(ThemeAbstract, graphene.ObjectType):
    _id= graphene.String()
    colors= graphene.Field(ThemeColor)