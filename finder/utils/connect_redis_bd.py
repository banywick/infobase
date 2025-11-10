import redis


def connect_redis():
    return redis.StrictRedis(host="redis", port=6379, db=0)  # ← Изменили "localhost" на "redis"



