import os.path


def resolve_path(path):
    project_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(project_dir, path)
    return full_path
