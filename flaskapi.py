from urllib import response
from flask import Flask, json, request, jsonify
import json as pjson
from pathlib import Path
import os

companies = [{"id": 1, "name": "Company One"},
             {"id": 2, "name": "Company Two"}]

recording_cache = {}

this_dir = os.path.dirname(os.path.realpath(__file__))
storage_dir = os.path.join(this_dir, 'storage')
print(f'Dir: {storage_dir}')
if not os.path.exists(storage_dir):
    os.mkdir(storage_dir)
    print('Storage dir created')

api = Flask(__name__)

def has_cache(video_id):
    return video_id in recording_cache

def has_storage(video_id):
    return os.path.exists(os.path.join(storage_dir, f'{video_id}.json'))

def get_storage_path(video_id):
    return os.path.join(storage_dir, f'{video_id}.json')

def has_recording(video_id):
    return has_cache(video_id) or has_storage(video_id)

def cors_response(**kwargs):
    if 'msg' not in kwargs:
        kwargs['msg'] = 'Message'
    response = jsonify([kwargs])
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

@api.route('/companies', methods=['GET'])
def get_companies():
    return json.dumps(companies)

@api.route('/start', methods=['GET'])
def start_record():
    if request.args.get('v'):
        video_id = request.args.get('v')
        if not has_cache(video_id):
            recording_cache[video_id] = []
        if has_storage(video_id):
            with open(get_storage_path(video_id), 'r') as file:
                recording_cache[video_id] = pjson.loads(file.read())
    return cors_response()

@api.route('/stop', methods=['GET'])
def stop_record():
    if request.args.get('v'):
        video_id = request.args.get('v')
        if has_cache(video_id):
            with open(get_storage_path(video_id), 'w') as file:
                file.write(pjson.dumps(recording_cache[video_id], indent='  '))
        recording_cache[video_id] = []
    return cors_response()

@api.route('/print', methods=['POST', 'OPTIONS'])
def print_stuff():
    if request.method == 'POST':
        data = json.loads(request.data)
        video_id = data['videoId']
        storage_path = get_storage_path(video_id)
        if not has_cache(video_id):
            recording_cache[video_id] = []
        if not has_recording(video_id):
            Path(storage_path).touch()
        recording_cache[video_id].append({'rawhtml': data['rawhtml']})
    return cors_response()

if __name__ == '__main__':
    api.run()
