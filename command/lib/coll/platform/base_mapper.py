from time import sleep
from django.db import OperationalError


def sync_sqlite(func):
    def func_wrapper(*args, **kwargs):
        done = False
        res = None
        while not done:
            try:
                res = func(*args, **kwargs)
                done = True
            except OperationalError as e:
                sleep(2)
        return res
    return func_wrapper

class BaseMapper:
    pass