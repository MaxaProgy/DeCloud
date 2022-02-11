import os


def get_path(dirs, file):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *dirs, file)