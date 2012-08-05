import datetime

def parse_dt(s):
    if not s.endswith('Z'):
        s += 'Z' # Zulu time - UTC
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
