import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import get_sequence, get_sequence_in_array
from ..utility_types import ResponseMessage
from .types import ActivityInput, ActivityCategoryInput, Activity, ActivityCategory

#Activity
class CreateActivity(graphene.Mutation):
    class Arguments:
        fields= ActivityInput()
        activity_category_id= graphene.Int()

    created_activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage) 
    
    @mutation_header_jwt_required
    def mutate(self, info, fields, activity_category_id):
        is_user_activities_exist= mongo.db.user_activities.find_one({ 'user_id': ObjectId(get_jwt_identity()) })
        query_conditions= {
            'query_filter': { 'user_id': ObjectId(get_jwt_identity()) },
            '$elemMatch': {}
        }

        if is_user_activities_exist is None:
            create_user_activities= mongo.db.user_activities.insert_one({
                '_id': get_sequence('user_activities'),
                'user_id': ObjectId(get_jwt_identity()),
                'activity_categories': [
                    {
                        '_id': get_sequence_in_array('user_activities', ObjectId(get_jwt_identity()), 'activity_categories'),
                        'category': None,
                        'activities': [
                            {
                                '_id': get_sequence_in_array('user_activities', ObjectId(get_jwt_identity()), 'activities'),
                                'name': fields.name,
                                'icon': fields.icon
                            }
                        ]
                    }
                ]
            })

            if create_user_activities.inserted_id is None:
                return CreateActivity(
                    created_activity= None,
                    response= ResponseMessage(text= 'Tidak dapat membuat user_activities baru, aktivitas gagal ditambahkan', status= False)
                )
        else:
            if activity_category_id == 0:
                is_none_category_exist= mongo.db.user_activities.find_one({
                    'user_id': ObjectId(get_jwt_identity()),
                    'activity_categories.category': None
                })

                if is_none_category_exist is None:
                    create_none_category= mongo.db.user_activities.update_one(
                        { 'user_id': ObjectId(get_jwt_identity()) },
                        {
                            '$push': {
                                'activity_categories': {
                                    '_id': get_sequence_in_array('user_activities', ObjectId(get_jwt_identity()), 'activity_categories'),
                                    'category': None,
                                    'activities': []
                                }
                            }
                        }
                    )

                    if create_none_category.modified_count == 0:
                        return CreateActivity(
                            created_activity= None,
                            response= ResponseMessage(text= 'Tidak dapat membuat kategori "None", aktivitas gagal ditambahkan', status= False)
                        )

                query_conditions['query_filter']['activity_categories.category']= None
                query_conditions['$elemMatch']= { 'category': None }
            else:
                is_category_id_exist= mongo.db.user_activities.find_one(
                    { 'user_id': ObjectId(get_jwt_identity()) },
                    {
                        'activity_categories': {
                            '$elemMatch': {
                                '_id': activity_category_id
                            }
                        }
                    }
                )

                if 'activity_categories' not in is_category_id_exist:
                    return CreateActivity(
                        created_activity= None,
                        response= ResponseMessage(text= 'Kategori aktivitas tidak ditemukan, aktivitas gagal ditambahkan', status= False)
                    )
                
                query_conditions['query_filter']['activity_categories._id']= activity_category_id
                query_conditions['$elemMatch']= { '_id': activity_category_id }
            
            insert_on_user_activities= mongo.db.user_activities.update_one(
                query_conditions['query_filter'],
                {
                    '$push': {
                        'activity_categories.$.activities': {
                            '_id': get_sequence_in_array('user_activities', ObjectId(get_jwt_identity()), 'activities'),
                            'name': fields.name,
                            'icon': fields.icon
                        }
                    }
                }
            )

            if insert_on_user_activities.modified_count == 0:
                return CreateActivity(
                    created_activity= None,
                    response= ResponseMessage(text= 'Tidak dapat menyimpan pada user_activities collection, aktivitas gagal ditambahkan', status= False)
                )

        created_activity= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                'activity_categories': {
                    '$elemMatch': query_conditions['$elemMatch']
                }
            }
        )

        return CreateActivity(
            created_activity= created_activity['activity_categories'][0]['activities'][-1],
            response= ResponseMessage(text= 'Berhasil menambahkan aktivitas baru', status= True)
        )

