from flask import request
from flask_limiter import Limiter

def get_real_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr).split(',')[0].strip()

limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["300 per day", "100 per hour"],
    storage_uri="memory://",
)
