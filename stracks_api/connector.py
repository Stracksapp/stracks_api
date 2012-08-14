"""
    Clientside API
"""

import datetime
import requests
import json

class ConnectorException(Exception):
    pass

class MissingAction(ConnectorException):
    pass

class UnknownAction(ConnectorException):
    pass

class NotImplementedAction(ConnectorException):
    pass

class MissingArgument(ConnectorException):
    pass

class Connector(object):
    """
        Responsible for connecting to the Stracks service.
    """
    def session_start(self, sessionid):
        raise NotImplementedAction("session_start")

    def session_end(self, sessionid):
        raise NotImplementedAction("session_end")

    def request(self, sessionid, requestdata):
        raise NotImplementedAction("request")

    def send(self, data):
        """
            Do we need the send() intermediate call?
            Why not just invoke the relevant methods directly?
        """
        action = data.get('action')
        if action is None:
            raise MissingAction()

        try:
            if action == 'session_start':
                self.session_start(data['sessionid'])
            elif action == 'session_end':
                self.session_end(data['sessionid'])
            elif action == 'request':
                self.request(data['sessionid'], data['data'])
            else:
                raise UnknownAction(action)
        except KeyError, e:
            raise MissingArgument(e.message)


class HTTPConnector(Connector):
    """
        Connect to the API synchronously through HTTP
    """
    def __init__(self, url):
        """
            A HTTP connector takes the url of the API / AppInstance as
            argument
        """
        self.url = url
        self.queue = []

    def session_start(self, sessionid):
        data = {}
        data['started'] = datetime.datetime.utcnow().isoformat()
        data['sessionid'] = sessionid
        self.queue.append({'action':'start', 'data':data})
        self.flush()

    def session_end(self, sessionid):
        data = {}
        data['ended'] = datetime.datetime.utcnow().isoformat()
        data['sessionid'] = sessionid
        self.queue.append({'action':'end', 'data':data})
        self.flush()

    def request(self, sessionid, requestdata):
        data = {}
        data['sessionid'] = sessionid
        data['requestdata'] = requestdata
        self.queue.append({'action':'request', 'data':data})
        self.flush()

    def flush(self):
        print "BAAP"
        if self.queue:
            requests.post(self.url + "/", data=json.dumps(self.queue))
            self.queue = []

import threading
import Queue
import atexit

class ASyncHTTPConnector(HTTPConnector):
    thread = None

    def __init__(self, url):
        super(ASyncHTTPConnector, self).__init__(url)
        self.thread = None
        self.lock = threading.Lock()
        self.thread_queue = Queue.Queue()
        self.running = False

    def loop(self):
        self.running = True
        while self.running:
            print "Loop"
            item = self.thread_queue.get()
            ## https://github.com/kennethreitz/grequests ?
            ## catch exceptions, retry later
            requests.post(self.url + "/", data=json.dumps(item))
            print "Post", json.dumps(item)
        print "Thread ends"

    def stop(self):
        self.lock.acquire()
        try:
            print "Stopping thread"
            if self.thread is not None:
                self.running = False
                self.thread.join()
                self.thread = None
        finally:
            self.lock.release()

    def flush(self):
        """ flush queue to thread """
        print "Flushing", self.queue
        if self.queue:
            if self.thread is None:
                self.lock.acquire()
                try:
                    self.thread = threading.Thread(target=self.loop)
                    self.thread.setDaemon(True)
                    print "Starting thread"
                    self.thread.start()
                    print "Thread started"
                finally:
                    self.lock.release()
                    atexit.register(self.stop)

            self.thread_queue.put_nowait(self.queue)
            self.queue = []

class RedisConnector(Connector):
    """
        A connector that simply stores data in redis (or any other keystore?),
        where a separate task is responsible for sending the data to the
        Stracks API
    """