class UpdateActivity(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        fields= ActivityInput()
        activity_category_id= graphene.Int()

    updated_activity= graphene.Field(Activity)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, _id, fields, activity_category_id):
        query_conditions= {
            '$elemMatch': {
                'activities': {
                    '$elemMatch': {
                        '_id': _id
                    }
                }
            },
            'array_filters': {
                'item1': {}
            }
        }
        update_query= {}

        if activity_category_id == 0:
            query_conditions['$elemMatch']['category']= None
            query_conditions['array_filters']['item1']= { 'item1.category': None } 
        else:
            query_conditions['$elemMatch']['_id']= activity_category_id
            query_conditions['array_filters']['item1']= { 'item1._id': activity_category_id } 

            is_category_id_exist= mongo.db.user_activities.find_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                { 
                    'activity_categories': {
                        '$elemMatch': {
                            '_id': activity_category_id
                        }
                    } 
                }
            )

            if 'activity_categories' not in is_category_id_exist:
                return UpdateActivity(
                    updated_activity= None,
                    response= ResponseMessage(text= 'Kategori aktivitas tidak ditemukan, aktivitas gagal diperbarui', status= False)
                )

        is_activity_id_exist= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                'activity_categories': {
                    '$elemMatch': query_conditions['$elemMatch']
                }
            }
        )

        if 'activity_categories' not in is_activity_id_exist:
            return UpdateActivity(
                updated_activity= None,
                response= ResponseMessage(text= 'Aktivitas tidak ditemukan pada kategori ini, aktivitas gagal diperbarui', status= False)
            )

        if 'name' in fields:
            update_query['activity_categories.$[item1].activities.$[item2].name']= fields.name
        elif 'icon' in fields:
            update_query['activity_categories.$[item1].activities.$[item2].icon']= fields.icon
        
        result= mongo.db.user_activities.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            { '$set': update_query },
            array_filters= [
                query_conditions['array_filters']['item1'],
                { 'item2._id': _id }
            ]   
        )

        if result.matched_count == 0 and result.modified_count == 0:
            return UpdateActivity(
                updated_activity= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, aktivitas gagal diperbarui', status= False)
            )
        
        updated_activity_query= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            { 
                'activity_categories': {
                    '$elemMatch': query_conditions['$elemMatch']
                } 
            }
        )
        updated_activity= None

        for activity in updated_activity_query['activity_categories'][0]['activities']:
            if activity['_id'] == _id:
                updated_activity= activity
                break

        return UpdateActivity(
            updated_activity= updated_activity,
            response= ResponseMessage(text= 'Berhasil membarui aktivitas', status= True)
        )

class RemoveActivities(graphene.Mutation):
    class Arguments:
        activity_ids= graphene.List(graphene.Int)
        activity_category_id= graphene.Int()

    removed_activities= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, activity_ids, activity_category_id):
        query_conditions= {
            'query_filter': {  'user_id': ObjectId(get_jwt_identity()) },
            '$elemMatch': {
                'activities._id': {
                    '$all': activity_ids
                }
            }
        }

        if activity_category_id == 0:
            query_conditions['query_filter']['activity_categories.category']= None
            query_conditions['$elemMatch']['category']= None
        else:
            query_conditions['query_filter']['activity_categories._id']= activity_category_id
            query_conditions['$elemMatch']['_id']= activity_category_id
        
            is_category_id_exist= mongo.db.user_activities.find_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                { 
                    'activity_categories': {
                        '$elemMatch': {
                            '_id': activity_category_id
                        }
                    } 
                }
            )

            if 'activity_categories' not in is_category_id_exist:
                return RemoveActivities(
                    removed_activities= [],
                    response= ResponseMessage(text= 'Kategori aktivitas tidak ditemukan, aktivitas gagal terhapus', status= False)
                )

        is_activity_ids_exist= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            { 
                'activity_categories': {
                    '$elemMatch': query_conditions['$elemMatch']
                } 
            }
        )
        
        if 'activity_categories' not in is_activity_ids_exist:
            return RemoveActivities(
                removed_activities= [],
                response= ResponseMessage(text= 'Aktivitas tidak ditemukan pada kategori ini, aktivitas gagal terhapus', status= False)
            )
        
        result= mongo.db.user_activities.update_one(
            query_conditions['query_filter'],
            {
                '$pull': {
                    'activity_categories.$.activities': {
                        '_id': {
                            '$in': activity_ids
                        }
                    }
                }
            }
        )

        if result.modified_count == 0:
            return RemoveActivities(
                removed_activities= [],
                response= ResponseMessage(text= 'Terjadi kendala pada server, aktivitas gagal terhapus', status= False)
            )

        return RemoveActivities(
            removed_activities= activity_ids,
            response= ResponseMessage(text= 'Berhasil menghapus aktivitas', status= True)
        )

