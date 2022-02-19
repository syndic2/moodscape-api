from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId

import datetime

from extensions import mongo
from utilities.helpers import datetime_format, validate_datetime

brief_cope_evaluation_api= Blueprint('brief_cope_evaluation_api', __name__)

@brief_cope_evaluation_api.route('/<user_id>', methods= ['GET'])
def get_user_brief_cope_results(user_id):
    start_date= request.args.get('start_date')
    end_date= request.args.get('end_date')

    if validate_datetime(start_date, 'date') is False or validate_datetime(end_date, 'date') is False:
        return jsonify(status= False, message= 'Format tanggal tidak valid'), 400

    if ObjectId.is_valid(user_id) is True:
        user_id= ObjectId(user_id)

    brief_cope_results= list(mongo.db.brief_cope_results.find({ 
        'user_id': user_id,
        'created_at': { 
            '$gte': datetime.datetime.strptime(start_date, datetime_format('date')), 
            '$lte': datetime.datetime.strptime(end_date, datetime_format('date')) 
        }
    }).sort('created_at'))

    for result in brief_cope_results:
        result['_id']= str(result['_id'])

        if ObjectId.is_valid(result['user_id']) is True:
            result['user_id']= str(result['user_id'])

        result['created_at']= {
            'date': str(result['created_at'].date())
        }

    return jsonify(status= True, brief_cope_results= brief_cope_results)

@brief_cope_evaluation_api.route('/save', methods= ['POST'])
def save_brief_cope_result():
    data= request.get_json()
    data['created_at']= datetime.datetime.strptime(str(datetime.datetime.now().date()), datetime_format('date'))

    if ObjectId.is_valid(data['user_id']) is True:
        data['user_id']= ObjectId(data['user_id'])
    else:
        data['user_id']= str(data['user_id'])

    result= mongo.db.brief_cope_results.insert_one(data)

    if result.inserted_id is None:
        return jsonify(status= False, message= 'Terjadi kesalahan pada server, gagal menyimpna hasil evaluasi Brief-COPE'), 500

    return jsonify(status= True, message= 'Berhasil menyimpan hasil evaluasi Brief-COPE')