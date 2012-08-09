import datetime
from django.utils.timezone import utc

def parse_dt(s):
    if not s.endswith('Z'):
        s += 'Z' # Zulu time - UTC
    d = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    return d.replace(tzinfo=utc)