class MoveActivitiesIntoCategory(graphene.Mutation):
    class Arguments:
        activity_ids= graphene.List(graphene.Int)
        from_category_id= graphene.Int()
        to_category_id= graphene.Int()

    moved_activities= graphene.List(Activity)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, activity_ids, from_category_id, to_category_id):
        query_conditions= {
            'remove_filter_query': { 
                'user_id': ObjectId(get_jwt_identity())
            },
            '$elemMatch': {
                'activities._id': {
                    '$all': activity_ids
                }
            },
            'in': {
                'activities': {
                    '$filter': {
                        'input': '$$item1.activities',
                        'as': 'item2',
                        'cond': {
                            '$in': ['$$item2._id', activity_ids]
                        }
                    }
                }
            },
            'cond': {}
        }

        if from_category_id == 0:
            query_conditions['$all']= [to_category_id]
            query_conditions['$elemMatch']['category']= None
            query_conditions['in']['category']= '$$item1.category'
            query_conditions['cond']['$eq']= ['$$item1.category', None]
            query_conditions['remove_filter_query']['activity_categories.category']= None
        else:
            query_conditions['$all']= [from_category_id, to_category_id]
            query_conditions['$elemMatch']['_id']= from_category_id
            query_conditions['in']['_id']= '$$item1._id'
            query_conditions['cond']['$eq']= ['$$item1._id', from_category_id]
            query_conditions['remove_filter_query']['activity_categories._id']= from_category_id

        is_category_ids_exist= mongo.db.user_activities.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'activity_categories._id': {
                '$all': query_conditions['$all']
            }
        })

        if is_category_ids_exist is None or from_category_id == to_category_id:
            return MoveActivitiesIntoCategory(
                moved_activities= [],
                response= ResponseMessage(text= 'Kategori asal atau tujuan tidak ditemukan/sesuai, aktivitas gagal dipindahkan', status= False)
            )

        is_activity_ids_exist= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            { 
                'activity_categories': {
                    '$elemMatch': query_conditions['$elemMatch']
                } 
            }
        )

        if 'activity_categories' not in is_activity_ids_exist:
            return MoveActivitiesIntoCategory(
                moved_activities= [],
                response= ResponseMessage(text= 'Aktivitas tidak ditemukan pada kategori asal, aktivitas gagal dipindahkan', status= False)
            )

        activities= mongo.db.user_activities.aggregate([
            {
                '$match': {
                    'user_id': ObjectId(get_jwt_identity()),
                    'activity_categories': {
                        '$elemMatch': query_conditions['$elemMatch']
                    }
                },
            },
            {
                '$addFields': {
                    'activity_categories': {
                        '$filter': {
                            'input': {
                                '$map': {
                                    'input': '$activity_categories',
                                    'as': 'item1',
                                    'in': query_conditions['in']
                                }
                            },
                            'as': 'item1',
                            'cond': query_conditions['cond']
                        }
                    }
                }
            },
        ])
        activities= list(activities)[0]['activity_categories'][0]['activities']

        remove_activities_from_origin_category= mongo.db.user_activities.update_one(
            query_conditions['remove_filter_query'],
            {
                '$pull': {
                    'activity_categories.$.activities': {
                        '_id': {
                            '$in': activity_ids
                        }
                    }
                }
            }
        )

        if remove_activities_from_origin_category.modified_count == 0:
            return MoveActivitiesIntoCategory(
                moved_activities= [],
                response= ResponseMessage(text= 'Tidak dapat menghapus aktivitas dari kategori asal, aktivitas gagal dipindahkan', status= False)
            )
        
        move_activities_from_destination_category= mongo.db.user_activities.update_one(
            { 'user_id': ObjectId(get_jwt_identity()), 'activity_categories._id': to_category_id },
            {  
                '$push': { 
                    'activity_categories.$.activities': {
                        '$each': activities
                    } 
                } 
            }
        )

        if move_activities_from_destination_category.modified_count == 0:
            return MoveActivitiesIntoCategory(
                moved_activities= [],
                response= ResponseMessage(text= 'Terjadi kendala pada server, aktivitas gagal dipindahkan', status= False)
            )

        return MoveActivitiesIntoCategory(
            moved_activities= activities,
            response= ResponseMessage(text= 'Berhasil memindahkan aktivitas ke dalam kategori lain', status= True)
        )

