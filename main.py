import json
from enum import IntEnum
from pprint import pprint
from prettytable import PrettyTable

from todoist_api_python.api import TodoistAPI
import typer


class Priority(IntEnum):
    p1 = 4
    p2 = 3
    p3 = 2
    p4 = 1


TEST_API_TOKEN = "d2de1c89ce6061a3ddb0ad2ecfc88670bd6e14c9"
todo = TodoistAPI(TEST_API_TOKEN)
app = typer.Typer()


@app.command()
def add(name: str, time=None, date=None, priority: int = Priority.p4.value, description: str = '',
        project: int = None):
    todo.add_task(name, priority=priority, project=project, due_date_utc=date, due_time_utc=time,
                  description=description)


@app.command()
def done(name: str):
    tasks = todo.get_tasks()
    for task in tasks:
        if task.content == name:
            todo.close_task(task.id)
            break


@app.command()
def find(key: str):
    tasks = todo.get_tasks()
    task_table = PrettyTable(['Sr. No.', 'Name', 'Priority', 'Due Date', 'Project', 'Description'])
    sr_no = 0
    for task in tasks:
        if key in task.content:
            sr_no += 1
            name = task.content
            priority = Priority(1).name
            due_date = task.due.string
            project = todo.get_project(task.project_id).name
            description = task.description
            task_table.add_row([sr_no, name, priority, due_date, project, description])
    print(task_table)


@app.command()
def show_all():
    tree = {}
    for task in todo.get_tasks():
        if task.project_id in tree:
            tree[task.project_id]['tasks'].append(task.content)
        else:
            tree[task.project_id] = {}
            tree[task.project_id]['name'] = todo.get_project(task.project_id).name
            tree[task.project_id]['tasks'] = [task.content]
    # print(json.dumps(tree, indent=4))
    pprint(tree)


if __name__ == '__main__':
    app()
    # todo.add_task("Test", priority=Priority.p2.value)

# def get_tree(todo: TodoistAPI) -> dict:
#     tree = {}
#     for task in todo.get_tasks():
#         if task.project_id in tree:
#             tree[task.project_id].append(task.id)
#         else:
#             tree[task.project_id] = [task.id]
#     return tree
#
#
# # Developer Function
# def get_tree_good(todo: TodoistAPI) -> dict:
#     tree = {}
#     for task in todo.get_tasks():
#         if task.project_id in tree:
#             tree[task.project_id]['tasks'].append((task.id, task.content))
#         else:
#             tree[task.project_id] = {}
#             tree[task.project_id]['name'] = todo.get_project(task.project_id).name
#             tree[task.project_id]['tasks'] = [(task.id, task.content)]
#     return tree
