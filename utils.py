from functools import wraps


def get(read_schema):
    """
    Method decorator for GET CRUD RPC entrypoints
    :param read_schema:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            resource = func(self, *args, **kwargs)

            return read_schema().dump(resource).data

        return wrapper

    return decorator


delete = get
""" Method decorator for DELETE CRUD RPC entrypoints
"""
