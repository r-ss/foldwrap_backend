import redis

from config import config


class RessRedisAbstraction:
    prefix = "fw:"  # added to every key to minimize collisions risk
    expiration = 60 * 60 * 12  # 12 hours

    def __init__(self, host="foldwrap-redis", port=6379, db=0):
        if config.PRODUCTION:
            self.r = redis.Redis(host=host, port=port, db=db, password=config.REDIS_PASSWORD)
        else:
            self.expiration = 60 * 5
            self.r = redis.Redis(host="127.0.0.1", port=port, db=db, password=config.REDIS_PASSWORD)

    def get(self, k):
        if config.TESTING_MODE:
            return "Testing mode, no redis, no get"

        v = self.r.get(f"{self.prefix}{k}")
        if v:
            if v.decode() == "None":
                return None
            return v.decode()
        return None

    def set(self, k, v, exp=None):
        if config.TESTING_MODE:
            return True

        if not exp:
            exp = self.expiration
        self.r.set(f"{self.prefix}{k}", v, ex=exp)
        return True

    def incr(self, k):
        if config.TESTING_MODE:
            return True

        self.r.incr(f"{self.prefix}{k}")
        return True

    def delete(self, k):
        if config.TESTING_MODE:
            return True

        self.r.delete(f"{self.prefix}{k}")
        return True

    def ping(self):
        if config.TESTING_MODE:
            return "Testing mode, no redis, no ping"

        try:
            ping = self.r.ping()
            return ping
        except redis.exceptions.ConnectionError:
            print("Redis ping failed, seems like it is not running")
            return False


"""

REDIS INSTALLATION

https://betterprogramming.pub/getting-started-with-redis-a-python-tutorial-3a18531a73a6



docker pull redis
docker run -d -p 6379:6379 -v /home/ress/redis_data:/data --name redis-server redis

docker exec -it redis-server redis-cli

Run without persistence:
docker run -d -p 6379:6379 --name redis-server redis --requirepass redis2password


USAGE EXAMPLE

from ress_redis import RessRedisAbstraction as redis


r = redis()

r.set('hello', 'worlde') # True

value = r.get('hello')
print(value) # b'world'

r.delete('hello') # True
print(r.get('hello')) # None



CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                                       NAMES
876969d5b15e   redis     "docker-entrypoint.s…"   7 seconds ago   Up 7 seconds   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   redis-server


"""
