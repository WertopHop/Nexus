import sys
import os

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_user_data_dir():
    if sys.platform == 'win32':
        app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        data_dir = os.path.join(app_data, 'Nexus')
    else:
        data_dir = os.path.join(os.path.expanduser('~'), '.nexus')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir