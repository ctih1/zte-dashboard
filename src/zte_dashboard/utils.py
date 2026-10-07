from functools import wraps


class OnCooldownException(Exception): ...


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
