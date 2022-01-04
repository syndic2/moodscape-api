from flask import Blueprint, request, jsonify

from extensions import mongo
from utilities.helpers import object_id_to_string_in_list

mental_disorder_api = Blueprint('mental_disorder_api', __name__)

@mental_disorder_api.route('/', methods=['GET'])
def get_mental_disorders():
    name = ""

    if request.args.get('name'):
        name = request.args.get('name')

    mental_disorders = list(
        mongo.db.mental_disorders.find({ 'name': { '$regex': name, '$options': 'i' } })
    )

    return jsonify(mental_disorders=object_id_to_string_in_list(mental_disorders))

@mental_disorder_api.route('/list', methods=['GET'])
def get_mental_disorders_list():
    mental_disorders = list(mongo.db.mental_disorders.find({}, { 'name': 1 }))

    return jsonify(mental_disorders=object_id_to_string_in_list(mental_disorders))
