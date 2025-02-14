import redis


def connect_redis():
    return redis.StrictRedis(host="localhost", port=6379, db=0)