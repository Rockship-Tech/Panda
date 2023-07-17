import os
import datetime
import jwt

from functools import wraps
from flask import jsonify, request
from functional import seq

from system.exceptions import ApplicationError, make_error, PermissionDenied, SystemException

from model.user import User
from model.model_enum import UserType

def authorized(role_string=None):
    def real_jwt_required(fn):
        @wraps(fn)
        def internal(*args, **kwargs):
            # If this API have role_strings, add to permitted_roles for checking later
            permitted_roles = []
            if role_string:
                for role in role_string:
                    if role == "u":
                        permitted_roles.append("user")
                    else:
                        raise AssertionError(f"An API have a strange role {role}")

            try:
                token = request.headers["Authorization"].split(" ")
                if len(token) != 2 or token[0] != "JWT":
                    raise jwt.InvalidTokenError
                payload = jwt.decode(token[1], os.getenv("SECRET_KEY"), options={'verify_exp': False})
                userrole = payload.get("role")
                if userrole not in UserType.list():
                    raise jwt.InvalidTokenError

                if role_string and userrole not in permitted_roles:
                    raise ApplicationError(
                        "You are not valid user.",
                        code=403,
                        detail={"have": userrole, "want": permitted_roles},
                    )
            except KeyError:
                return jsonify(
                    {"success": False, "message": "Authorization Header must be provide."}
                ), 401
            except jwt.ExpiredSignatureError:
                return jsonify(
                    {"success": False, "message": "Signature expired. Please log in again."}
                ), 401
            except jwt.InvalidTokenError:
                return jsonify(
                    {"success": False, "message": "Invalid token. Please check your token carefully or login again."}
                ), 401
            except ApplicationError as app_err:
                return make_error(app_err.message, detail=app_err.detail, code=403)

            if userrole == "user":
                user = User.query.find_by_id(payload["id"])
                if not user:
                    return jsonify({"success": False, "message": "Authentication Error: User not found."}), 401

                following_category = seq(user.slots) \
                    .map(lambda x: str(x.category_id)) \
                    .to_list()
                request.following_category = []
                request.following_category.extend(following_category)
                request.user = user
            request.user_id = payload["id"]
            request.role = payload["role"]
            return fn(*args, **kwargs)
        return internal
    return real_jwt_required


def encode_access_token(user_id, role) -> str:
    """
    Warn: user_id can be UUID so it need str(user_id)
    """
    if role not in ["staff", "user", "guest"]:
        raise ApplicationError("Role is not valid.")
    payload = {
        "id": str(user_id),
        "iat": datetime.datetime.utcnow(),
        "role": role,
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256").decode()
