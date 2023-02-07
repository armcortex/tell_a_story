from utils import start_process
from story import run_gen_story


if __name__ == '__main__':
    p = start_process(run_gen_story)
    p.join()
