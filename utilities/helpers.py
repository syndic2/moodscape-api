from extensions import mongo

def auto_increment_id(collection):
    _id= 1
    results= mongo.db[collection].find({}).sort('_id', -1).limit(1)

    if results.count() > 0:
        _id= results[0]['_id']+1
    
    return _id  

def auto_increment_id_in_array(collection, array_field):
    _id= 0
    results= mongo.db[collection].aggregate([
        { '$unwind': '$activities' },
        {
            '$group': {
                '_id': '$category',
                'max_activity_id': {
                    '$max': '$activities._id'
                }
            }
        },
        { '$sort': { 'max_activity_id': -1 } },
        { '$limit': 1 }
    ])
    results= list(results) #Must turn into List, unless can't access props

    if len(results) > 0:
        _id= results[0]['max_activity_id']+1 

    return _id