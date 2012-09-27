from celery.task import Task

import requests

class StracksFlushTask(Task):
    def run(self, url, data):
        requests.post(url + "/", data=data)

