import os
import sys
import logging
import datetime
import yaml
import pickle
import time
from multiprocessing import Process
# from functools import wraps



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s Proc: %(process)s  %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


if sys.platform == 'linux' or sys.platform == 'linux2':
    DOWNLOAD_BASE_PATH = './download/'
elif sys.platform == 'darwin':
    DOWNLOAD_BASE_PATH = '/Users/mcs51/code_storge/tell_a_story/download/'
else:
    raise ValueError('Only support linux and macOS')


# def restart_process_dec(story_fn, write_msg_task, failed_msg: str):
#     def wrap(func):
#         @wraps(func)
#         def wrapped_f(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 logging.error(f'{"=" * 20}  {func.__qualname__}() error Begin {"=" * 20}')
#                 logging.error(f'{failed_msg}, error message: {e}')
#                 logging.error(f'Process restart')
#                 logging.error(f'{"=" * 20}  {func.__qualname__}() error End {"=" * 20}')
#                 write_msg_task(f'{"*" * 5} {func.__qualname__}() failed, restarting {"*" * 5}')
#
#                 start_process(story_fn())
#                 time.sleep(1)
#                 os.system(f'kill {os.getpid()}')
#         return wrapped_f
#     return wrap


def start_process(fn, args=()):
    logging.info(f'function: {fn.__qualname__}()')
    p = Process(target=fn, args=args)
    p.start()
    return p


def current_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S_%f")[:-3]


def read_yaml(file_path):
    with open(file_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError(exec)

    return config


def write_yaml(file_path: str, d: dict):
    with open(file_path, 'w') as f:
        yaml.dump(d, f)


def write_pickle(file_path: str, d: dict):
    with open(file_path, 'wb') as f:
        pickle.dump(d, f)


def read_pickle(file_path: str):
    with open(file_path, 'rb') as f:
        x = pickle.load(f)

    return x



