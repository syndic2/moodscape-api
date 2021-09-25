import os, datetime
from extensions import mongo

upload_path= os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads')

def formatted_file_name(file_name):
    splits= file_name.split('.')
    
    return f"{splits[0]}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{splits[1]}"

def datetime_format(type= 'datetime'):
    if type == 'datetime':
        return '%Y-%m-%d %H:%M'
    elif type == 'date':
        return '%Y-%m-%d'
    elif type == 'time':
        return '%H:%M'

def validate_datetime(text, type= 'datetime'):
    try:
        datetime.datetime.strptime(text, datetime_format(type))
        return True
    except:
        return False

def lesser_comparison_datetime(text_a, text_b, type= 'datetime'):
    try:
        if datetime.datetime.strptime(text_a, datetime_format(type)) < datetime.datetime.strptime(text_b, datetime_format(type)):
            return True
        else:
            return False
    except:
        return False

def get_sequence(collection):
    is_collection_exist_query= { '_id': collection }
    document= mongo.db.sequences.find_one(is_collection_exist_query)

    if document is None:
        mongo.db.sequences.insert_one({ '_id': collection, 'value': 0 })

    document= mongo.db.sequences.find_one_and_update(is_collection_exist_query, { '$inc': { 'value': 1 } }, return_document= True)

    return document['value']

def get_sequence_in_array(collection, document_id, array_documents):
    is_document_exist_query= { 'collection': collection, 'document_id': document_id, 'array_documents': array_documents }
    document= mongo.db.array_sequences.find_one(is_document_exist_query)
    
    if document is None:
        mongo.db.array_sequences.insert_one({
            '_id': get_sequence('array_sequences'),
            'collection': collection,
            'document_id': document_id, 
            'array_documents': array_documents,
            'value': 0
        })

    document= mongo.db.array_sequences.find_one_and_update(is_document_exist_query, { '$inc': { 'value': 1 } }, return_document= True)

    return document['value']