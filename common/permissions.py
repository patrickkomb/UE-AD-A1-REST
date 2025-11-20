from functools import wraps
from flask import request, jsonify, make_response
import requests
from common.env import USERS_SERVICE_URL

def is_admin(userid):
    try:
        user_resp = requests.get(f"{USERS_SERVICE_URL}/{userid}", headers={"X-User-Id": 'admin'})
        if user_resp.status_code == 200:
            user_detail = user_resp.json()
            print(user_detail["is_admin"])
            if user_detail["is_admin"]:
                return True
        else:
            return False
    except Exception as e:
        return False # TODO: Gestion erreur pour renvoyer XYZ service unavailable

def check_access(source_userid, target_userid=None, require_admin=False):
    if not source_userid:
        return make_response(jsonify({"error": "Missing X-User-Id header"}), 401)

    if require_admin and not is_admin(source_userid):
        return make_response(jsonify({"error": "Access forbidden"}), 403)

    if target_userid is not None and source_userid != target_userid and not is_admin(source_userid):
        return make_response(jsonify({"error": "Access forbidden"}), 403)

    return None

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        source_userid = request.headers.get("X-User-Id")
        res = check_access(source_userid, require_admin=True)
        if res:
            return res
        return f(*args, **kwargs)
    return wrapper

def owner_or_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        source_userid = request.headers.get("X-User-Id")
        target_userid = kwargs.get("userid")
        res = check_access(source_userid, target_userid=target_userid)
        if res:
            return res
        return f(*args, **kwargs)
    return wrapper
