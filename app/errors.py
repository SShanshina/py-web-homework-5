from typing import Union
from flask import jsonify
from app.settings import app


def get_object_or_404(session, model, *criterion):
    object = session.query(model).filter(*criterion).first()
    if object is None:
        raise HTTPError(404, 'object not found')
    return object


class HTTPError(Exception):

    def __init__(self, status_code: int, message: Union[str, dict, list]):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def handle_errors(error):
    response = jsonify({
        'message': error.message
    })
    response.status_code = error.status_code
    return response
