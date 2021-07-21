import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import auto_increment_id
from ..utility_types import ResponseMessage
from .types import ActivityInput, ActivityCategoryInput, Activity, ActivityCategory, ProtectedActivity, ProtectedActivityCategory

class CreateActivity(graphene.Mutation):
    class Arguments:
        fields= ActivityInput()
    
    created_activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage) 
    
    def mutate(self, info, fields):
        return CreateActivity(response= ResponseMessage(text= 'Berhasil menambahkan aktivitas baru', status= True))

class UpdateActivity(graphene.Mutation):
    class Arguments:
        fields= ActivityInput()

    updated_activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        return UpdateActivity(response= ResponseMessage(text= 'Berhasil membarui aktivitas', status= True))

class RemoveActivity(graphene.Mutation):
    class Arguments:
        activity_ids= graphene.List(graphene.Int)

    removed_activities= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, activity_ids):
        return RemoveActivity(response= ResponseMessage(text= 'Berhasil menghapus aktivitas', status= True))

class CreateActivityCategory(graphene.Mutation):
    class Arguments:
        fields= ActivityCategoryInput()

    created_activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        return CreateActivityCategory(response= ResponseMessage(text= 'Berhasil menambahkan kategori aktivitas baru', status= True))

class UpdateActivityCategory(graphene.Mutation):
    class Arguments:
        fields= ActivityCategoryInput()

    updated_activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)
    
    def mutate(self, info, fields):
        return UpdateActivityCategory(response= ResponseMessage(text= 'Berhasil membarui kategori aktivitas', status= True))

class RemoveActivityCategory(graphene.Mutation):
    class Arguments:
        activity_category_ids= graphene.List(graphene.Int)
    
    removed_activity_categories= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, activity_category_ids):
        return RemoveActivityCategory(response= ResponseMessage(text= 'Berhasil menghapus kategori aktivitas', status= True))

class ActivityMutation(graphene.AbstractType):
    #User handle activity
    create_activity= CreateActivity.Field()
    update_activity= UpdateActivity.Field()
    remove_activity= RemoveActivity.Field()
    
    #User handle activity category
    create_activity_category= CreateActivityCategory.Field()
    update_activity_category= UpdateActivityCategory.Field()
    remove_activity_category= RemoveActivityCategory.Field()