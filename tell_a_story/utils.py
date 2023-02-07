import logging
import datetime
import yaml
import pickle
from multiprocessing import Process


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def start_process(fn):
    p = Process(target=fn)
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



