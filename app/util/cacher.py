from app.util import memcached
import os

def cacher(func, key, mc=memcached.shared):
    def call(parameter):
        call_key = "cacher::" + key + "::" + parameter
        cached_result = mc.get(call_key)
        if cached_result:
            return cached_result
        result = func(parameter)
        mc.set(call_key, result)
        return result

    return call





