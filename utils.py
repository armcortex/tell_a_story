import logging
import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def current_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
