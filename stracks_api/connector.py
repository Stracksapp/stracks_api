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
    def __init__(self, url, debug=False):
        """
            A HTTP connector takes the url of the API / AppInstance as
            argument
        """
        self.url = url
        self.queue = []
        self._debug = debug

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
        if self.queue:
            requests.post(self.url + "/", data=json.dumps(self.queue))
            self.queue = []

import threading
import Queue
import atexit

import logging

logger = logging.getLogger("stracks")

class ASyncHTTPConnector(HTTPConnector):
    thread = None
    terminate = object()

    TIMEOUT = 10 # seconds

    def __init__(self, url, debug=False):
        super(ASyncHTTPConnector, self).__init__(url, debug)
        self.thread = None
        self.lock = threading.Lock()
        self.thread_queue = Queue.Queue()
        self.backlog = []

    def debug(self, s):
        if self._debug:
            print s

    def loop(self):
        while True:
            self.debug("Loop")
            try:
                item = self.thread_queue.get(timeout=10)
                self.backlog.append(item)
            except Queue.Empty:
                self.debug("Queue 10 sec timeout")

            self.debug("Queue size: %d, backlog size: %d" % (self.thread_queue.qsize(), len(self.backlog)))

            ##
            ## flush entire backlog if possible. May be just one item
            ## (or none at all if queue.get timed out)
            while self.backlog:
                item = self.backlog[0]
                if item is self.terminate:
                    self.debug("Terminating")
                    return  # break out of two loops

                ## https://github.com/kennethreitz/grequests ?

                error = False
                try:
                    requests.post(self.url + "/", data=json.dumps(item),
                                  timeout=self.TIMEOUT)
                    self.backlog.pop()
                except requests.exceptions.Timeout:
                    self.debug("Connection timed out")
                    error = True
                except requests.exceptions.TooManyRedirects:
                    self.debug("Too many redirects")
                    error = True
                except requests.exceptions.URLRequired:
                    self.debug("Not a valid URL")
                    error = True
                except requests.exceptions.SSLError:
                    self.debug("SSL Error")
                    error = True
                except requests.exceptions.ConnectionError:
                    self.debug("Connection error")
                    error = True
                except requests.exceptions.HTTPError:
                    self.debug("HTTP error")
                    error = True
                except requests.exceptions.RequestException:
                    self.debug("Request exception")
                    error = True
                except Exception, e:
                    self.debug("Unknown exception: " + str(e))
                    error = True
                if error:
                    ## increase the delay, but not infinitely
                    # delay = 10 * min(5, tries)
                    ## log error so we can report it eventually
                    self.debug("Delaying")
                    break

                self.debug("Post" + json.dumps(item))

    def stop(self):
        self.lock.acquire()
        try:
            self.debug("Stopping thread")
            if self.thread is not None:
                self.thread_queue.put_nowait(self.terminate)
                self.thread.join()
                self.thread = None
        finally:
            self.lock.release()
        self.debug("Thread stopped")

    def flush(self):
        """ flush queue to thread """
        self.debug("Flushing " + str(self.queue))
        if self.queue:
            if self.thread is None:
                self.lock.acquire()
                try:
                    self.thread = threading.Thread(target=self.loop)
                    self.thread.setDaemon(True)
                    self.debug("Starting thread")
                    self.thread.start()
                    self.debug("Thread started")
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
