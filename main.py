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

    def add(self, name: str = typer.Argument(...), due: Optional[str] = None, priority: int = 4,
            description: str = '', project: Optional[str] = None):
        project_id = None
        priority_value = Priority(priority).value

        if project:
            projects = self.client.get_projects()
            matched_projects = list(filter(lambda x: project in x.name, projects))
            if len(matched_projects) == 0:
                project_id = self.client.add_project(project).id
                print(f'Project "{project}" created.')
            elif len(matched_projects) == 1:
                project_id = matched_projects[0].id
            else:
                print("Multiple projects found. Please select one.")
                table = PrettyTable(['Sr. No.', 'Name'])
                sr_no = 0
                for project in matched_projects:
                    name = project.name
                    table.add_row([sr_no, name])
                    sr_no += 1
                print(table)
                choice = int(input("Enter your choice: "))
                project_id = matched_projects[choice].id

        self.client.add_task(name, priority=priority_value, project_id=project_id, due_string=due, due_lang="en",
                             description=description)

    def add_new_project(self, name: str):
        return self.client.add_project(name).id

    def done(self, name: str):
        tasks = self.client.get_tasks()
        projects = self.client.get_projects()
        matched_tasks = list(filter(lambda x: name in x.content, tasks))
        if len(matched_tasks) == 0:
            print("No matching task.")
        elif len(matched_tasks) == 1:
            task = matched_tasks[0]
            self.client.close_task(task.id)
            print(f'"{task.content}" completed.')
        else:
            print("Multiple tasks found. Please select one.")
            table = PrettyTable(['Sr. No.', 'Name', 'Priority', 'Due Date', 'Project', 'Description'])
            sr_no = 0
            for task in matched_tasks:
                name = task.content
                priority = Priority(1).name
                due_date = task.due.string if task.due else ""
                project = list(filter(lambda x: x.id == task.project_id, projects))[0].name
                description = task.description
                table.add_row([sr_no, name, priority, due_date, project, description])
                sr_no += 1
            print(table)
            choice = int(input("Enter your choice: "))
            self.client.close_task(matched_tasks[choice].id)
            print(f'"{matched_tasks[choice].content}" completed.')

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
                tree[task.project_id]['tasks'].append(task)
            else:
                tree[task.project_id] = {}
                tree[task.project_id]['name'] = list(filter(lambda x: x.id == task.project_id, projects))[0].name
                tree[task.project_id]['tasks'] = [task]

        table = PrettyTable(['Sr. No.', 'Name', 'Priority', 'Due Date', 'Project', 'Description'])
        for project_id, project in tree.items():
            sr_no = 0
            for task in project['tasks']:
                name = task.content
                priority = Priority(task.priority).name
                due_date = task.due.string if task.due else ""
                project_name = project['name']
                description = task.description
                table.add_row([sr_no, name, priority, due_date, project_name, description])
                sr_no += 1
        pprint(table)


todoist = Todoist()
app.command()(set_token)
app.command()(todoist.add)
app.command(name='add-project')(todoist.add_new_project)
app.command()(todoist.done)
app.command()(todoist.find)
app.command()(todoist.find_project)
app.command(name='list')(todoist.list_all)

if __name__ == '__main__':
    app()
