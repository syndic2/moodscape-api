import graphene
from flask_graphql_auth import fields, get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from utilities.helpers import auto_increment_id
from extensions import mongo
from ..utility_types import ResponseMessage
from ..activity.types import ActivityInput, ActivityCategoryInput, Activity, ActivityCategory
from .types import ProtectedUserActivity, ProtectedUserActivityCategory

class CreateUserActivity(graphene.Mutation):
    class Arguments:
        fields= ActivityInput()
    
    created_activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage) 

    def mutate(self, root, fields):
        return CreateUserActivity(response= ResponseMessage(text= 'Berhasil menambahkan aktivitas baru', status= True))

class UpdateUserActivity(graphene.Mutation):
    class Arguments:
        fields= ActivityInput()

    updated_activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, fields):
        return UpdateUserActivity(response= ResponseMessage(text= 'Berhasil membarui aktivitas', status= True))

class RemoveUserActivity(graphene.Mutation):
    class Arguments:
        activity_ids= graphene.List(graphene.Int)

    removed_activities= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, activity_ids):
        return RemoveUserActivity(response= ResponseMessage(text= 'Berhasil menghapus aktivitas', status= True))

class CreateUserActivityCategory(graphene.Mutation):
    class Arguments:
        fields= ActivityCategoryInput()

    created_activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, fields):
        return CreateUserActivityCategory(response= ResponseMessage(text= 'Berhasil menambahkan kategori aktivitas baru', status= True))

class UpdateUserActivityCategory(graphene.Mutation):
    class Arguments:
        fields= ActivityCategoryInput()

    updated_activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)
    
    def mutate(self, root, fields):
        return UpdateUserActivityCategory(response= ResponseMessage(text= 'Berhasil membarui kategori aktivitas', status= True))

class RemoveUserActivityCategory(graphene.Mutation):
    class Arguments:
        activity_category_ids= graphene.List(graphene.Int)
    
    removed_activity_categories= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, activity_category_ids):
        return RemoveUserActivityCategory(response= ResponseMessage(text= 'Berhasil menghapus kategori aktivitas', status= True))

class UserActivitiesMutation(graphene.AbstractType):
    #User handle activity
    create_user_activity= CreateUserActivity.Field()
    update_user_activity= UpdateUserActivity.Field()
    remove_user_activity= RemoveUserActivity.Field()
    
    # User handle activity category
    create_user_activity_category= CreateUserActivityCategory.Field()
    update_user_activity_category= UpdateUserActivityCategory.Field()
    remove_user_activity_category= RemoveUserActivityCategory.Field()
