from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId

from os import environ as ENV
import requests, json

from extensions import mongo

fcm_service_api= Blueprint('fcm_api', __name__)

@fcm_service_api.route('/tokens', methods=['GET'])
def get_tokens():
    tokens= list(mongo.db.fcm_tokens.find({}))

    for i in range(len(tokens)):
        tokens[i]['_id']= str(tokens[i]['_id'])
        tokens[i]['user_id']= str(tokens[i]['user_id'])

    return jsonify(tokens= tokens)

@fcm_service_api.route('/save-token', methods=['POST'])
def save_token():
    user_id= request.json['user_id']
    token= request.json['token']

    is_token_exist= mongo.db.fcm_tokens.find_one({ 
        'user_id': ObjectId(user_id),
        'token': token
     })

    if is_token_exist is not None:
        return jsonify(
            token= token,
            message=  'FCM token sudah tersimpan'
        ), 409

    result= mongo.db.fcm_tokens.insert_one({
        'user_id': ObjectId(user_id),
        'token': token
    })

    if result.inserted_id is None:
        return jsonify(
            token= token,
            message= 'Terjadi kesalahan pada server'
        ), 500

    return jsonify(
        token= token,
        message= 'Berhasil menyimpan token notifikasi FCM baru'
    )

@fcm_service_api.route('/remove-token/<token>', methods=['DELETE'])
def remove_token(token):
    is_token_exist= mongo.db.fcm_tokens.find_one({ 'token': token })

    if is_token_exist is None:
        return jsonify(
            token= token,
            message= 'Token tidak ditemukan, gagal menghapus token'
        ), 404

    result= mongo.db.fcm_tokens.delete_many({ 'token': token })

    if result.deleted_count == 0:
        return jsonify(
            token= token,
            message= 'Terjadil kesalahan pada server, gagal menghapus token'
        ), 500

    return jsonify(
        token= token,
        message= 'Berhasil menghapus token'
    )

def send_notification(token, notification, data= {}):
    notify= requests.post(
        url= 'https://fcm.googleapis.com/fcm/send', 
        headers= {
            'Authorization': f"key={ENV.get('FCM_SERVER_KEY')}",
            'Content-Type': 'application/json'
        },
        data= json.dumps({ 'to': token, 'notification': notification, 'data': data })
    )
    response= notify.json()

    return response
