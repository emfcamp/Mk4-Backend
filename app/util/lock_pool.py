import threading

# fix me: this will leak memory.
shared_dict = {}

def shared_lock(key):
    if key not in shared_dict:
        shared_dict[key] = threading.Lock()
    return shared_dict[key]




