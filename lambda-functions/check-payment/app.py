import random

def handler(event, context):
    status = bool(random.getrandbits(1))
    return {"status":status}