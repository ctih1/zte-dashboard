from functools import wraps
from fastapi import Request
import os
import hashlib


class OnCooldownException(Exception): ...


class AuthenticationErrorr(Exception): ...


def check_cooldown(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        target_instance_w_zte = None

        for arg in args:
            if "zte" not in dir(arg):
                continue
            target_instance_w_zte = arg

        if getattr(target_instance_w_zte, "on_cooldown"):
            raise OnCooldownException("On cooldown!")

        a = func(*args, **kwargs)
        return a

    return wrapper


def is_authenticated(request: Request) -> bool:
    target_password_sha256 = request.cookies.get("Token")
    if not target_password_sha256:
        return False

    passwords = os.environ["PASSWORDS"].split(",")

    return any(
        [
            hashlib.sha256(password.encode("UTF-8")).hexdigest()
            == target_password_sha256
            for password in passwords
        ]
    )


def check_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        target: Request | None = None

        if "request" in kwargs:
            target = kwargs["request"]
        else:
            for arg in args:
                if isinstance(arg, Request):
                    continue
                target = arg

        if not target:
            raise AuthenticationErrorr("Failed to find request object")

        if not is_authenticated(target):
            raise AuthenticationErrorr("Invalid login token")

        a = func(*args, **kwargs)
        return a

    return wrapper
