from django.conf import settings
import redis

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, password=settings.REDIS_PASSWORD)


def check_email_spam(email):
    if r.get(email):
        return 0
    else:
        r.set(email, 'spam', ex=180)
        return 1
