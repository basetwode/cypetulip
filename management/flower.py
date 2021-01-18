import ast
import json

import requests

# from django.conf import settings
from django.conf import settings

TASKS_PATH = 'api/tasks'
TASKS_INFO_PATH = 'api/task/info/'
TASKS_EXEC_PATH = 'api/task/send-task/'
TASKS_ABORT_PATH = 'api/task/abort/'


class Task:
    args = None
    children = None
    client = None
    clock = None
    eta = None
    exception = None
    exchange = None
    expires = None
    failed = None
    kwargs = None
    name = None
    parent = None
    parent_id = None
    received = None
    rejected = None
    result = None
    retried = None
    retries = None
    revoked = None
    root = None
    root_id = None
    routing_key = None
    runtime = None
    sent = None
    started = None
    state = None
    succeeded = None
    timestamp = None
    traceback = None
    uuid = None
    worker = None

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def to_dict(self):
        return self.__dict__

    def get_args(self):
        return ast.literal_eval("[" + self.args[1:-1] + "]")


class FlowerView:
    server_uri = ''

    def __init__(self, uri=None):  # =settings.FLOWER_URL
        self.server_uri =  settings.FLOWER_URL

    def get_tasks(self, page=0, num_items=20):
        offset = num_items*page
        resp = requests.get(settings.FLOWER_URL + TASKS_PATH+"?offset="+str(offset)+"&limit="+str(num_items))
        if 200 <= resp.status_code < 400:
            return [Task(**v) for k, v in json.loads(resp.content).items()]
        else:
            return {'error': 'Unable to retrieve tasks'}

    def get_task_info(self, uuid):
        resp = requests.get(self.server_uri + TASKS_INFO_PATH + uuid)
        if 200 <= resp.status_code < 400:
            return Task(**json.loads(resp.content))
        else:
            return {'error': 'Unable to retrieve task'}

    def restart_task(self, uuid):
        task = self.get_task_info(uuid)
        resp = requests.post(self.server_uri + TASKS_EXEC_PATH + task.name,
                             json={"args": task.get_args() or [] if len(task.get_args()) == 0 else task.get_args()})
        return 200 <= resp.status_code < 400


# flower = FlowerView(uri='http://localhost:8888/')
# tasks = flower.get_tasks()
# task_info = flower.get_task_info('16af9b6b-edb8-47fd-a307-3d3a2e92ae35')
# rest_task = flower.restart_task('16af9b6b-edb8-47fd-a307-3d3a2e92ae35')
#
# print(tasks)
# print(task_info)
