import os
import logging
from enum import IntEnum
from pprint import pprint
from typing import Optional

import dotenv
import typer
from prettytable import PrettyTable
from todoist_api_python.api import TodoistAPI


class Priority(IntEnum):
    p1 = 4
    p2 = 3
    p3 = 2
    p4 = 1


logger = logging.getLogger(__name__)
app = typer.Typer()


def set_token():
    token = input("Enter your API token: ")
    dotenv.set_key(dotenv.find_dotenv(), 'API_TOKEN', token)
    return token


class Todoist:
    def __init__(self):
        self._client: Optional[TodoistAPI] = None

    @property
    def client(self):
        if self._client is None:
            token = os.getenv('API_TOKEN')
            if not token:
                dotenv.load_dotenv()
                token = os.getenv('API_TOKEN')
            if not token:
                token = set_token()
            self._client = TodoistAPI(token)
        return self._client

    def add(self, name: str, time=None, date=None, priority: int = Priority.p4.value, description: str = '',
            project: int = None):
        self.client.add_task(name, priority=priority, project=project, due_date_utc=date, due_time_utc=time,
                             description=description)

    def done(self, name: str):
        tasks = self.client.get_tasks()
        for task in tasks:
            if task.content == name:
                print(f"{name} completed.")
                self.client.close_task(task.id)
                break

    def find_project(self, key: str):
        projects = self.client.get_projects()
        project_table = PrettyTable(['Sr. No.', 'Name'])
        sr_no = 0
        for project in projects:
            if key in project.name:
                sr_no += 1
                name = project.name
                project_table.add_row([sr_no, name])
        print(project_table)

    def list_all(self):
        tree = {}
        tasks = self.client.get_tasks()
        projects = self.client.get_projects()
        for task in tasks:
            if task.project_id in tree:
                tree[task.project_id]['tasks'].append(task.content)
            else:
                tree[task.project_id] = {}
                tree[task.project_id]['name'] = list(filter(lambda x: x.id == task.project_id, projects))[0].name
                tree[task.project_id]['tasks'] = [task.content]
        pprint(tree)

    def find(self, key: str):
        tasks = self.client.get_tasks()
        task_table = PrettyTable(['Sr. No.', 'Name', 'Priority', 'Due Date', 'Project', 'Description'])
        sr_no = 0
        for task in tasks:
            if key in task.content:
                sr_no += 1
                name = task.content
                priority = Priority(1).name
                due_date = task.due.string if task.due else ""
                project = self.client.get_project(task.project_id).name
                description = task.description
                task_table.add_row([sr_no, name, priority, due_date, project, description])
        print(task_table)


todoist = Todoist()
app.command()(set_token)
app.command()(todoist.add)
app.command()(todoist.done)
app.command()(todoist.find)
app.command()(todoist.find_project)
app.command(name='list')(todoist.list_all)

if __name__ == '__main__':
    app()
