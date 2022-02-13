import os


def get_path(dirs, file=None):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), *dirs)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, file)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('')
    return path