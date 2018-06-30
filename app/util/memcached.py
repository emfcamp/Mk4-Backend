from memcache import Client

shared = Client(['127.0.0.1:11211'], debug=0, cache_cas=True)



