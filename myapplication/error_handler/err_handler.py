from flask import Blueprint, current_app, json, request
from werkzeug.exceptions import HTTPException
from datetime import datetime


def error_handler(e):
    time = datetime.now()
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    dictionary = {'errors': [{'timestamp': str(time), 'status': int(e.code), 'description': str(e.description),
                              "name": str(e.name), "method": request.method, "path": request.full_path,
                              "args": request.args, "host": request.host_url, "url": request.url}]}
    api_body = json.dumps(dictionary, indent=4, sort_keys=True)
    response = e.get_response()
    response.data = api_body
    response.content_type = "application/json"
    response.code = e.code
    response.content_language = "en"
    return response
