class Config(object):
    CACHE_TYPE = "redis"
    CACHE_REDIS_HOST = "redis"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_REDIS_URL = "redis://redis:6379/0"
    CACHE_REDIS_PASSWORD = "redis"
    CACHE_DEFAULT_TIMEOUT = 500