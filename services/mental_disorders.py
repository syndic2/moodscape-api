from flask import Blueprint, request, jsonify
from itsdangerous import json

from extensions import mongo
from utilities.helpers import object_id_to_string_in_list

mental_disorder_api = Blueprint('mental_disorder_api', __name__)

@mental_disorder_api.route('/', methods= ['GET'])
def get_mental_disorders():
    name = ""

    if request.args.get('name'):
        name = request.args.get('name')

    mental_disorders = list(
        mongo.db.mental_disorders.find({ 'name': { '$regex': name, '$options': 'i' } })
    )

    return jsonify(status= True, mental_disorders=object_id_to_string_in_list(mental_disorders))

@mental_disorder_api.route('/list', methods= ['GET'])
def get_mental_disorders_list():
    mental_disorders = list(mongo.db.mental_disorders.find({}, { 'name': 1 }))
    
    return jsonify(status= True, mental_disorders=object_id_to_string_in_list(mental_disorders))

@mental_disorder_api.route('/by-name/<mental_disorder_name>', methods= ['GET'])
def get_mental_disorder(mental_disorder_name):
    mental_disorder= mongo.db.mental_disorders.find_one({ 'name': mental_disorder_name.title() })

    if mental_disorder is None:
        return jsonify(status= False, message= 'Data gangguan mental tidak ditemukan'), 404

    mental_disorder['_id']= str(mental_disorder['_id'])

    return jsonify(status= True, mental_disorder= mental_disorder)