#Activity Category
class CreateActivityCategory(graphene.Mutation):
    class Arguments:
        fields= ActivityCategoryInput()

    created_activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, fields):
        is_user_activities_exist= mongo.db.user_activities.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if is_user_activities_exist is None:
            create_user_activities= mongo.db.user_activities.insert_one({
                '_id': get_sequence('user_activities'),
                'user_id': ObjectId(get_jwt_identity()),
                'activity_categories': [
                    {
                        '_id': get_sequence_in_array('user_activities', ObjectId(get_jwt_identity()), 'activity_categories'),
                        'category': fields.category,
                        'activities': []
                    }
                ]
            })

            if create_user_activities.inserted_id is None:
                return CreateActivityCategory(
                    created_activity_category= None,
                    response= ResponseMessage(text= 'Tidak dapat membuat user_activities baru, kategori aktivitas gagal ditambahkan', status= False)
                ) 
        else:
            activities= []
            
            if 'activities' in fields and len(fields.activities) > 0:
                is_activity_ids_exist= mongo.db.user_activities.find_one(
                    { 'user_id': ObjectId(get_jwt_identity()) },
                    { 
                        'activity_categories': {
                            '$elemMatch': {
                                'category': None,
                                'activities._id': {
                                    '$all': fields.activities
                                }
                            }
                        }
                    }
                )

                if 'activity_categories' not in is_activity_ids_exist:
                    return CreateActivityCategory(
                        created_activity_category= None,
                        response= ResponseMessage(text= 'Id aktivitas tidak ditemukan, kategori aktivitas gagal ditambahkan', status= False)
                    )
                
                remove_activities_from_none_category= mongo.db.user_activities.update_one(
                    { 'user_id': ObjectId(get_jwt_identity()), 'activity_categories.category': None },
                    { 
                        '$pull': {
                            'activity_categories.$.activities': {
                                '_id': {
                                    '$in': fields.activities
                                }
                            }
                        } 
                    }
                ) 

                if remove_activities_from_none_category.modified_count == 0:
                    return CreateActivityCategory(
                        created_activity_category= None,
                        response= ResponseMessage(text= 'Tidak dapat menghapus aktivitas dari kategori "None", kategori aktivitas gagal ditambahkan', status= False)
                    ) 

                activities= [activity for activity in is_activity_ids_exist['activity_categories'][0]['activities'] if activity['_id'] in fields.activities]

            insert_on_user_activities= mongo.db.user_activities.update_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                { 
                    '$push': {
                        'activity_categories': {
                            '_id': get_sequence_in_array('user_activities', ObjectId(get_jwt_identity()), 'activity_categories'),
                            'category': fields.category,
                            'activities': activities
                        }
                    }
                }
            )

            if insert_on_user_activities.modified_count == 0:
                return CreateActivityCategory(
                    created_activity_category= None,
                    response= ResponseMessage(text= 'Tidak dapat menyimpan pada user_activities collection, kategori aktivitas gagal ditambahkan', status= False)
                ) 

        created_activity_category= mongo.db.user_activities.aggregate([
            {
                '$match': {
                    'user_id': ObjectId(get_jwt_identity())
                }
            },
            {
                '$addFields': {
                    'last_inserted': {
                        '$last': '$activity_categories'
                    }
                }
            },
            {
                '$project': {
                    'last_inserted': 1
                }
            }
        ])

        return CreateActivityCategory(
            created_activity_category= list(created_activity_category)[0]['last_inserted'],
            response= ResponseMessage(text= 'Berhasil menambahkan kategori aktivitas baru', status= True)
        )

class UpdateActivityCategory(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        fields= ActivityCategoryInput()

    updated_activity_category= graphene.Field(ActivityCategory)
    response= graphene.Field(ResponseMessage)
    
    @mutation_header_jwt_required
    def mutate(self, info, _id, fields):
        update_query= {}
        
        is_category_id_exist= mongo.db.user_activities.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'activity_categories._id': _id
        })

        if is_category_id_exist is None:
            return UpdateActivityCategory(
                updated_activity_category= None,
                response= ResponseMessage(text= 'Id kategori aktivitas tidak ditemukan, kategori aktivitas gagal diperbarui', status= False)
            ) 

        if 'category' in fields: 
            update_query['activity_categories.$.category']= fields.category

        result= mongo.db.user_activities.update_one(
            { 'user_id': ObjectId(get_jwt_identity()), 'activity_categories._id': _id },
            { '$set': update_query }
        )

        if result.modified_count == 0:
            return UpdateActivityCategory(
                updated_activity_category= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, kategori aktivitas gagal diperbarui', status= False)
            )

        updated_activity_category= mongo.db.user_activities.find_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            { 
                'activity_categories': {
                    '$elemMatch': { '_id': _id }
                }
            }
        )

        return UpdateActivityCategory(
            updated_activity_category= updated_activity_category['activity_categories'][0],
            response= ResponseMessage(text= 'Berhasil membarui kategori aktivitas', status= True)
        )

