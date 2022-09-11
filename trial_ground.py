from todoist_api_python.api import TodoistAPI


def get_tree(todo: TodoistAPI) -> dict:
    tree = {}
    for task in todo.get_tasks():
        if task.project_id in tree:
            tree[task.project_id].append(task.id)
        else:
            tree[task.project_id] = [task.id]
    return tree


# Developer Function
def get_tree_good(todo: TodoistAPI) -> dict:
    tree = {}
    for task in todo.get_tasks():
        if task.project_id in tree:
            tree[task.project_id]['tasks'].append((task.id, task.content))
        else:
            tree[task.project_id] = {}
            tree[task.project_id]['name'] = todo.get_project(task.project_id).name
            tree[task.project_id]['tasks'] = [(task.id, task.content)]
    return tree
