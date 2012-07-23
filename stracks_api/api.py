import datetime

class Connector(object):
    """
        Responsible for connecting to the Stracks service.
    """

class HTTPConnector(Connector):
    pass

class RedisConnector(Connector):
    pass

class API(object):
    def __init__(self, connector):
        self.connector = connector

    def session(self):
        return Session(self)

class Session(object):
    def __init__(self, api):
        self.api = api

    def request(self, ip, useragent, path):
        return Request(self)

    def end(self):
        """ session ends, send data to connector """
        ## do we need this explicitly?
        pass

class Entity(object):
    ## allow option to implicitly create
    def __init__(self, id):
        self.entityid = id

    def __call__(self, clientid):
        return (self.entityid, clientid)

class Request(object):
    def __init__(self, session, ip, useragent, path):
        self.session = session
        self.ip = ip
        self.useragent = useragent
        self.path = path
        time = datetime.datetime.utcnow()
        self.data = dict(ts=time,
                         ip=self.ip,
                         useragent=self.useragent,
                         entries=[])

    def log(self, msg, entities=None, tags=None, action=None):
        ## perform some validation on msg and entities
        time = datetime.datetime.utcnow()
        self.data.entries.append(
            dict(msg=msg,
                 entities=entities,
                 tags=tags,
                 action=action,
                 ts=time)
        )


        # register time
        # setup default IP, useragent, etc entities

        pass

    