class RemoveActivityCategories(graphene.Mutation):
    class Arguments:
        activity_category_ids= graphene.List(graphene.Int)
        keep_activities= graphene.Boolean()

    removed_activity_categories= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)
    
    @mutation_header_jwt_required
    def mutate(self, info, activity_category_ids, keep_activities):
        is_category_ids_exist= mongo.db.user_activities.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'activity_categories._id': {
                '$all': activity_category_ids
            }
        }) 

        if is_category_ids_exist is None:
            return RemoveActivityCategories(
                removed_activity_categories= [],
                response= ResponseMessage(text= 'Kategori aktivitas tidak ditemukan, kategori aktivitas gagal terhapus', status= False)
            )

        if keep_activities is True:
            activity_categories= mongo.db.user_activities.aggregate([
                {
                    '$match': { 
                        'user_id': ObjectId(get_jwt_identity()) 
                    }
                },
                { '$unwind': '$activity_categories' },
                {
                    '$match': { 
                        'activity_categories._id': {
                            '$all': activity_category_ids
                        }
                    }
                },
                {
                    '$replaceRoot': {
                        'newRoot': '$activity_categories'
                    }
                },
            ])
            activities= []

            for activity_category in list(activity_categories):
                activities+= activity_category['activities']

            move_into_none_category= mongo.db.user_activities.update_one(
                { 'user_id': ObjectId(get_jwt_identity()), 'activity_categories.category': None },
                {  
                    '$push': { 
                        'activity_categories.$.activities': {
                            '$each': activities
                        } 
                    } 
                }
            )

            if move_into_none_category.modified_count == 0:
                return RemoveActivityCategories(
                    removed_activity_categories= [],
                    response= ResponseMessage(text= 'Terjadi kendala pada server, aktivitas gagal dipindahkan ke "None" kategori', status= False)
                )
        
        result= mongo.db.user_activities.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                '$pull': {
                    'activity_categories': {
                        '_id': {
                            '$in': activity_category_ids
                        }
                    }
                }
            }
        )
        
        if result.modified_count == 0:
            return RemoveActivityCategories(
                removed_activity_categories= [],
                response= ResponseMessage(text= 'Terjadi kendala padas server, kategori aktivitas gagal terhapus', status= False)
            )

        return RemoveActivityCategories(
            removed_activity_categories= activity_category_ids,
            response= ResponseMessage(text= 'Kategori aktivitas berhasil terhapus', status= True)
        )

class ReorderActivityCategory(graphene.Mutation):
    class Arguments:
        category_ids= graphene.List(graphene.Int)
    
    reordered_activity_categories= graphene.List(ActivityCategory)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, category_ids):
        activity_categories= mongo.db.user_activities.find_one({ 'user_id': ObjectId(get_jwt_identity()) })['activity_categories']

        if len(category_ids) == 0 or len(category_ids) > len(activity_categories) or len(category_ids) < len(activity_categories):
            return ReorderActivityCategory(
                reordered_activity_categories= activity_categories,
                response= ResponseMessage(text= 'Ukuran indeks kategori aktivitas tidak sesuai, kategori aktivitas gagal terubah', status= False)
            ) 

        reordered_activity_categories= []

        for _id in category_ids:
            for activity_category in activity_categories:
                if activity_category['_id'] == _id:
                    reordered_activity_categories.append(activity_category)

        result= mongo.db.user_activities.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {  '$set': { 'activity_categories': reordered_activity_categories } }
        )

        if result.modified_count == 0:
            return ReorderActivityCategory(
                reordered_activity_categories= activity_categories,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, urutan kategori aktivitas gagal terubah', status= False)
            ) 

        return ReorderActivityCategory(
            reordered_activity_categories= reordered_activity_categories,
            response= ResponseMessage(text= 'Berhasil merubah urutan kategori aktivitas', status= True)
        )

class ActivityMutation(graphene.AbstractType):
    #User handle activity
    create_activity= CreateActivity.Field()
    update_activity= UpdateActivity.Field()
    remove_activities= RemoveActivities.Field()
    move_activities_into_category= MoveActivitiesIntoCategory.Field()
    
    #User handle activity category
    create_activity_category= CreateActivityCategory.Field()
    update_activity_category= UpdateActivityCategory.Field()
    remove_activity_categories= RemoveActivityCategories.Field()
    reorderActivityCategory= ReorderActivityCategory.Field()