import threading

# fix me: this will leak memory.
shared_dict = {}

def shared_lock(key):
    if key not in shared_dict:
        print("new lock", key)
        shared_dict[key] = threading.Lock()
    return shared_dict[key]




