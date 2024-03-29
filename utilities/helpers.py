import os, datetime
from extensions import mongo

default_img= 'https://via.placeholder.com/100'
upload_path= os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads')
telegram_sessions_path= os.path.join(os.path.dirname(os.path.abspath(__file__)), '../telegram_sessions')

def is_uploaded_file_exist(file_name, sub_directory= 'images'):
    return os.path.isfile(os.path.join(f"{upload_path}/{sub_directory}", file_name))

def get_month_name(month_number):
    months= [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]

    return months[month_number]

def get_months_between(start_date, end_date):
    """
    Given two instances of ``datetime.date``, generate a list of dates on
    the 1st of every month between the two dates (inclusive).

    e.g. "5 Jan 2020" to "17 May 2020" would generate:

        1 Jan 2020, 1 Feb 2020, 1 Mar 2020, 1 Apr 2020, 1 May 2020

    """
    # if start_date > end_date:
    #     raise ValueError(f"Start date {start_date} is not before end date {end_date}")

    year = start_date.year
    month = start_date.month

    while (year, month) <= (end_date.year, end_date.month):
        yield datetime.date(year, month, 1)

        # Move to the next month.  If we're at the end of the year, wrap around
        # to the start of the next.
        #
        # Example: Nov 2017
        #       -> Dec 2017 (month += 1)
        #       -> Jan 2018 (end of year, month = 1, year += 1)
        #
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

def calculate_age(date_of_birth):
    today= datetime.date.today()
    age= today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    return age

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

def object_id_to_string_in_list(data, key_id= '_id'):
    for i in range(len(data)):
        data[i][key_id]= str(data[i][key_id])

    return data